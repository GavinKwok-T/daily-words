# Daily Words

给小学生用的英语单词网页：每天解锁 20 个新词，配英音发音、英式音标、中文释义、例句和拼写小测，错词自动进错词本。不需要账号，手机、平板、电脑打开网页就能用。

- **词表**：剑桥英语官方词表 Pre A1 Starters → A1 Movers → A2 Flyers → A2 Key，共 1788 个词，大约 90 天学完。同级别里按话题分组，从易到难。
- **发音**：微软 Azure 神经语音，英音 `en-GB-SoniaNeural`。
- **音标**：牛津风格的英式音标，和 Wiktionary 交叉核对过。
- **拼写**：以英式为准，美式写法不同的会标出来（比如 colour，美式 color）。
- **陪练**：网页上的"复制给 Gemini"按钮，配合 `docs/gemini-gem.md` 里的 Gem 设置。
- **解锁**：从开始日期起每天解锁 20 个词。日期取网站服务器响应头里的时间，固定按菲律宾时间（Asia/Manila）计算，改设备时间不会提前解锁；没网时才用设备时间。改开始日期需要家长密码（4 位数，存在设备上，只防孩子随手改，不是安全加密）。

## 目录

| 路径 | 内容 |
| --- | --- |
| `site/` | 网页本身（发布到 GitHub Pages 的就是这个目录） |
| `site/data/days.json` | 90 天的单词数据，由 `scripts/build_site.py` 生成 |
| `site/audio/` | 每个单词、例句一个音频文件 |
| `sources/` | 剑桥官方词表 PDF |
| `data/wordlist.json`、`data/words.json` | 从 PDF 提取、清理后的词表 |
| `data/content/*.json` | 每个词的中文、音标、话题、例句、提示（人工编写） |
| `data/final.json` | 合并、排好学习顺序的全部单词 |
| `data/ipa/wiktionary-raw.json` | 从 Wiktionary 抓的音标，用来核对 |
| `docs/gemini-gem.md` | Gemini"单词小老师"的设置说明 |

## 重新生成

```bash
.venv/bin/python scripts/build_wordlist.py    # PDF → data/wordlist.json
.venv/bin/python scripts/clean_wordlist.py    # 去重、清理 → data/words.json
.venv/bin/python scripts/merge_content.py     # 合并内容、排序 → data/final.json
.venv/bin/python scripts/fetch_wiktionary.py  # 抓 Wiktionary 音标（可中断续跑）
.venv/bin/python scripts/check_ipa.py         # 核对音标
.venv/bin/python scripts/make_audio.py        # 生成发音（可中断续跑，约 3–4 小时）
.venv/bin/python scripts/build_site.py        # 生成 site/data/days.json
```

发音需要 Azure 语音服务的密钥：项目根目录的 `.env`（不进版本库）里放 `AZURE_SPEECH_KEY` 和 `AZURE_SPEECH_REGION`。目前 `.env` 是指向 `~/Projects/ielts-vocab/.env` 的链接，两个项目共用一个免费层资源。

环境：`/opt/homebrew/bin/python3.12 -m venv .venv && .venv/bin/pip install pypdf soundfile numpy`；音频转换用 macOS 自带的 `afconvert`。

本地预览：`python3 -m http.server 8765 --directory site`，然后打开 http://localhost:8765 。
