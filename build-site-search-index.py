from html.parser import HTMLParser
from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "search-index.json"
SKIP_DIRS = {".git", ".github", "assets", "test", "tests"}
SKIP_NAMES = {"day-template.html", "404.html"}

class PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.title_parts, self.heading_parts = [], [], []
        self.in_title = False
        self.in_heading = False
        self.ignored = []

    def handle_starttag(self, tag, attrs):
        if tag == "title": self.in_title = True
        if tag == "h1": self.in_heading = True
        if tag in {"script", "style", "noscript", "svg"}: self.ignored.append(tag)
        if tag in {"p", "li", "div", "section", "h1", "h2", "h3", "h4", "br", "tr"}: self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "h1": self.in_heading = False
        if tag in self.ignored:
            self.ignored.reverse(); self.ignored.remove(tag); self.ignored.reverse()
        if tag in {"p", "li", "div", "section", "h1", "h2", "h3", "h4", "br", "tr"}: self.parts.append(" ")

    def handle_data(self, data):
        if self.in_title: self.title_parts.append(data)
        if self.in_heading: self.heading_parts.append(data)
        if not self.ignored: self.parts.append(data)

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def is_daily_note(path):
    return path.parent.name == "daily-study" and re.fullmatch(r"day\d+note\.html", path.name, re.I) is not None

def label_for(path):
    rel = path.relative_to(ROOT).as_posix()
    if is_daily_note(path):
        match = re.search(r"day(\d+)note\.html$", path.name, re.I)
        return f"Day {match.group(1)}" if match else "每日记录"
    if rel.startswith("algorithm/"): return "算法练习"
    if rel.startswith("roadmap/"): return "学习路线"
    if rel.startswith("review/"): return "复盘记录"
    return path.parent.name if path.parent != ROOT else "网站页面"

def kind_for(path):
    rel = path.relative_to(ROOT).as_posix()
    if is_daily_note(path): return "daily"
    if path.parent.name == "daily-study": return "page"
    if rel.startswith("algorithm/"): return "algorithm"
    if rel.startswith("roadmap/"): return "roadmap"
    if rel.startswith("review/"): return "review"
    return "page"

def main():
    items = []
    for path in ROOT.rglob("*.html"):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in rel_parts) or path.name.lower() in SKIP_NAMES or path.relative_to(ROOT).as_posix() == "index.html":
            continue
        parser = PageText()
        try: parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            print(f"读取失败: {path.relative_to(ROOT)}: {exc}"); continue
        title = clean(" ".join(parser.heading_parts)) or clean(" ".join(parser.title_parts))
        if not title or title.casefold() == path.stem.casefold():
            match = re.fullmatch(r"day(\d+)note", path.stem, re.I)
            title = f"第 {match.group(1)} 天学习记录" if match else path.stem
        rel = path.relative_to(ROOT).as_posix()
        items.append({"kind": kind_for(path), "label": label_for(path), "title": title, "content": clean(" ".join(parser.parts)), "file": rel})
        print(f"完成: {rel}")
    items.sort(key=lambda item: (item["label"], item["title"]))
    OUTPUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"全站搜索索引完成：{len(items)} 个页面 -> {OUTPUT.name}")

if __name__ == "__main__": main()
