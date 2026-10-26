# 整活NBA · 本次交付

以娱乐测试为核心，沿用V13紫金漫画风；21位人物、132道题（新增24道球场题）、51张整活海克斯、21条分支故事。自建DIY球星作为自选队友，不篡改测试匹配身份；五人名单和随机队名可生成1080×1920海报。

手机试玩：https://yangcrazy1.github.io/Basketball/nba/?v=nba-1

全部下载、品牌原稿与手机视口截图：https://yangcrazy1.github.io/Basketball/nba/download.html?v=nba-1

7项逻辑及微信API状态模拟测试、10组本地完整浏览器流程、6组真实HTTPS流程通过；小红书目录与ZIP静态审计均81文件、零警告，5个外置脚本通过ES2017解析。微信端已补测“含DIY时保存自选五人／恢复匹配阵容”保持实际名单一致。

微信原生工程包含6页WXML/WXSS/JS，非web-view包装；主包未压缩小于2MiB。工程需微信开发者工具导入并配置真实AppID。开发者工具、Android/iOS微信真机及平台审核仍待验证。

小红书上传包仍需创服平台模拟器完整验证，随后Android和iOS真机扫码验证同一ZIP。普通浏览器或API模拟不替代原生验收；Chrome61 CSS与实机性能未实测。

## 产物

- `zhenghuo-nba-web.zip`：854090 B，SHA256 `5b90ade3f86f92108c5e424e5fbea6213ab98599e737c2637287b35fd8d7cfae`。
- `zhenghuo-nba-xhs.zip`：854608 B，SHA256 `3a207f014ea41f154445fb3811e952d232b1d356a43e996d7137d2f92ebcca81`。
- `zhenghuo-nba-offline.html`：1504800 B，SHA256 `4447aaa17552dc194be83b7c783b7e669192564fdc519a2180de933caab56f1f`。
- `zhenghuo-nba-wechat.zip`：888423 B，SHA256 `4937489c5be9928e937893949a62c478e341b112a343cb3e7b8c8918b0f41d7d`。

源码：`acd14ac9c10254f10837117c996d784237cb79f3`；Pages产物：`ab8c1a05334c1c271ae56d127d2bba08a766ca70`。此次部署只改 `/nba/`，原V13、V14、V15等路径全部保留。

V13原版小红书包：https://yangcrazy1.github.io/Basketball/v13/downloads/world-another-me-v13-xhs.zip ，公开字节SHA仍为 `54929e09e98f85c7c16ed167676cca817e928243084c882edd6613ff1dd648a9`。此前无V13原生微信包，本次提供按最新要求制作的整活NBA微信原生工程。
