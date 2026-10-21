"""清理 data/wordlist.json：拆出美式说法和用法备注，去重，去掉碎片、人名和最基础的虚词。

用法（在项目根目录运行）：
    .venv/bin/python scripts/clean_wordlist.py

输出 data/words.json，每个词 {w, us, note, pos, level}：
- w：英式写法（词表本身以英式为主）
- us：美式写法或说法不同时才有，比如 colour → color，rubbish → garbage
- note：词表里的用法限定，比如 bat 只指"球拍"
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
raw = json.loads((root / "data/wordlist.json").read_text())

# 四年级、英语授课学校的孩子早就会的虚词，不占名额
TRIVIAL = set("""a an a/an the and or but i you he she it we they me him her us them my your his its our their
mine yours hers ours theirs this that these those yes no hello hi bye goodbye oh ok ok/okay okay
be do have can not to of in on at for with from""".split())
NAMES = {"ann/ anna", "may (as in girl’s name)", "may (as in girl's name)", "sweet(s"}  # 人名和断开的碎片
# Key 里的美式说法，前面已经作为英式词的 us 学过
US_ALIASES = {"apartment", "candy", "soccer", "store", "backpack", "cookie", "fries", "eraser", "truck",
              "elevator", "movie", "fall", "flashlight", "pajamas", "gray", "color", "center", "favorite",
              "theater", "tire", "math", "program", "kilometer"}
# Key 里和前面级别重复、只是写法不同的词
KEY_DUPES = {"alright", "people", "stairs", "stomach ache", "wake", "wake up", "no one", "cafe/café",
             "boot", "stripes", "have got to", "have to"}  # have (got) to 在 Movers 已经学过
FIX = {"TV /television": "TV", "television/TV": "TV",
       # 单复数并列的写法统一成单数，复数写在例句或提示里
       "child/ children": "child", "foot/feet": "foot", "man/men": "man", "mouse/mice": "mouse",
       "person/people": "person", "woman/women": "woman", "leaf/leaves": "leaf", "tooth/teeth": "tooth"}
# PDF 里被断成两行、没解析出来的词，补回它们原本所在的级别
MANUAL = {
    "Starters": [("Miss", "n"), ("Mr", "n"), ("Mrs", "n")],
    "Movers": [("city centre", "n"), ("shopping centre", "n"), ("sports centre", "n"),
               ("could (past of can)", "v"), ("take off (get undressed)", "v")],
    "Flyers": [("a.m.", "adv"), ("p.m.", "adv"), ("kilometre (US kilometer)", "n"),
               ("programme (US program)", "n"), ("file (computer)", "n"), ("take (time)", "v")],
    "Key": [],
}


def parse(entry):
    s = FIX.get(entry["raw"], entry["raw"]).replace("’", "'").strip()
    us = None
    m = re.search(r"\(UK ([^)]+)\)", s)
    if m:  # 'apartment (UK flat)'：英式在括号里
        us = re.sub(r"\s*\(UK [^)]+\)", "", s).strip()
        s = m.group(1).strip()
    m = re.search(r"\(US ([^)]+)\)", s)
    if m:  # 'colour (US color)'
        us = m.group(1).strip()
        s = (s[:m.start()] + s[m.end():]).strip()
    note = None
    m = re.search(r"\((?:as in |e\.g\. |as )?([^)]+)\)\s*$", s)
    if m and not re.search(r"\(s\)|\(e\)|\(up\)|\(bear\)|\(got\)|\('s\)", s):
        note = m.group(1).strip()
        s = s[:m.start()].strip()
    s = re.sub(r"\s+", " ", s)
    return s, us, note


def key_of(w):
    w = w.lower().replace("’", "'")
    w = re.split(r"\s*/\s*", w)[0]
    return re.sub(r"[!?.]", "", w).strip()


entries = []
for lv in ["Starters", "Movers", "Flyers", "Key"]:
    entries += [e for e in raw if e["level"] == lv]
    entries += [{"raw": r, "pos": pos, "level": lv} for r, pos in MANUAL[lv]]

seen, out, dropped = set(), [], []
for e in entries:
    r = e["raw"] if "raw" in e else e["w"]
    if r.lower() in NAMES or r.startswith("(") or (r.endswith(")") and "(" not in r) or re.search(r"\d", r):
        dropped.append(r)
        continue
    w, us, note = parse({"raw": r})
    if w.endswith("(s") or r == "T uesday":  # PDF 断行留下的碎片；Tuesday 和其他星期几一起放在 Key 级别学
        dropped.append(r)
        continue
    k = key_of(w)
    if (k in TRIVIAL or w.lower() in TRIVIAL) and w != "IT":  # IT 是信息技术，不是代词 it
        dropped.append(w)
        continue
    if e["level"] == "Key" and (k in US_ALIASES or w.lower() in KEY_DUPES):
        dropped.append(w)
        continue
    if k in seen:
        continue
    seen.add(k)
    out.append({"w": w, "us": us, "note": note, "pos": e["pos"], "level": e["level"]})

(root / "data/words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for lv in ["Starters", "Movers", "Flyers", "Key"]:
    print(lv, sum(1 for x in out if x["level"] == lv))
print("合计", len(out), "；去掉", len(dropped), "条：", "、".join(dropped))
