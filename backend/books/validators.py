import re


def parse_year_from_text(value: str | None) -> int | None:
    """
    從外部來源日期字串解析出西元年份。

    支援格式：
      - "2009"         → 2009
      - "2024-03"      → 2024
      - "2024/03"      → 2024
      - "2024年3月"    → 2024（若剛好是此類中文格式）
      - 其他非數字字串 → None
    """
    if not value:
        return None

    # 先取前4位連續數字（最常見 ISO / Mytb 格式）
    m = re.match(r'^(\d{4})', value.strip())
    if m:
        year = int(m.group(1))
        if 1900 <= year <= 2100:
            return year
        return None

    # 嘗試拆 slash 或 dash
    for sep in ('-', '/'):
        if sep in value:
            part = value.split(sep)[0].strip()
            if part.isdigit() and len(part) == 4:
                year = int(part)
                if 1900 <= year <= 2100:
                    return year

    return None
