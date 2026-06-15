document.addEventListener("DOMContentLoaded", function () {
    // 1. Inject the Modal HTML and Custom CSS into the body
    const modalHTML = `
        <style>
            .modal-overlay { background-color: rgba(17, 24, 39, 0.5); }
            .modal-content { background-color: #ffffff; color: #111827; }
            .modal-header, .modal-footer { border-color: #e5e7eb; }
            .modal-footer { background-color: #f9fafb; }
            .modal-label { color: #6b7280; }
            .modal-value { color: #111827; }
            .modal-close { color: #9ca3af; }
            .modal-close:hover { color: #6b7280; }
            .modal-cancel-btn { background-color: #ffffff; color: #374151; border-color: #d1d5db; }
            .modal-cancel-btn:hover { background-color: #f3f4f6; }
            
            html.dark .modal-content { background-color: #1f2937; color: #f9fafb; }
            html.dark .modal-header, html.dark .modal-footer { border-color: #374151; }
            html.dark .modal-footer { background-color: #111827; }
            html.dark .modal-label { color: #9ca3af; }
            html.dark .modal-value { color: #f9fafb; }
            html.dark .modal-close { color: #6b7280; }
            html.dark .modal-close:hover { color: #9ca3af; }
            html.dark .modal-cancel-btn { background-color: #374151; color: #e5e7eb; border-color: #4b5563; }
            html.dark .modal-cancel-btn:hover { background-color: #4b5563; }
        </style>
        <div id="custom-detail-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center modal-overlay backdrop-blur-sm transition-opacity">
            <div class="modal-content rounded-lg shadow-xl w-11/12 max-w-md overflow-hidden transform transition-all">
                <div class="px-6 py-4 border-b modal-header flex justify-between items-center">
                    <h3 class="text-lg leading-6 font-medium modal-value" id="modal-title">
                        Detail Klaim Hadiah
                    </h3>
                    <button id="modal-close-btn" class="modal-close focus:outline-none">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
                <div class="px-6 py-4">
                    <div class="mb-4">
                        <p class="text-sm font-semibold modal-label">Kode Klaim</p>
                        <p class="text-base modal-value font-mono" id="modal-code"></p>
                    </div>
                    <div class="mb-4">
                        <p class="text-sm font-semibold modal-label">Member</p>
                        <p class="text-base modal-value" id="modal-member"></p>
                    </div>
                    <div class="mb-4">
                        <p class="text-sm font-semibold modal-label">Hadiah (Reward)</p>
                        <p class="text-base font-bold text-primary-600" id="modal-reward"></p>
                    </div>
                    <div class="mb-4">
                        <p class="text-sm font-semibold modal-label">Waktu Pengajuan</p>
                        <p class="text-base modal-value" id="modal-date"></p>
                    </div>
                </div>
                <div class="px-6 py-3 modal-footer border-t flex justify-end gap-3">
                    <button id="modal-cancel-btn" class="modal-cancel-btn px-4 py-2 border rounded-md shadow-sm text-sm font-medium focus:outline-none">
                        Tutup
                    </button>
                    <a id="modal-edit-btn" href="#" class="px-4 py-2 bg-primary-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-primary-700 focus:outline-none">
                        Edit Data
                    </a>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    const modal = document.getElementById('custom-detail-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const cancelBtn = document.getElementById('modal-cancel-btn');

    function closeModal() {
        modal.classList.add('hidden');
    }

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Close when clicking outside
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // 2. Attach click events to all Detail buttons
    // Since Unfold might load things dynamically or we just attach to document
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.show-detail-modal-btn');
        if (btn) {
            e.preventDefault();
            // Populate data
            document.getElementById('modal-code').textContent = btn.getAttribute('data-code');
            document.getElementById('modal-member').textContent = btn.getAttribute('data-member');
            document.getElementById('modal-reward').textContent = btn.getAttribute('data-reward');
            document.getElementById('modal-date').textContent = btn.getAttribute('data-date');
            document.getElementById('modal-edit-btn').setAttribute('href', btn.getAttribute('data-edit-url'));

            // Show modal
            modal.classList.remove('hidden');
        }
    });
});
