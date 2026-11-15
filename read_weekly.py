with open("static/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(2145, 2220):
    if i < len(lines):
        print(f"L{i+1}: {lines[i]}", end="")
