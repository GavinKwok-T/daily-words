"""用微软 Azure 神经语音（英音 Sonia）给每个单词和例句生成发音，一段一个文件。

用法（在项目根目录运行，可以中断后重跑，已生成的会跳过）：
    .venv/bin/python scripts/make_audio.py

输出：site/audio/w/<单词>.m4a、site/audio/ex/<例句哈希>.m4a，以及 data/audio-index.json
（原文 → 文件路径）。密钥从项目根目录的 .env 读取（AZURE_SPEECH_KEY、AZURE_SPEECH_REGION），
.env 不进版本库。只切掉首尾静音，不做别的裁剪：Azure 的输出是稳定的，词尾没有杂音。
"""
import hashlib
import io
import json
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
import soundfile as sf

root = Path(__file__).resolve().parent.parent
VOICE = "en-GB-SoniaNeural"
env = dict(line.split("=", 1) for line in (root / ".env").read_text().splitlines() if "=" in line)
KEY, REGION = env["AZURE_SPEECH_KEY"].strip(), env["AZURE_SPEECH_REGION"].strip()
ENDPOINT = f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or hashlib.sha1(text.encode()).hexdigest()[:10]


# 显示写法和该读的内容不一样的词
SPEAK = {"v/versus": "versus", "as ... as": "as big as", "Dr": "Doctor", "Mr": "Mister",
         "Mrs": "Missus", "Ms": "Mizz"}


def spoken(word):
    """显示用的写法里有括号、斜杠，朗读时只读主体：'teddy (bear)' → 'teddy bear'，
    'barbecue/barbeque' → 'barbecue'，'give somebody a call/ring' → 'give somebody a call'。"""
    if word in SPEAK:
        return SPEAK[word]
    w = re.sub(r"\(([^)]*)\)", r"\1", word)
    w = re.sub(r"\s*/\s*\S+", "", w)
    return re.sub(r"\s+", " ", w).strip()


def tts(text, rate):
    ssml = (f'<speak version="1.0" xml:lang="en-GB"><voice name="{VOICE}">'
            f'<prosody rate="{rate}">{escape(text)}</prosody></voice></speak>')
    req = urllib.request.Request(ENDPOINT, data=ssml.encode(), method="POST", headers={
        "Ocp-Apim-Subscription-Key": KEY, "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm", "User-Agent": "kids-vocab"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            time.sleep(3.2)  # 免费层每分钟约 20 次请求
            return data
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise SystemExit(f"Azure 返回 {e.code}：{e.read()[:200]!r}")
            time.sleep(int(e.headers.get("Retry-After") or 15))


def save(wav_bytes, out):
    audio, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32")
    loud = np.where(np.abs(audio) > 0.003)[0]
    if len(loud):
        pad = int(0.06 * sr)
        audio = audio[max(loud[0] - pad, 0): loud[-1] + pad]
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        sf.write(wav, audio, sr)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(wav), str(out)], check=True)


words = json.loads((root / "data/final.json").read_text())
index_path = root / "data/audio-index.json"
index = json.loads(index_path.read_text()) if index_path.exists() else {}
jobs = []
for x in words:
    jobs.append((x["w"], f"audio/w/{slug(x['w'])}.m4a", spoken(x["w"]), "-10%"))  # 文件名按显示写法，避免 Dr 和 doctor 撞名
    jobs.append((x["ex"], f"audio/ex/{hashlib.sha1(x['ex'].encode()).hexdigest()[:12]}.m4a", x["ex"], "-5%"))

paths = {}
for text, rel, _, _ in jobs:
    if paths.setdefault(rel, text) != text:
        raise SystemExit(f"文件名冲突：{paths[rel]!r} 和 {text!r} 都会存成 {rel}")

todo = [j for j in jobs if not (root / "site" / j[1]).exists()]
print(f"共 {len(jobs)} 段，待生成 {len(todo)} 段", flush=True)
for i, (text, rel, say, rate) in enumerate(todo, 1):
    save(tts(say, rate), root / "site" / rel)
    index[text] = rel
    if i % 25 == 0:
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1))
        print(f"{i}/{len(todo)}", flush=True)
for text, rel, _, _ in jobs:
    index[text] = rel
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1))
print("done", len(index))
