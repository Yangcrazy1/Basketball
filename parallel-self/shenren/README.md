# 世界上另一个我 · V10 回归增强版

手机娱乐网页：英雄联盟综合、篮球梦之队、抽象热梗。恢复 V10 棱彩漫画卡牌和三页穿越序章，在 V11 的 40 人题库与匹配引擎上增量优化；内部发行编号为 12，答题记录 schema 保持 11。

- **直接体验**：https://yangcrazy1.github.io/Basketball/v12/
- **下载、独立 Logo／封面与实际截图**：https://yangcrazy1.github.io/Basketball/v12/review.html
- 40 位启用人物头像均有已核对参考；328 道情境题、156 张海克斯（每人 3 张独占卡）。
- 故事每次打开可重看，大厅默认折叠，顶部常驻“我的穿越故事”。两种配色。
- 自动／自选五人战队，三主题各 48 种搞笑队名组合；换名不改变身份、分数与阵容。支持保存、历史重放与 1080×1920 五人合照 PNG。
- 每人新增穿越来历、宇宙任务、隐藏被动、队友评价；保留原先真实作答证据与人物赠卡的区别。

## 构建与验证

使用 Python 标准库、Node；浏览器检查使用环境已有 Playwright、Pillow 与 Chromium。没有新增运行时依赖。

```sh
python build.py
python tools/build-web.py
python tools/build-xhs.py
node --expose-internals tools/check-xhs.mjs
node --test tests/engine.test.cjs tests/legacy-engine.test.cjs tests/xhs-platform.test.cjs
python tests/browser-check-v12.py
python tools/package-v12.py
```

开发源文件位于 `src/`。`src/legacy/` 是冻结 V10 引擎／数据，用于重放旧记录。不要重跑旧版本一次性数据迁移脚本覆盖当前题库。

## 产物与验证边界

- `release/world-another-me-v12.html`：完整嵌入图片的离线单文件。
- `release/world-another-me-v12-web.zip`：静态网页部署包。
- `release/world-another-me-v12-xhs.zip`：小红书待上传包，根目录 `index.html`。
- `docs/v12-delivery.md`、`docs/v12-build-manifest.json`、`docs/browser-check-v12.json` 与 `docs/xhs-validation-v12.json`：变更、哈希及校验记录。

38 项逻辑／存储测试、16 组浏览器流程通过。截图为手机视口模拟，未冒充实体手机验收。小红书已静态审计与 SDK 契约模拟；**创服平台模拟器、Android 真机扫码、iOS 真机扫码仍待用户验证**；Chrome 61 CSS 与实际设备性能未实测。

`image-sources.json` 记录参考来源、实际字节指纹与漫画对应关系。公开照片参考核对不等于商用授权；漫画人物、标签、剧情和海克斯为娱乐创作，不代表本人发言或背书。所有答案仅在设备保存，无登录、后端或在线推理。

旧 V10 根入口、`/play/`、V11 五轮预览与历史交付文件继续保留。本轮只发布到 `/v12/`。
