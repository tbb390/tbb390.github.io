from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "daily-study"
LINK = '<link rel="stylesheet" href="../assets/daily-study.css">'

updated = 0
skipped = 0

for page in sorted(NOTES.glob("*.html")):
    source = page.read_text(encoding="utf-8")

    if "daily-study.css" in source:
        skipped += 1
        continue

    # Add after any existing inline styles so common rules can unify the visual shell.
    head_end = re.search(r"</head\s*>", source, flags=re.IGNORECASE)
    if not head_end:
        print(f"跳过（没有 head 结束标签）: {page.name}")
        skipped += 1
        continue

    source = source[:head_end.start()] + "  " + LINK + "\n" + source[head_end.start():]
    page.write_text(source, encoding="utf-8")
    updated += 1
    print(f"已添加公共样式: {page.name}")

print(f"完成：新增引用 {updated} 篇，跳过 {skipped} 篇。")
