# 世界上另一个我 V10

手机网页娱乐测试：英雄联盟（一个综合入口）、篮球梦之队、抽象热梗。

三幕漫画开场、穿越隧道、随机 8/16/24 题、点选自动下一题、身份揭晓、架空背景故事、个人恶搞海克斯、自动/自选五人战队及可下载海报。95 位唯一角色、348 道题、125 张自制海克斯；84 位真人头像已核对照片，1 位原创角色，10 位待核实头像使用清晰标注的文字占位。

- 网页：https://yangcrazy1.github.io/Basketball/?v=10-story
- 下载与单独封面/Logo：https://yangcrazy1.github.io/Basketball/download/?v=10-story
- 小红书待上传包：`release/world-another-me-v10-xhs.zip`
- 功能、头像缺项与小红书校验边界：[`docs/v10-delivery.md`](docs/v10-delivery.md)

构建与验证（Python 标准库；网页流程测试使用环境已有 Playwright）：

```sh
python build.py
node --test tests/engine.test.cjs tests/xhs-platform.test.cjs
python tests/browser-check.py
python tools/build-xhs.py
```

`src/data.json`、`src/engine.js`、`src/app.js` 是主版本；`tools/v10-content.py` 是从 V9 数据的一次性内容升级记录，不应在已升级数据上重复运行。小红书构建使用相同数据与引擎，外置经典脚本和包内资源，采用 `src/xhs-platform.js` 接入公开平台能力。

`image-sources.json` 记录照片来源、哈希和漫画对应关系；原型图片不代表官方或本人背书。人物标签、卡牌效果和 S8 等剧情均为娱乐创作。全部答案仅在当前设备保存，无登录/后端/在线推理。

小红书包已做静态审查和体积审计；**创服平台模拟器、Android、iOS 真机扫码仍待用户验证**，Chrome 61 与实际设备性能尚未实测。
