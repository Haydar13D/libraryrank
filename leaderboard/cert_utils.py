import os
import io
import logging
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)

FONTS_DIR = os.path.join(os.path.dirname(__file__), 'fonts')


def _get_font(font_name, size):
    """
    Attempts to load a TrueType font from leaderboard/fonts/ or falls back.
    """
    font_path = os.path.join(FONTS_DIR, font_name)
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception as e:
            logger.warning(f"Failed to load font {font_path}: {e}")

    # Fallbacks in leaderboard/fonts
    for alt in ['arialbd.ttf', 'arial.ttf', 'timesbd.ttf', 'calibrib.ttf']:
        alt_path = os.path.join(FONTS_DIR, alt)
        if os.path.exists(alt_path):
            try:
                return ImageFont.truetype(alt_path, size=size)
            except Exception:
                pass

    return ImageFont.load_default()


def _hex_to_rgb(hex_str, default=(30, 41, 59)):
    """Converts a hex color code (#1e293b) to an RGB tuple."""
    if not hex_str:
        return default
    hex_clean = hex_str.strip().lstrip('#')
    if len(hex_clean) == 3:
        hex_clean = ''.join([c * 2 for c in hex_clean])
    if len(hex_clean) == 6:
        try:
            return tuple(int(hex_clean[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            pass
    return default


def generate_certificate_pdf(registration, member_name=None):
    """
    Generates a high-resolution PDF certificate for the given SeminarRegistration.
    Saves the PDF to registration.certificate_pdf and returns the ContentFile / bytes.
    """
    seminar = registration.seminar
    if not seminar.cert_template:
        logger.info(f"Seminar {seminar.id} does not have a cert_template configured.")
        return None

    # Determine participant's display name
    if not member_name:
        from .models import Member
        mem = Member.objects.filter(member_id=registration.member_id).first()
        if mem and mem.name:
            member_name = mem.name.strip()
        else:
            member_name = registration.member_id

    # Open template image
    try:
        template_img = Image.open(seminar.cert_template.path)
        img = template_img.convert('RGB')
    except Exception as e:
        logger.error(f"Error opening cert template for seminar {seminar.id}: {e}")
        return None

    img_w, img_h = img.size
    draw = ImageDraw.Draw(img)

    # 1. Draw Certificate Number (if configured)
    cert_number = registration.certificate_number
    if not cert_number and seminar.cert_number_template:
        try:
            # Count sequence for this seminar
            seq = registration.seminar.registrations.filter(attended_at__isnull=False).count()
            if seq == 0:
                seq = 1
            cert_number = seminar.cert_number_template.format(
                num=seq,
                year=seminar.date.strftime('%Y'),
                month=seminar.date.strftime('%m'),
                day=seminar.date.strftime('%d'),
                nim=registration.member_id
            )
        except Exception:
            cert_number = seminar.cert_number_template

        registration.certificate_number = cert_number

    if cert_number:
        num_font = _get_font('arial.ttf', size=max(18, int(seminar.cert_name_font_size * 0.45)))
        num_y = seminar.cert_number_pos_y
        num_color = (71, 85, 105) # Slate gray
        
        # Calculate horizontal center
        bbox = draw.textbbox((0, 0), cert_number, font=num_font)
        text_w = bbox[2] - bbox[0]
        num_x = int((img_w - text_w) / 2)
        draw.text((num_x, num_y), cert_number, font=num_font, fill=num_color)

    # 2. Draw Participant Name (Centered)
    name_font = _get_font(seminar.cert_font_family, size=seminar.cert_name_font_size)
    name_color = _hex_to_rgb(seminar.cert_name_color, default=(30, 41, 59))
    name_y = seminar.cert_name_pos_y

    bbox_name = draw.textbbox((0, 0), member_name, font=name_font)
    name_w = bbox_name[2] - bbox_name[0]
    name_x = int((img_w - name_w) / 2)
    draw.text((name_x, name_y), member_name, font=name_font, fill=name_color)

    # 3. Draw NIM (Centered beneath Name, if enabled)
    if seminar.cert_show_nim and registration.member_id:
        nim_text = f"NIM / NIDN: {registration.member_id}"
        nim_font = _get_font('arial.ttf', size=max(20, int(seminar.cert_name_font_size * 0.42)))
        nim_color = (100, 116, 139) # #64748b
        nim_y = seminar.cert_nim_pos_y

        bbox_nim = draw.textbbox((0, 0), nim_text, font=nim_font)
        nim_w = bbox_nim[2] - bbox_nim[0]
        nim_x = int((img_w - nim_w) / 2)
        draw.text((nim_x, nim_y), nim_text, font=nim_font, fill=nim_color)

    # 4. Convert Canvas to PDF
    pdf_io = io.BytesIO()
    img.save(pdf_io, format='PDF', resolution=300.0)
    pdf_bytes = pdf_io.getvalue()

    # Save to model
    safe_title = "".join(c for c in seminar.title if c.isalnum() or c in (' ', '_', '-')).strip()[:30]
    filename = f"Sertifikat_{registration.member_id}_{registration.seminar_id}.pdf"
    
    registration.certificate_pdf.save(filename, ContentFile(pdf_bytes), save=True)
    return pdf_bytes


def send_certificate_email(registration, member_name=None):
    """
    Dispatches the email with the generated PDF e-certificate attached.
    """
    if not registration.email:
        logger.warning(f"Cannot send certificate email: Registration {registration.id} has no email.")
        return False

    seminar = registration.seminar
    
    # Ensure certificate PDF is generated
    if not registration.certificate_pdf:
        generate_certificate_pdf(registration, member_name=member_name)

    if not registration.certificate_pdf:
        logger.warning(f"Cannot send email: Failed to generate certificate for {registration.id}")
        return False

    # Standard body requested by user:
    # "Terima kasih telah mengikuti kegiatan {seminar.title}.
    # Berikut kami kirim sertifikat."
    subject = f"Sertifikat Kegiatan: {seminar.title}"
    body = (
        f"Terima kasih telah mengikuti kegiatan {seminar.title}.\n"
        f"Berikut kami kirim sertifikat keikutsertaan Anda.\n\n"
        f"Detail Kegiatan:\n"
        f"- Narasumber: {seminar.speaker}\n"
        f"- Tanggal: {seminar.date.strftime('%d %B %Y')}\n"
        f"- Status: Kehadiran Terverifikasi (+{seminar.points_attend} XP)\n\n"
        f"Salam Hangat,\n"
        f"Perpustakaan Universitas Muhammadiyah Surakarta"
    )

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'library@ums.ac.id')
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[registration.email],
        )

        # Attach PDF
        registration.certificate_pdf.seek(0)
        pdf_content = registration.certificate_pdf.read()
        filename = f"Sertifikat_{registration.member_id}.pdf"
        email.attach(filename, pdf_content, 'application/pdf')

        email.send(fail_silently=False)
        logger.info(f"Certificate email successfully sent to {registration.email} for seminar {seminar.id}")
        return True
    except Exception as e:
        logger.error(f"Error sending certificate email to {registration.email}: {e}")
        return False
