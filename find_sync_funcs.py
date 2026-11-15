with open("static/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

for fn in ["syncWearableToWeekly", "syncAiToWeekly", "syncWearableToMonthly", "syncAiToMonthly", "syncWearableToYearly", "syncAiToYearly"]:
    match = re.search(r'(window\.' + fn + r'|function\s+' + fn + r')[\s\S]*?\n\s*\};?', text)
    if match:
        print(f"=== {fn} ===")
        print(match.group(0)[:500])
    else:
        print(f"=== {fn} NOT FOUND ===")
