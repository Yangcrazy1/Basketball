# 世界上另一个我 · V7 神人海克斯

手机直接体验：https://yangcrazy1.github.io/Basketball/?v=7-fun 。[离线下载入口](https://yangcrazy1.github.io/Basketball/download/?v=7-fun)。一个完整 HTML（约 5.4 MB），无需账号与后台，头像、原创恶搞图标与题库都在文件里。

## 这版改了什么

- **网友 DIY 风格的恶搞海克斯**：25 张自制卡，包括掀桌、第五位收集者、泉水股东、开送驾驶证、回归基本功、正方形讲解、这波不亏等。卡面包含反常效果与反转吐槽。16 个新生成的原创搞笑图标供这些卡使用；V7 不加载官方强化数据或图标。
- 参考用户提供的恶搞卡和已经查看的网络 DIY 配图，重新写成 LoL 语境。不是“网上原卡合集”，没有把未读到的文章内容冒充素材。参考记录见 `docs/v7-parody-references.json`。
- **相关程度**：人物匹配与恶搞卡都依据实际选择的行为语义及六维风格；卡牌引用真实作答。挂机与开送、争经济与保队友会给出不同结果。带 AFK/甩锅前提的卡只有选中过相应行为才会出现。队友分工也随卡牌类别变化。
- **问题因果**：100 道联盟情境，25 个四幕小剧场（海克斯 64、峡谷 36）。8 / 16 / 24 题随机抽取 2 / 4 / 6 个剧场，内部顺序连贯，选项随机。收集者关键情境下一幕有四个不同问题，返回修改后跟随变化。新局首题改变，续答保留本轮。
- **界面**：缩短手机首页，首屏可开始；增加四选一试玩和25张卡图鉴；结果先显示人物、本命恶搞卡与匹配证据，六维详情可展开；海报按钮固定在底部。
- **海报**：1080×1920 人物×原创恶搞卡×五人战队 PNG，直接下载。仍有夜场紫/奶油两套配色。
- 42 位人物、44 个主题条目，保留新版卡通头像、合法五人分位、架空 S8/Galio/GOAT 剧情。美国讲师与三维模型继续移除。篮球/抽象网络各 36 题，共 172 题。

所有卡牌效果和人物倾向都是本作娱乐创作。37 位人物有已检查的公开参考图像，5 位为明确标记的示意头像；来源及授权状态见 `image-sources.json`。V6 的官方强化资料文件仅作为历史来源保留，不进入 V7 运行文件。

## 构建与验证

```sh
python build.py
node --test tests/engine.test.cjs
python tests/browser-check.py
python tests/public-web-check.py
```

构建只需 Python 标准库。引擎测试使用 Node。浏览器检查需要 Playwright、Pillow 与 `/usr/bin/chromium`。报告为 `docs/browser-check-v7.json` 和 `docs/web-verification-v7.json`；范围是 Chromium 手机尺寸、实际下载与离线执行，不是实体手机硬件测试。

核心内容：`src/data.json`；匹配与问题分支：`src/engine.js`；页面和 Canvas 海报：`src/app.js`；卡牌：`assets/parody-cards.json`；新图标：`assets/parody-icon-atlas.json`、`assets/parody-icons-v7.webp`。普通构建不需要网络。

`tools/v7-content.py` 是内容制作脚本；`tools/v6-content.py` 为旧版官方资料制作工具，不属于 V7 构建前置。V7 使用单独的 `world-otherme.v7` 本机存储，保留其他版本的记录。
