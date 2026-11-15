import re

with open("static/index.html", "r", encoding="utf-8") as f:
    text = f.read()

print("Searching for overview sections and digital ingestion...")
overview_match = re.search(r'<section class="view[^"]*" id="view-overview">([\s\S]*?)</section>', text)
if overview_match:
    print("Overview length:", len(overview_match.group(1)))
    lines = overview_match.group(1).splitlines()
    print("Total lines in overview:", len(lines))
    for i, l in enumerate(lines[:60]):
        print(f"L{i+1}: {l[:120]}")

print("\n--- Digital references ---")
for i, l in enumerate(text.splitlines()):
    if any(k in l.lower() for k in ["digital ingestion", "ingest", "panemanualinput", "panedigitalinput", "tabmodedigital"]):
        print(f"Line {i+1}: {l.strip()[:120]}")
