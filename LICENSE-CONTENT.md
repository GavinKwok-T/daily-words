# 内容许可 / Content License

这个仓库里的东西分三类，许可各不相同。

## 1. 代码：MIT

`site/index.html`、`scripts/` 下的脚本和 `.github/` 下的配置采用 [MIT 许可](LICENSE)：可以自由使用、修改、再发布，保留版权声明即可。

## 2. 学习内容：CC BY-NC 4.0

每个单词的**中文释义、例句、记忆提示和音标**（`data/content/`、`data/final.json`、`site/data/days.json` 里的这些字段），以及 `docs/` 下的文档，采用 [知识共享 署名-非商业性使用 4.0 国际许可协议（CC BY-NC 4.0）](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans)：

- **可以**：复制、分享给其他家长、老师和孩子，也可以修改、改编。
- **需要**：注明来源，比如"来自 Daily Words（https://github.com/GavinKwok-T/daily-words）"，并说明是否做过修改。
- **不可以**：用于商业目的，比如打包售卖、放进收费课程。

## 3. 不在上述授权范围内的部分

- **词表**：选用哪些单词、分成哪几个级别，依据的是剑桥英语官方词表 Pre A1 Starters、A1 Movers、A2 Flyers（2018）和 A2 Key（2025），© UCLES（Cambridge Assessment English）。这里只是注明出处，不代表剑桥授权。官方词表请到 [cambridgeenglish.org](https://www.cambridgeenglish.org/) 获取。
- **发音音频**（`site/audio/`）：用微软 Azure 神经语音（en-GB-SoniaNeural）生成，供这个网页播放使用，不随上面的许可授权。需要音频的话，建议用自己的语音服务重新生成（`scripts/make_audio.py`）。

---

**Summary in English.** Code is MIT-licensed (see [LICENSE](LICENSE)). The learning content (Chinese meanings, example sentences, tips, IPA transcriptions) and the docs are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). The selection and levelling of words is based on the Cambridge English wordlists (© UCLES) and is credited, not licensed, here. The audio files were generated with Microsoft Azure neural TTS and are not covered by these licenses.
