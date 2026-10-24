# 平行宇宙的另一个我 · V14 平行人生

手机娱乐网页：英雄联盟综合、篮球梦之队、抽象热梗。三幕独立暖色绘本引导穿越，随机 8／16／24 道情境题，按真实作答获得身份、海克斯与五人队，再进入会因选择改变的六幕故事。发行编号 14，新答题 schema 为 13。

- **直接体验**：https://yangcrazy1.github.io/Basketball/v14/
- **实际内容审阅、下载、独立原稿与截图**：https://yangcrazy1.github.io/Basketball/v14/review.html
- 58 位活动人物、332 道情境题、174 张海克斯；其中 137 张人物代表卡形成 143 条归属，六张共享卡各保存一次。新增格林与恶鼠，新活动名单移除任正非。
- 三张独立竖幅开场、浅暖纸色与苔绿主色，保留夜间配色及 V10 棱彩海克斯画风。首页、图鉴、答题、身份与故事按小程序触控交互优化。
- 故事每次打开可重看，大厅默认折叠，顶部常驻“我的穿越故事”。两种配色。
- 自动／自选五人战队，三主题各 48 种搞笑队名组合；换名不改变身份、分数与阵容。支持保存、历史重放与 1080×1920 五人合照 PNG。
- 每人六幕故事、两次选择和不同结局；背包只记录真实答题获得或故事明确奖励的卡，未获得不发动，返回改选会撤销后续奖励。58 人故事均已完成。
- 热门人物在答案相近时有更高优先级；原始匹配分不被加分覆盖，每位启用人物均有合法作答可匹配到。

## 构建与验证

使用 Python、Node 与已有 Pillow 压缩图片；浏览器检查使用环境已有 Playwright 与 Chromium。运行页面无第三方在线依赖。

```sh
python build.py
python tools/build-web.py
python tools/build-xhs.py
node --expose-internals tools/check-xhs.mjs
node --test tests/engine.test.cjs tests/legacy-engine.test.cjs tests/xhs-platform.test.cjs tests/v13-content.test.cjs tests/v13-priority-history.test.cjs tests/v14-engine.test.cjs
python tests/browser-check-v14.py
python tools/package-v14.py
```

开发源文件位于 `src/`。`src/legacy/`、`src/legacy-v11/`、`src/legacy-v12/` 分别冻结 schema 10、11、12；历史记录用对应引擎重放。V14 内容源在 `content/v14-*.json`，`python content/build-v14-content.py --assemble` 严格检查全量稿后装配。不要重跑旧版本一次性迁移脚本覆盖当前题库。

## 产物与验证边界

- `release/world-another-me-v14.html`：完整嵌入图片的离线单文件。
- `release/world-another-me-v14-web.zip`：静态网页部署包。
- `release/world-another-me-v14-xhs.zip`：小红书待上传包，根目录 `index.html`。
- `docs/v14-delivery.md`、`docs/v14-build-manifest.json`、`docs/browser-check-v14.json`、`docs/v14-unit-check.json` 与 `docs/xhs-validation-v14.json`：变更、哈希及校验记录。

58 项逻辑／存储测试、24 组完整浏览器流程、8 组实际审阅页检查通过。小红书 ZIP 约 8.11 MiB，83 个本地文件，四个经典脚本通过 ES2017 解析；目录／ZIP 静态审计通过，体积建议值警告已记录。截图为手机视口模拟。静态检查与 SDK 契约模拟不代表原生验收或平台审核通过；**创服平台模拟器、Android 真机扫码、iOS 真机扫码仍待用户验证**；Chrome 61 CSS 与实际设备性能未实测。

`image-sources.json` 与 `docs/v14-portrait-references.md` 记录参考来源、实际字节指纹与漫画对应关系。尼达、伊利采用核对过的官方公开头像；头像归属核对不等于全部真人面部独立核验。王思聪热狗姿势为原创新绘。公开照片参考核对不等于商用授权；漫画人物、标签、剧情和海克斯为娱乐创作，不代表本人发言或背书。所有答案仅在设备保存，无登录、后端或在线推理。

旧 V10 根入口、`/play/`、V11 五轮预览、V12、V13 与历史交付文件继续保留。本轮发布到 `/v14/`。
