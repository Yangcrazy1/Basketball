# 整活NBA

以娱乐测试为核心的篮球独立版本。沿用 V13 的紫金宇宙与漫画卡片风格，保留现有篮球内容；球场是测试情境，DIY 是测试结果的延伸玩法。

- 21 位篮球圈人物、132 道随机题（原108道＋24道新球场题）、51 张整活海克斯、21 条六幕分支故事。
- 8／16／24 题可选，选择后自动下一题，可返回改选、恢复草稿和查看真实答案依据。
- 原有计分引擎保持不变，匹配身份、原始分数与队伍修改分开保存。
- 自选五人阵容、随机离谱队名；DIY 名字、号码、口头禅、六维能力与专属海克斯，可邀请进五人团。DIY 不进入默认测试身份池。
- 实际阵容和故事可以生成1080×1920 PNG；本机保存，无账号、后端和在线推理。

## 交付

手机网页：https://yangcrazy1.github.io/Basketball/nba/

下载与实际截图：https://yangcrazy1.github.io/Basketball/nba/download.html

- `release/zhenghuo-nba-wechat.zip`：WXML／WXSS／JS 原生微信小程序工程，解压后用微信开发者工具导入。占位 AppID 需替换为自己的正式 AppID；不是聊天中点击安装的文件。
- `release/zhenghuo-nba-xhs.zip`：整活NBA小红书静态上传包。
- `release/zhenghuo-nba-web.zip`：静态网页部署包。
- `release/zhenghuo-nba-offline.html`：完整离线网页，交给支持脚本的浏览器打开；手机优先使用 HTTPS 网页。

原始 V13 小红书包保持不变：https://yangcrazy1.github.io/Basketball/v13/downloads/world-another-me-v13-xhs.zip 。此前没有 V13 原生微信包；本次微信工程是按最新要求制作的篮球独立版本。

## 构建

```sh
python scripts/extract-content.py
python scripts/build.py
python scripts/build-wechat.py
node --test tests/game.test.cjs tests/wechat-structure.test.cjs
python tests/browser-check.py
python scripts/package.py
```

`shared/game.js` 为网页、微信共用的纯逻辑适配；`content/engine.js` 与原3493200提交字节相同。头像和海克斯从原图集按已有映射做技术裁剪，未重新猜测人物；来源与资源指纹见 `docs/portrait-sources.json`、`content/content-manifest.json`。

用户提供的另一个对话 ID 不能直接读取，仓库中球场页面返回403；用户已选择用“球场场景题＋DIY自建整活球星”落地，未声称复制了不可访问页面。

## 已完成验证

7项逻辑／微信API状态模拟、10组本地浏览器、6组公开HTTPS流程通过。大小、指纹及交付入口见 `docs/build-manifest.json`、`docs/delivery.md`；真实线上结果见 `docs/public-check.json`。

## 验证边界

普通浏览器截图是手机视口模拟。原生微信工程通过静态与 API 状态模拟不等于开发者工具或真机验收，仍待正式 AppID、开发者工具编译及 Android／iOS 微信真机验证。

小红书 ZIP 仍须上传创服平台，先完成平台模拟器完整功能验证，再分别用 Android 与 iOS 真机扫码验证相同产物；Chrome61 CSS 与真实设备性能未实测。未代用户登录平台、上传审核或申请相册权限。
