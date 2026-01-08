# -*- coding: utf-8 -*-
"""
Replace fruit product labels with cosmetics equivalents in the home.html template.
This script makes a backup copy before editing.
"""
from pathlib import Path
p = Path(r"d:\New folder\py_doan\webbanmypham\app\templates\app\home.html")
backup = p.with_suffix('.html.bak')
if not backup.exists():
    backup.write_bytes(p.read_bytes())
text = p.read_text(encoding='utf-8')
replacements = {
    'Trái cây nhập khẩu': 'Mỹ phẩm nhập khẩu',
    'title="Dừa"': 'title="Son môi"',
    '>Dừa<': '>Son môi<',
    'alt="Dưa"': 'alt="Son môi"',
    '>Dưa<': '>Son môi<',
    'trái cây': 'mỹ phẩm',
    'Trái cây': 'Mỹ phẩm'
}
for a, b in replacements.items():
    text = text.replace(a, b)
p.write_text(text, encoding='utf-8')
print(f"Updated: {p}\nBackup: {backup}")
