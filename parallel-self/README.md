> 最新网页为 [V9「世界上另一个我」三大梗宇宙](shenren/README.md)，英雄联盟综合、金闪闪队NBA、抽象热梗三个板块，300道题、68张自制海克斯，点选后自动下一题。手机直达 https://yangcrazy1.github.io/Basketball/?v=9-worlds 。以下是保留的 V4 说明。



# 另一个我 · ELSEWHERE V4

一个可离线运行的平行身份娱乐测试。24 道原创荒诞情境题、74 位角色、五个世界，提供安卓安装包和单文件网页。将数据、纯 JavaScript 计分与页面分开，方便以后迁移微信小程序。

## 手机使用

针对当前截图中的安卓手机，优先使用 **APK**：下载完成后由系统安装器打开，安装后从桌面「另一个我」进入。首次安装可能需要系统允许浏览器安装应用；APK 适用于 Android 8 及以上，并要求较新的 Android System WebView / Chrome。iPhone 不能安装 APK。

最终文件位于 [`releases/v4/`](releases/v4/)。下载入口和真实 HTTPS 文件校验结果见该目录 README。单文件 HTML 作为备用：部分聊天或文件预览器不执行 JavaScript，因此不能保证点击所有预览入口都能运行。没有把工作区绝对路径当作公开网址。

## 这版能做什么

- 星雾紫 / 森屿青，两套漫画手账风界面，适配手机和桌面。
- 「真实反应 / 理想人设」两种答题视角，分开记录。
- 8 / 16 / 24 题：主角风格、做事子型、出场分支逐层展开；短版补答保留答案，新增证据允许修正初判。
- 「鸽子公司入职」「电饭煲突然破防」「改造月亮」等原创情境。四个选项打散分值，部分题提供 0.3 权重副维信息。
- 精神股东、反差番外、平行搭子、六维地图、逐条选择证据、场景反差，以及五类角色匹配和可搜索图鉴。
- 回看并修改单题后重算；断点续答；最近 12 次档案；收藏角色；本地清除记录。
- 离线生成 1080×1760 PNG 身份卡。安卓封装接入系统保存位置和分享界面，不申请相册或存储权限。

题库和人物向量是娱乐性内容规则，接近分不是心理准确率，不能推断真人心理。真实反应和理想人设共用规则，差别来自用户按不同视角选择的答案。

## 人物图片的准确范围

本版实际展示 8 位人物的真实来源参考图：虎哥、刀哥、户晨风、詹姆斯、成龙、姚明、孙笑川、葛优。原图、肖像、网上线稿分别标记，可点击查看出处；照片保持原样，没有把普通肖像称为名场面。

**按真实照片重绘公众人物卡通未完成**：图像服务拒绝了这项生成请求。本版没有用想象图冒充重绘。峰哥、美国讲师、大司马等保留原创示意头像；其余角色使用原创通用头像，不能当成官方人物美术。旧原创图集不是依据本轮真实照片重绘。

来源与授权状态见 [`docs/v4-image-sources.json`](docs/v4-image-sources.json)。公开可见不等于已取得商用授权，商用图片授权尚未全部确认。此版本用于原型体验，不能据此认为素材已获商业发行许可。

## 最快的选型与 MVP

结论：**复用成熟的流程和存储模块，自己维护原创题库、匹配引擎与表现层**。没有发现可直接换名就满足本需求、同时授权清楚的完整项目。为这次单机验证引入后台、登录或 AI API 没有必要。

当前实际复用了 [sbti-weapp](https://github.com/HalfSweetLemon/sbti-weapp) 的 MIT 存储模块，保留原实现与 [`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt)。SBTI、CBTI、CosmosPersona、OpenPsychometrics 等用于机制对照，没有复制它们的原题、美术或段子。维护情况、许可证、部署难度和可复用功能见 [`docs/v4-market-analysis.md`](docs/v4-market-analysis.md)；早期九个项目的取证记录见 [`docs/选型与MVP.md`](docs/选型与MVP.md)。

最简单的微信 MVP 仍是：首页选档 → 原创情境答题 → 人格与角色结果 → 本地图片分享。沿用 `src/data.json` 和 `src/engine.js`，以 `wx` 适配存储，重做 WXML/WXSS 与微信 Canvas。当前交付不是可直接上传的原生微信小程序；AppID、开发者工具与微信真机验收留到实际接入时完成。

## 构建与验证

网页构建只用 Python 3 标准库；Node 18+ 运行引擎测试。

```bash
python3 build.py
node --test tests/engine.test.cjs
python3 tests/v4-browser-check.py
```

浏览器检查需要 Playwright、Pillow 和 Chromium（测试脚本默认 `/usr/bin/chromium`），自动使用随机本地 HTTP 端口。禁网检查使用完整 HTML 在 `about:blank` 渲染，因为云浏览器策略禁止 `file://` 导航。不能把这些检查写成手机本地文件验收。

安卓构建与签名说明见 [`mobile-android/README.md`](mobile-android/README.md)。SDK 与测试签名密钥放在工程外，不随源码分发；打包时验证内置 HTML 与本次受测文件一致。应用不声明 INTERNET 或存储权限；只有用户主动点击出处才通过系统浏览器打开链接。

可复现结果见 [`docs/v4-browser-check-results.json`](docs/v4-browser-check-results.json) 与 [`mobile-android/structural-validation.json`](mobile-android/structural-validation.json)。已做引擎、浏览器、APK 编译/签名/结构检查；没有连接手机或运行安卓模拟器，不能声称做过真机安装、启动或系统保存验收。

所有答案仅保存在设备本地。V4 使用独立 `elsewhere.v4` 存储区，不迁移或覆盖旧版记录。
