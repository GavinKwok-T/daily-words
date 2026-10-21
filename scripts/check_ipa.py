"""把我们写的英式音标和 Wiktionary 交叉核对，列出对不上的词。

用法（在项目根目录运行，先跑 scripts/fetch_wiktionary.py）：
    .venv/bin/python scripts/check_ipa.py

先统一两边的记法（Wiktionary 用 ɹ、ɛ、t͡ʃ、/ʃən/，牛津用 r、e、tʃ、/ʃn/；长音符号、次重音、
音节点、单音节词的重音符号都忽略），短语拆成单词逐个比。对不上不一定是错，但每个都要人工看过。
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
words = json.loads((root / "data/final.json").read_text())
wikt = json.loads((root / "data/ipa/wiktionary-raw.json").read_text())
SWAPS = [("ɝ", "ɜr"), ("ɚ", "ər"), ("ɹ", "r"), ("ɛ", "e"), ("ɐ", "ʌ"), ("ᵻ", "ɪ"), ("ɫ", "l"), ("ɡ", "g"), ("ɾ", "t")]


def norm(ipa):
    s = ipa.strip("/[] ")
    for a, b in SWAPS:
        s = s.replace(a, b)
    s = re.sub(r"[̀-ͯ]", "", s)
    s = re.sub(r"[ːˌ.‿ ]", "", s).lstrip("ˈ")
    s = re.sub(r"ə([nlm])(?![aeiouæɑɒɔəɜɪʊʌ])", r"\1", s)
    s = s.replace("r", "")  # 英式不卷舌：比较时忽略所有 r 的有无，避免和美式读法互相干扰
    return s


def expand(ipa):
    if "(" not in ipa:
        return [ipa]
    m = re.search(r"\(([^)]*)\)", ipa)
    return expand(ipa[:m.start()] + m.group(1) + ipa[m.end():]) + expand(ipa[:m.start()] + ipa[m.end():])


def pool(title):
    return {norm(x) for e in wikt.get(title, []) for p in e["ipa"] if p.startswith("/") for x in expand(p)}


missing, bad = [], []
for x in words:
    w, ours = x["w"], x["ipa"]
    base = re.sub(r"\s*\(.*?\)", "", w).split("/")[0].strip(" !?")
    if pool(base):
        if norm(ours) not in pool(base):
            bad.append((w, ours, sorted(pool(base))[:6]))
        continue
    parts = [p for p in re.split(r"[ \-]", base) if p]
    our_parts = ours.strip("/").split()
    if len(parts) > 1 and len(parts) == len(our_parts) and all(pool(p) for p in parts):
        wrong = [p for p, o in zip(parts, our_parts) if norm(o) not in pool(p)]
        if wrong:
            bad.append((w, ours, ["组成词对不上：" + "、".join(wrong)]))
    else:
        missing.append(w)

print(f"共 {len(words)} 个词；Wiktionary 查不到 {len(missing)} 个；对不上 {len(bad)} 个\n")
print("查不到：", "、".join(missing), "\n")
for w, ours, ref in bad:
    print(f"{w:22} 我们 {ours:22} Wiktionary {' '.join(ref)}")
