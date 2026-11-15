with open("static/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

for m in re.finditer(r'(manual entry|digital ingestion|sync-action-bar|syncactionbar)', text, re.IGNORECASE):
    idx = m.start()
    print("Match at line:", text[:idx].count("\n") + 1, ":", text[idx:idx+100].replace("\n", " "))
