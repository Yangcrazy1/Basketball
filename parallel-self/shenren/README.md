# 平行宇宙的另一个我 · V13 镜面宇宙版

手机娱乐网页：英雄联盟综合、篮球梦之队、抽象热梗。三页漫画引导穿越，随机 8／16／24 道情境题，按真实作答生成平行身份、恶搞海克斯和五人战队。发行编号 13，新答题记录 schema 为 12。

- **直接体验**：https://yangcrazy1.github.io/Basketball/v13/
- **下载、独立 Logo／封面与实际截图**：https://yangcrazy1.github.io/Basketball/v13/review.html
- 57 位启用人物头像均有已核对参考；428 道情境题、207 张海克斯（每人 3 张独占卡）。新增／恢复 17 位人物。
- 新 Logo、镜面双宇宙封面、三幕序章、三主题简洁背景；身份过场的大头像占画面约三分之二。
- 故事每次打开可重看，大厅默认折叠，顶部常驻“我的穿越故事”。两种配色。
- 自动／自选五人战队，三主题各 48 种搞笑队名组合；换名不改变身份、分数与阵容。支持保存、历史重放与 1080×1920 五人合照 PNG。
- 每人都有穿越来历、宇宙任务、隐藏被动、队友评价；保留真实作答证据与人物赠卡的区别。
- 热门人物在答案相近时有更高优先级；原始匹配分不被加分覆盖，每位启用人物均有合法作答可匹配到。

## 构建与验证

使用 Python、Node 与已有 Pillow 压缩图片；浏览器检查使用环境已有 Playwright 与 Chromium。运行页面无第三方在线依赖。

```sh
python build.py
python tools/build-web.py
python tools/build-xhs.py
node --expose-internals tools/check-xhs.mjs
node --test tests/engine.test.cjs tests/legacy-engine.test.cjs tests/xhs-platform.test.cjs tests/v13-content.test.cjs tests/v13-priority-history.test.cjs
python tests/browser-check-v13.py
python tools/package-v13.py
```

开发源文件位于 `src/`。`src/legacy/` 冻结 schema 10，`src/legacy-v11/` 冻结 schema 11；历史记录使用对应冻结引擎重放，保留旧身份、阵容与队名。不要重跑旧版本一次性数据迁移脚本覆盖当前题库。

## 产物与验证边界

- `release/world-another-me-v13.html`：完整嵌入图片的离线单文件。
- `release/world-another-me-v13-web.zip`：静态网页部署包。
- `release/world-another-me-v13-xhs.zip`：小红书待上传包，根目录 `index.html`。
- `docs/v13-delivery.md`、`docs/v13-build-manifest.json`、`docs/browser-check-v13.json`、`docs/v13-unit-check.json` 与 `docs/xhs-validation-v13.json`：变更、哈希及校验记录。

实际测试统计以本轮记录为准。截图为手机视口模拟，未冒充实体手机验收。小红书静态审计与 SDK 契约模拟不代表原生验收；**创服平台模拟器、Android 真机扫码、iOS 真机扫码仍待用户验证**；Chrome 61 CSS 与实际设备性能未实测。

`image-sources.json` 与 `docs/v13-portrait-references.md` 记录参考来源、实际字节指纹与漫画对应关系。尼达、伊利采用核对过的官方公开头像；头像归属核对不等于全部真人面部独立核验。王思聪热狗姿势为原创新绘。公开照片参考核对不等于商用授权；漫画人物、标签、剧情和海克斯为娱乐创作，不代表本人发言或背书。所有答案仅在设备保存，无登录、后端或在线推理。

旧 V10 根入口、`/play/`、V11 五轮预览、V12 与历史交付文件继续保留。本轮发布到 `/v13/`。
