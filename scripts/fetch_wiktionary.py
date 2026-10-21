"""从 Wiktionary 抓取词表里每个词（短语再拆成单词）的英语音标，用于核对。

用法（在项目根目录运行，可以中断后重跑，已经抓过的会跳过）：
    .venv/bin/python scripts/fetch_wiktionary.py

结果缓存在 data/ipa/wiktionary-raw.json：{词: [{"labels": [...], "ipa": [...]}]}。
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
cache_path = root / "data/ipa/wiktionary-raw.json"
cache_path.parent.mkdir(parents=True, exist_ok=True)
cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

words = [x["w"] for x in json.loads((root / "data/final.json").read_text())]
titles = []
for w in words:
    base = re.sub(r"\s*\(.*?\)", "", w).split("/")[0].strip(" !?")
    titles.append(base)
    if " " in base or "-" in base:
        titles += [p for p in re.split(r"[ \-]", base) if p]
titles = list(dict.fromkeys(t for t in titles if t))


def raw(title):
    url = "https://en.wiktionary.org/w/index.php?action=raw&title=" + urllib.parse.quote(title)
    req = urllib.request.Request(url, headers={"User-Agent": "kids-vocab/1.0 (+https://github.com/GavinKwok-T/daily-words)"})
    try:
        return urllib.request.urlopen(req, timeout=20).read().decode()
    except Exception:
        return None


todo = [t for t in titles if t not in cache]
print(f"共 {len(titles)} 个条目，待抓 {len(todo)} 个", flush=True)
for i, t in enumerate(todo, 1):
    text = raw(t) or (raw(t.lower()) if t != t.lower() else None) or ""
    eng = text.split("==English==", 1)[1] if "==English==" in text else ""
    eng = re.split(r"\n==[^=]", eng)[0]
    entries = []
    for line in eng.splitlines():
        if "{{IPA|en|" not in line:
            continue
        labels = re.findall(r"\{\{(?:a|accent|q|qualifier|i|lb)\|([^}]*)\}\}", line)
        for ipa in re.findall(r"\{\{IPA\|en\|([^}]*)\}\}", line):
            entries.append({"labels": labels, "ipa": [p for p in ipa.split("|") if p.startswith(("/", "["))]})
    cache[t] = entries
    if i % 50 == 0:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False))
        print(f"{i}/{len(todo)}", flush=True)
    time.sleep(0.4)
cache_path.write_text(json.dumps(cache, ensure_ascii=False))
print("done", len(cache))
