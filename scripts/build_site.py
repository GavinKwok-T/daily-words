"""把单词数据和音频路径合成网页用的 site/data/days.json。

用法（在项目根目录运行）：
    .venv/bin/python scripts/build_site.py

输入：data/final.json（按学习顺序排好的全部单词）、data/audio-index.json（原文 → 音频路径）。
输出：site/data/days.json，每天 20 个词，字段尽量短，网页一次加载全部。
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
PER_DAY = 20
LEVEL_NAMES = {"Starters": "Pre A1 Starters", "Movers": "A1 Movers", "Flyers": "A2 Flyers", "Key": "A2 Key"}

words = json.loads((root / "data/final.json").read_text())
audio = json.loads((root / "data/audio-index.json").read_text()) if (root / "data/audio-index.json").exists() else {}

days, missing_audio = [], 0
for i in range(0, len(words), PER_DAY):
    chunk = words[i:i + PER_DAY]
    items = []
    for x in chunk:
        item = {"w": x["w"], "zh": x["zh"], "ipa": x["ipa"], "ex": x["ex"], "t": x["topic"]}
        if x.get("us"):
            item["us"] = x["us"]
        if x.get("tip"):
            item["tip"] = x["tip"]
        if x["w"] in audio:
            item["a"] = audio[x["w"]]
        else:
            missing_audio += 1
        if x["ex"] in audio:
            item["ea"] = audio[x["ex"]]
        items.append(item)
    levels = list(dict.fromkeys(x["level"] for x in chunk))
    days.append({"d": len(days) + 1, "lv": " / ".join(LEVEL_NAMES[l] for l in levels), "w": items})

out = root / "site/data/days.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(days, ensure_ascii=False, separators=(",", ":")))
print(f"{len(days)} 天，{len(words)} 个词；还没有发音的单词 {missing_audio} 个 -> {out}（{out.stat().st_size // 1024} KB）")
