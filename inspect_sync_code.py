with open("static/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "syncWearableTo" in l or "syncAiTo" in l:
        print(f"L{i+1}:")
        for j in range(max(0, i-2), min(len(lines), i+25)):
            print(f"  {lines[j]}", end="")
        print("="*60)
