import csv
import io
import time
import json
import logging
from datetime import datetime, date
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db import connections, connection
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)

def superuser_required_view(view_func):
    """Decorator to ensure authenticated superusers / staff members can access this tool."""
    def _wrapped(request, *args, **kwargs):
        is_api = request.path.endswith('/api/') or request.GET.get('action') or request.method == 'POST' or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if not request.user.is_authenticated:
            if is_api:
                return JsonResponse({'success': False, 'error': 'Sesi Anda telah berakhir. Silakan login kembali.'}, status=401)
            raise PermissionDenied("Silakan login terlebih dahulu.")

        if not (request.user.is_superuser or request.user.is_staff):
            if is_api:
                return JsonResponse({'success': False, 'error': 'Akses ditolak: Hanya Superuser atau Staff yang diizinkan.'}, status=403)
            raise PermissionDenied("Hanya Superuser atau Staff yang memiliki izin untuk mengakses Database Explorer.")

        return view_func(request, *args, **kwargs)
    return _wrapped


def json_serializer(obj):
    """Custom JSON serializer for DB values like date, datetime, bytes, etc."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except Exception:
            return f"<BLOB {len(obj)} bytes>"
    return str(obj)


@superuser_required_view
def db_explorer_dashboard(request):
    """Render the main Database Explorer (Lite phpMyAdmin) dashboard."""
    # List available database connections
    available_dbs = []
    for db_name in connections.databases.keys():
        cfg = connections.databases[db_name]
        available_dbs.append({
            'name': db_name,
            'label': f"{db_name.upper()} ({cfg.get('NAME', '')})",
            'engine': cfg.get('ENGINE', '').split('.')[-1],
            'is_default': (db_name == 'default'),
        })

    context = {
        'title': 'Database Explorer (Lite phpMyAdmin)',
        'site_title': 'LibraryRank Admin',
        'site_header': 'LibraryRank Admin',
        'available_dbs': available_dbs,
        'user': request.user,
    }
    return render(request, 'leaderboard/admin/db_explorer.html', context)


@superuser_required_view
def db_explorer_api(request):
    """
    JSON API endpoint for Database Explorer operations:
    - Tables listing & metadata
    - Table structure & schema
    - Table records browsing, search, sort, pagination
    - CRUD: Insert, Update, Delete row
    - Raw SQL runner
    - SQL Dump & CSV Export
    """
    db_name = request.GET.get('db') or request.POST.get('db') or 'default'
    if db_name not in connections.databases:
        return JsonResponse({'success': False, 'error': f"Database '{db_name}' tidak terdaftar."}, status=400)

    action = request.GET.get('action') or request.POST.get('action') or ''
    conn = connections[db_name]

    try:
        # 1. GET ALL TABLES
        if action in ('get_tables', 'list_tables'):
            with conn.cursor() as cursor:
                db_actual_name = conn.settings_dict.get('NAME')
                cursor.execute(
                    """
                    SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH, TABLE_COMMENT, ENGINE
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = %s
                    ORDER BY TABLE_NAME ASC
                    """,
                    [db_actual_name]
                )
                rows = cursor.fetchall()
                tables = []
                total_rows = 0
                total_size_kb = 0
                for r in rows:
                    row_cnt = r[1] or 0
                    data_kb = round(((r[2] or 0) + (r[3] or 0)) / 1024, 1)
                    total_rows += row_cnt
                    total_size_kb += data_kb
                    tables.append({
                        'name': r[0],
                        'rows': row_cnt,
                        'row_count': row_cnt,
                        'size_kb': data_kb,
                        'comment': r[4] or '',
                        'engine': r[5] or '',
                    })
                return JsonResponse({
                    'success': True,
                    'tables': tables,
                    'total_tables': len(tables),
                    'total_rows': total_rows,
                    'total_size_kb': round(total_size_kb, 1),
                    'db_name': db_name
                })

        # 2. GET TABLE SCHEMA / STRUCTURE
        elif action == 'get_table_schema':
            table_name = request.GET.get('table', '').strip()
            if not table_name:
                return JsonResponse({'success': False, 'error': 'Parameter table diperlukan.'}, status=400)

            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = []
                for r in cursor.fetchall():
                    columns.append({
                        'name': r[0],
                        'type': r[1],
                        'null': r[2],
                        'key': r[3],
                        'default': r[4],
                        'extra': r[5],
                        'is_pk': (r[3] == 'PRI'),
                    })
                return JsonResponse({'success': True, 'columns': columns, 'table': table_name})

        # 3. GET TABLE DATA (BROWSE)
        elif action == 'get_table_data':
            table_name = request.GET.get('table', '').strip()
            page = max(int(request.GET.get('page', 1)), 1)
            page_size = min(max(int(request.GET.get('page_size', 25)), 5), 200)
            search_query = request.GET.get('search', '').strip()
            sort_col = request.GET.get('sort_col', '').strip()
            sort_dir = 'DESC' if request.GET.get('sort_dir', '').upper() == 'DESC' else 'ASC'

            with conn.cursor() as cursor:
                # Get column names & primary key
                cursor.execute(f"DESCRIBE `{table_name}`")
                desc = cursor.fetchall()
                columns = [c[0] for c in desc]
                pk_cols = [c[0] for c in desc if c[3] == 'PRI']

                where_clauses = []
                where_params = []

                if search_query:
                    search_parts = []
                    for c in desc:
                        col_name = c[0]
                        col_type = c[1].lower()
                        if 'blob' in col_type or 'binary' in col_type or 'geometry' in col_type:
                            continue
                        search_parts.append(f"`{col_name}` LIKE %s")
                        where_params.append(f"%{search_query}%")
                    if search_parts:
                        where_clauses.append(f"({' OR '.join(search_parts)})")

                where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

                # Count total rows
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` {where_sql}", where_params)
                total_rows = cursor.fetchone()[0]

                # Sorting
                if sort_col and sort_col in columns:
                    order_sql = f"ORDER BY `{sort_col}` {sort_dir}"
                elif pk_cols:
                    order_sql = f"ORDER BY `{pk_cols[0]}` DESC"
                else:
                    order_sql = ""

                # Pagination
                offset = (page - 1) * page_size
                query = f"SELECT * FROM `{table_name}` {where_sql} {order_sql} LIMIT %s OFFSET %s"
                cursor.execute(query, where_params + [page_size, offset])
                
                raw_rows = cursor.fetchall()
                rows = []
                for r in raw_rows:
                    row_dict = {}
                    for idx, col in enumerate(columns):
                        val = r[idx]
                        if isinstance(val, (datetime, date)):
                            val = val.isoformat()
                        elif isinstance(val, bytes):
                            try:
                                val = val.decode('utf-8')
                            except Exception:
                                val = f"<BLOB {len(val)} bytes>"
                        row_dict[col] = val
                    rows.append(row_dict)

                total_pages = max((total_rows + page_size - 1) // page_size, 1)

                return JsonResponse({
                    'success': True,
                    'columns': columns,
                    'pk_cols': pk_cols,
                    'rows': rows,
                    'total_rows': total_rows,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                })

        # 4. INSERT ROW (CREATE)
        elif action == 'insert_row':
            if request.method != 'POST':
                return JsonResponse({'success': False, 'error': 'Method must be POST'}, status=405)
            
            body = json.loads(request.body.decode('utf-8'))
            table_name = body.get('table', '').strip()
            data = body.get('data', {})

            if not table_name or not data:
                return JsonResponse({'success': False, 'error': 'Table and data required.'}, status=400)

            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                desc = cursor.fetchall()
                col_meta = {
                    c[0]: {
                        'type': c[1].lower(),
                        'nullable': (c[2].upper() == 'YES'),
                        'default': c[4],
                        'extra': c[5].lower()
                    }
                    for c in desc
                }
                valid_cols = set(col_meta.keys())

                cols = []
                vals = []
                placeholders = []
                for k, v in data.items():
                    if k not in valid_cols:
                        continue

                    meta = col_meta[k]
                    # Skip auto_increment columns if empty
                    if 'auto_increment' in meta['extra'] and (v == '' or v is None):
                        continue

                    val_to_save = v
                    if v == '' or v is None:
                        if meta['nullable']:
                            val_to_save = None
                        elif meta['default'] is not None:
                            # Let MySQL apply table default
                            continue
                        else:
                            t = meta['type']
                            if 'int' in t or 'bool' in t or 'decimal' in t or 'float' in t or 'double' in t:
                                val_to_save = 0
                            else:
                                val_to_save = ''

                    cols.append(f"`{k}`")
                    vals.append(val_to_save)
                    placeholders.append("%s")

                if not cols:
                    return JsonResponse({'success': False, 'error': 'Tidak ada data valid untuk disimpan.'}, status=400)

                sql = f"INSERT INTO `{table_name}` ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(sql, vals)
                inserted_id = cursor.lastrowid

            return JsonResponse({'success': True, 'message': 'Data berhasil ditambahkan!', 'inserted_id': inserted_id})

        # 5. UPDATE ROW (EDIT)
        elif action == 'update_row':
            if request.method != 'POST':
                return JsonResponse({'success': False, 'error': 'Method must be POST'}, status=405)

            body = json.loads(request.body.decode('utf-8'))
            table_name = body.get('table', '').strip()
            pk_data = body.get('pk', {})
            update_data = body.get('data', {})

            if not table_name or not pk_data or not update_data:
                return JsonResponse({'success': False, 'error': 'Table, pk, and data are required.'}, status=400)

            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                desc = cursor.fetchall()
                col_meta = {
                    c[0]: {
                        'type': c[1].lower(),
                        'nullable': (c[2].upper() == 'YES'),
                        'default': c[4],
                        'extra': c[5].lower()
                    }
                    for c in desc
                }
                valid_cols = set(col_meta.keys())

                set_parts = []
                params = []
                for k, v in update_data.items():
                    if k not in valid_cols or k in pk_data:
                        continue

                    # Special handling for password: if left blank during edit, do NOT touch/overwrite password (protects SSO and existing hashes)
                    if k == 'password' and (v == '' or v is None):
                        continue

                    meta = col_meta[k]
                    val_to_save = v

                    if v == '' or v is None:
                        if meta['nullable']:
                            val_to_save = None
                        else:
                            t = meta['type']
                            if 'int' in t or 'bool' in t or 'decimal' in t or 'float' in t or 'double' in t:
                                val_to_save = meta['default'] if meta['default'] is not None else 0
                            else:
                                val_to_save = ''

                    set_parts.append(f"`{k}` = %s")
                    params.append(val_to_save)

                where_parts = []
                for pk_col, pk_val in pk_data.items():
                    if pk_col in valid_cols:
                        where_parts.append(f"`{pk_col}` = %s")
                        params.append(pk_val)

                if not set_parts:
                    return JsonResponse({'success': True, 'message': 'Tidak ada kolom yang diubah.'})

                if not where_parts:
                    return JsonResponse({'success': False, 'error': 'Primary key tidak valid.'}, status=400)

                sql = f"UPDATE `{table_name}` SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
                cursor.execute(sql, params)
                affected = cursor.rowcount

            return JsonResponse({'success': True, 'message': f'Data berhasil diperbarui! ({affected} baris terdampak)'})

        # 6. DELETE ROW (DELETE)
        elif action == 'delete_row':
            if request.method != 'POST':
                return JsonResponse({'success': False, 'error': 'Method must be POST'}, status=405)

            body = json.loads(request.body.decode('utf-8'))
            table_name = body.get('table', '').strip()
            pk_data = body.get('pk', {})

            if not table_name or not pk_data:
                return JsonResponse({'success': False, 'error': 'Table and pk are required.'}, status=400)

            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                valid_cols = [c[0] for c in cursor.fetchall()]

                where_parts = []
                params = []
                for pk_col, pk_val in pk_data.items():
                    if pk_col in valid_cols:
                        where_parts.append(f"`{pk_col}` = %s")
                        params.append(pk_val)

                if not where_parts:
                    return JsonResponse({'success': False, 'error': 'Primary key tidak valid.'}, status=400)

                sql = f"DELETE FROM `{table_name}` WHERE {' AND '.join(where_parts)}"
                cursor.execute(sql, params)
                affected = cursor.rowcount

            return JsonResponse({'success': True, 'message': f'Data berhasil dihapus! ({affected} baris terhapus)'})

        # 7. RUN CUSTOM SQL QUERY
        elif action == 'run_sql':
            if request.method != 'POST':
                return JsonResponse({'success': False, 'error': 'Method must be POST'}, status=405)

            body = json.loads(request.body.decode('utf-8'))
            sql_query = body.get('query', '').strip()

            if not sql_query:
                return JsonResponse({'success': False, 'error': 'Query SQL tidak boleh kosong.'}, status=400)

            t_start = time.time()
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                elapsed_ms = round((time.time() - t_start) * 1000, 2)

                if cursor.description:
                    # Query returned rows (e.g. SELECT, SHOW, DESCRIBE)
                    columns = [d[0] for d in cursor.description]
                    raw_rows = cursor.fetchmany(500) # Limit to first 500 rows for display safety
                    rows = []
                    for r in raw_rows:
                        row_dict = {}
                        for idx, col in enumerate(columns):
                            val = r[idx]
                            if isinstance(val, (datetime, date)):
                                val = val.isoformat()
                            elif isinstance(val, bytes):
                                try:
                                    val = val.decode('utf-8')
                                except Exception:
                                    val = f"<BLOB {len(val)} bytes>"
                            row_dict[col] = val
                        rows.append(row_dict)

                    return JsonResponse({
                        'success': True,
                        'is_select': True,
                        'columns': columns,
                        'rows': rows,
                        'row_count': len(rows),
                        'elapsed_ms': elapsed_ms,
                    })
                else:
                    # Non-SELECT statement (INSERT, UPDATE, DELETE, CREATE, etc.)
                    affected = cursor.rowcount
                    return JsonResponse({
                        'success': True,
                        'is_select': False,
                        'affected_rows': affected,
                        'elapsed_ms': elapsed_ms,
                        'message': f"Query berhasil dieksekusi dalam {elapsed_ms} ms. ({affected} baris terdampak)",
                    })

        # 8. EXPORT DATABASE BACKUP (.sql)
        elif action == 'export_sql':
            table_filter = request.GET.get('table', '').strip()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backup_{db_name}_{timestamp}.sql" if not table_filter else f"backup_{table_filter}_{timestamp}.sql"

            def sql_dump_generator():
                yield f"-- LibraryRank Lite phpMyAdmin SQL Dump\n"
                yield f"-- Database: `{db_name}`\n"
                yield f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                yield f"-- Host: {conn.settings_dict.get('HOST', 'localhost')}\n\n"
                yield f"SET FOREIGN_KEY_CHECKS = 0;\n"
                yield f"SET NAMES utf8mb4;\n\n"

                with conn.cursor() as dump_cursor:
                    if table_filter:
                        tables_to_dump = [table_filter]
                    else:
                        dump_cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
                        tables_to_dump = [row[0] for row in dump_cursor.fetchall()]

                    for tbl in tables_to_dump:
                        yield f"-- --------------------------------------------------------\n"
                        yield f"-- Table structure for table `{tbl}`\n"
                        yield f"-- --------------------------------------------------------\n\n"
                        yield f"DROP TABLE IF EXISTS `{tbl}`;\n"

                        # Get CREATE TABLE
                        dump_cursor.execute(f"SHOW CREATE TABLE `{tbl}`")
                        create_table_sql = dump_cursor.fetchone()[1]
                        yield f"{create_table_sql};\n\n"

                        # Dump Rows in chunks
                        dump_cursor.execute(f"SELECT * FROM `{tbl}`")
                        columns = [d[0] for d in dump_cursor.description]
                        
                        chunk = dump_cursor.fetchmany(100)
                        if chunk:
                            yield f"-- Dumping data for table `{tbl}`\n\n"
                            while chunk:
                                insert_rows = []
                                for row in chunk:
                                    formatted_vals = []
                                    for val in row:
                                        if val is None:
                                            formatted_vals.append("NULL")
                                        elif isinstance(val, (int, float)):
                                            formatted_vals.append(str(val))
                                        elif isinstance(val, (datetime, date)):
                                            formatted_vals.append(f"'{val.isoformat()}'")
                                        elif isinstance(val, bool):
                                            formatted_vals.append("1" if val else "0")
                                        elif isinstance(val, bytes):
                                            hex_val = val.hex()
                                            formatted_vals.append(f"0x{hex_val}")
                                        else:
                                            escaped = str(val).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
                                            formatted_vals.append(f"'{escaped}'")
                                    insert_rows.append(f"({', '.join(formatted_vals)})")

                                col_names = ", ".join([f"`{c}`" for c in columns])
                                yield f"INSERT INTO `{tbl}` ({col_names}) VALUES\n" + ",\n".join(insert_rows) + ";\n\n"
                                chunk = dump_cursor.fetchmany(100)

                yield f"SET FOREIGN_KEY_CHECKS = 1;\n"
                yield f"-- Dump completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            response = StreamingHttpResponse(sql_dump_generator(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        # 9. EXPORT TABLE TO CSV
        elif action == 'export_csv':
            table_name = request.GET.get('table', '').strip()
            if not table_name:
                return JsonResponse({'success': False, 'error': 'Table parameter required.'}, status=400)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{table_name}_{timestamp}.csv"

            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `{table_name}`")
                columns = [d[0] for d in cursor.description]
                
                response = HttpResponse(content_type='text/csv; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                # Write BOM for Excel UTF-8 compatibility
                response.write('\ufeff')
                
                writer = csv.writer(response)
                writer.writerow(columns)

                while True:
                    rows = cursor.fetchmany(500)
                    if not rows:
                        break
                    for row in rows:
                        formatted_row = []
                        for val in row:
                            if val is None:
                                formatted_row.append('')
                            elif isinstance(val, (datetime, date)):
                                formatted_row.append(val.isoformat())
                            elif isinstance(val, bytes):
                                formatted_row.append(f"<BLOB {len(val)}B>")
                            else:
                                formatted_row.append(str(val))
                        writer.writerow(formatted_row)

                return response

        else:
            return JsonResponse({'success': False, 'error': f"Aksi '{action}' tidak dikenali."}, status=400)

    except Exception as e:
        logger.exception(f"DB Explorer API Error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
