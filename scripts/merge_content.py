"""把 data/content/*.json 的释义、音标、例句合并进词表，排好学习顺序。

用法（在项目根目录运行）：
    .venv/bin/python scripts/merge_content.py

content 里每一项是 [词, 中文, 英式音标, 话题, 例句, 提示?]，词要和 data/words.json 里的 w 一致。
顺序：先按剑桥级别（Starters → Movers → Flyers → Key），同一级别里按话题分组（话题顺序见
TOPICS），话题内保持词表原来的顺序。输出 data/final.json。
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
LEVELS = ["Starters", "Movers", "Flyers", "Key"]
TOPICS = ["动物", "身体", "家人与人物", "食物饮料", "衣物", "家和房间", "学校", "颜色形状", "数字时间",
          "时间", "天气自然", "地点", "交通", "运动爱好", "玩具游戏", "工作", "购物金钱", "科技", "健康",
          "感受", "描述", "动作", "人物", "常用小词"]

words = json.loads((root / "data/words.json").read_text())
content = {}
for f in sorted((root / "data/content").glob("*.json")):
    for row in json.loads(f.read_text()):
        w, zh, ipa, topic, ex, *rest = row
        if topic not in TOPICS:
            raise SystemExit(f"{f.name}: {w} 的话题 {topic} 不在 TOPICS 里")
        content[w] = {"zh": zh, "ipa": ipa, "topic": topic, "ex": ex, "tip": rest[0] if rest else None}

missing = [x["w"] for x in words if x["w"] not in content]
extra = sorted(set(content) - {x["w"] for x in words})
merged = [{**x, **content[x["w"]]} for x in words if x["w"] in content]

for lv in LEVELS:
    total = sum(1 for x in words if x["level"] == lv)
    done = sum(1 for x in merged if x["level"] == lv)
    print(f"{lv}: {done}/{total}")
print("还没写的：", len(missing), "；多出来的（拼写对不上词表）：", extra)

if not missing:
    order = {lv: i for i, lv in enumerate(LEVELS)}
    merged.sort(key=lambda x: (order[x["level"]], TOPICS.index(x["topic"])))  # sort 是稳定的，组内保持原顺序
    (root / "data/final.json").write_text(json.dumps(merged, ensure_ascii=False, indent=1))
    print(f"已写入 data/final.json（{len(merged)} 个词）；网页数据由 scripts/build_site.py 生成")
