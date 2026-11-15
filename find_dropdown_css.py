with open("static/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'(\.spacemed-selector-bar|\.spacemed-dropdown)[\s\S]*?\}', text)
for m in matches:
    print(m)
