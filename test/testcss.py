from pathlib import Path
from html.parser import HTMLParser
from collections import Counter

class Inventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = Counter()
        self.classes = Counter()

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        for name, value in attrs:
            if name == "class" and value:
                self.classes.update(value.split())

for path in sorted(Path("daily-study").glob("*.html")):
    parser = Inventory()
    parser.feed(path.read_text(encoding="utf-8"))
    print(f"\n{path.name}")
    print("标签：", ", ".join(f"{k}:{v}" for k, v in parser.tags.most_common(12)))
    print("类名：", ", ".join(f"{k}:{v}" for k, v in parser.classes.most_common(12)))