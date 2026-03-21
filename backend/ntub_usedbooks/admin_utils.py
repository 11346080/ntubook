import csv
from datetime import datetime
from io import StringIO

from django.http import HttpResponse


def export_model_as_csv(modeladmin, request, queryset):
    """
    Generic CSV export action for any Django queryset.

    - UTF-8 BOM written once at the very beginning (Excel compatibility)
    - Header row written once before data rows (even if queryset is empty)
    - ForeignKey fields resolved to their __str__() value
    - datetime fields formatted as %Y-%m-%d %H:%M:%S
    - bool fields output as '是' / '否'
    - None values output as empty string
    """
    opts = modeladmin.model._meta
    field_names = [f.name for f in opts.fields if not f.many_to_many and not f.one_to_many]

    buffer = StringIO()
    writer = csv.writer(buffer)

    # Step 1: Write UTF-8 BOM exactly once
    buffer.write('\ufeff')

    # Step 2: Write header row exactly once
    header = []
    for fname in field_names:
        try:
            header.append(opts.get_field(fname).verbose_name)
        except Exception:
            header.append(fname)
    writer.writerow(header)

    # Step 3: Write one data row per object
    for obj in queryset:
        row = []
        for fname in field_names:
            field = opts.get_field(fname)
            value = field.value_from_object(obj)
            if value is None:
                row.append('')
            elif hasattr(field, 'remote_field') and field.remote_field:
                try:
                    row.append(str(getattr(obj, fname)) or '')
                except Exception:
                    row.append('')
            elif isinstance(value, bool):
                row.append('是' if value else '否')
            elif hasattr(value, 'strftime'):
                row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row.append(str(value))
        writer.writerow(row)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{opts.model_name}_{timestamp}.csv'

    response = HttpResponse(
        buffer.getvalue(),
        content_type='text/csv; charset=utf-8',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


export_model_as_csv.short_description = '匯出所選項目為 CSV'
