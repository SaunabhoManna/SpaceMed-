with open("static/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
overview_match = re.search(r'<section class="view[^"]*" id="view-overview">([\s\S]*?)</section>', text)
if overview_match:
    ov_html = overview_match.group(1)
    for i, line in enumerate(ov_html.splitlines()):
        if any(w in line.lower() for w in ["manual", "entry", "ingest", "input", "sync", "bar", "button"]):
            print(f"OV L{i+1}: {line.strip()[:100]}")
