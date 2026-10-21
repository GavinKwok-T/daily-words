"""从剑桥官方词表 PDF 提取单词，按级别从易到难合并成总表。

用法（在项目根目录运行）：
    .venv/bin/python scripts/build_wordlist.py

输入：sources/ 下的两份官方 PDF（Pre A1 Starters / A1 Movers / A2 Flyers 合订本 2018，
A2 Key 词汇表 2025）。输出：data/wordlist.json，保留词表原文、词性和级别，
去重和整理由 scripts/clean_wordlist.py 完成。
"""
import json
import re
from pathlib import Path

from pypdf import PdfReader

root = Path(__file__).resolve().parent.parent
YLE = root / "sources/506166-starters-movers-flyers-word-list-2018.pdf"
KEY = root / "sources/506886-a2-key-2020-vocabulary-list.pdf"
LEVELS = ["Starters", "Movers", "Flyers", "Key"]

POS = r"(?:adj|adv|conj|det|dis|excl|int|n|poss adj|poss|prep|pron|v)"
YLE_ENTRY = re.compile(rf"(.+?)\s+({POS}(?:\s*\+\s*{POS})*)(?:\s+of (?:place|time|direction))?(?=\s+[a-zA-Z(]|\s*$)")


def pages(pdf, first, last):
    reader = PdfReader(pdf)
    return "\n".join(reader.pages[i].extract_text() or "" for i in range(first - 1, last))


def yle_level(text):
    """解析 Starters/Movers/Flyers 某一级的 A–Z 词表，到 Letters & numbers / Names 为止。"""
    text = re.split(r"\nLetters & numbers|\nNames\n", text)[0]
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) == 1 or "wordlist" in line or line.startswith(("Grammatical key", "(No words")):
            continue
        if re.fullmatch(rf"{POS}\s+\w+.*", line) and line.split()[0] in {"adj", "adv", "conj", "det", "dis", "excl", "int", "n", "poss", "prep", "pron", "v"}:
            continue  # 词性缩写说明
        for m in YLE_ENTRY.finditer(line):
            word, pos = m.group(1).strip(), m.group(2).strip()
            if word[:1].isupper() and pos == "n" and " " not in word and word not in {"TV", "T-shirt"}:
                continue  # 人名（Alex、Alice…）
            entries.append({"raw": word, "pos": pos})
    return entries


def key_list(text):
    text = text.split("Appendix 1")[0]
    entries = []
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z][^()•©]*?)\s*\(([^)]*)\)\s*$", line.strip())
        if m:
            entries.append({"raw": m.group(1).strip(), "pos": m.group(2).strip()})
    return entries


raw_levels = {
    "Starters": yle_level(pages(YLE, 4, 7)),
    "Movers": yle_level(pages(YLE, 8, 11)),
    "Flyers": yle_level(pages(YLE, 12, 16)),
    "Key": key_list(pages(KEY, 4, len(PdfReader(KEY).pages))),
}

words = [{"raw": e["raw"], "pos": e["pos"], "level": level} for level in LEVELS for e in raw_levels[level]]
# 去重、拆美式说法交给 clean_wordlist.py

out = root / "data/wordlist.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(words, ensure_ascii=False, indent=1))
for level in LEVELS:
    print(f"{level}: {len(raw_levels[level])} 条")
print("合计", len(words), "条 ->", out)
