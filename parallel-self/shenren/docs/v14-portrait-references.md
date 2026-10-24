# 平行宇宙的另一个我 · V14 新增人物头像参考

核对日期：2026-10-24。V14 新增的两名篮球人物采用公开真人照片作身份参考，再生成漫画头像。这里的“已确认”指来源页面、配图和生成头像对应到正确人物，不表示源照片已获得商业再发布授权；照片仅作为创作溯源材料，漫画中的球衣、持球和播客姿态为本作二创设定。

| 人物 ID | 正确人物与公开来源 | 原图文件 | 身份核对结论 |
| --- | --- | --- | --- |
| `draymond-green` | 德雷蒙德·格林／Draymond Green；[Wikipedia 人物页](https://en.wikipedia.org/wiki/Draymond_Green)中的 `Draymond_Green_2022.jpg` | `assets/v14-references/draymond-green.image` | 人物页 infobox 配图；已目视检查短卷发、宽脸、厚胡须等外貌，确认采用 Draymond，未混用 Danny、Jalen 或其他同姓球员。 |
| `ershu` | 恶鼠／张梓祎；[新浪公开篮球报道](https://k.sina.cn/article_6073579234_16a0376e2001020wx0.html)《100多万人围观，“晏鼠组合”很强，但根本打不了退役职业球员》 | `assets/v14-references/ershu.image` | 正文明确写出“恶鼠张梓祎”与百分大战；采用文末单人近照，并与同文开头侧脸照交叉目视核对短脏辫、剃短两侧和棱角脸。未采用同文李青翔、孟铎等其他球员的图片。 |

两张采用原图均已实际下载并目视检查。恶鼠的另一个用户提供来源（Sohu）返回 403，本轮未重试绕过，也未把该页算作图片验证来源。未调用需要登录、验证码或受限接口的资源。

## 原图地址与字节校验

Draymond Green 原图地址：

<https://thumb.wikimedia.org/wikipedia/commons/thumb/9/99/Draymond_Green_2022.jpg/500px-Draymond_Green_2022.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail>

SHA-256：`90cf4a3ad6b665df1da5e453c4939a2b91fbb30dfa74fe1adc030a8ab90b0d3b`。

恶鼠／张梓祎原图地址（来源 HTML 使用 HTTP，此处使用同一公开 CDN 资源的 HTTPS 地址）：

<https://k.sinaimg.cn/n/sinakd20100/540/w640h700/20221129/7770-f25b12c7e5808374198f7fd574ccb04f.jpg/w700d1q75cms.jpg>

SHA-256：`01bbab1acb033f2a2d492b9e47cc9ba0e887ea91b6ace0e3fc16d1b42163440c`。

## 漫画生成与图集映射

新图集：`assets/portraits-v14-new.webp`，1254 × 1254，2 × 2 格。延续 V13 篮球头像的黑色勾线、半色调网点和杏橙／浅紫放射背景；以两张核对原图保留人物辨识度。没有绘制打架、踩踏或受伤场景。

| 本地图集索引 | 单元格 | 内容 | 使用方式 |
| --- | --- | --- | --- |
| 0 | 0（左上） | Draymond Green，蓝金篮球服 | `draymond-green` 默认头像 |
| 0 | 1（右上） | 恶鼠，深灰篮球服 | `ershu` 默认头像 |
| 0 | 2（左下） | Draymond Green，播客麦克风 | 备用，不新增人物 |
| 0 | 3（右下） | 恶鼠，青色球衣与篮球 | 备用，不新增人物 |

漫画原始 PNG 保留于 `/workspace/generated_images/exec-6f30e605-2f9c-4fb9-bbbf-98550fab88b7.png`。输出 WebP 为格式压缩，没有使用程序绘图重建人物。

- 原始 PNG SHA-256：`880235e70d598cf4d53c8807dee094f2eb4410b1a2680485666652d98a4d87d8`。
- WebP SHA-256：`0b48c5b3fba903c6cde09cb7d60e030aaafebbfa4c10fbbdf7a6d4d00a2e2335`。
- 独立补丁：`content/v14-portrait-patch.json`。其中 `sheet: 0` 是补丁本地索引，合并已有图集时须加上旧 `sheets` 长度。补丁同时保留人物、原图地址、原图 SHA、实际下载路径和目视核对说明。

本轮未直接改写旧 `portrait-atlas.json` 或 `image-sources.json`，避免覆盖已有 56 人头像与溯源记录。后续人物故事和专属海克斯属于平行宇宙虚构，不应把生成姿态当成历史现场或真实引语。

## 小红书运行规范核对

按本地 `minitool-zip-builder-1.8.0/references/js-api.md` 基线要求，正常访问[当前公开规范](https://miniapp-sandbox.xiaohongshu.com/minitool/doc)。本轮响应为 HTTP 200、107830 字节，SHA-256 为 `ec9a46746cf6570136e91def7445db9acbeafd132ac2e714fe6ed11b12f3363b`，与 V13 留档完全相同，因此本轮没有新增 API、参数或限额变化。

相对 2026-09-23 的冻结基线，在线文档已有的 AI 文本生成、窗口／位置、短长振动、陀螺仪及关注能力不是 V14 新增；沿用现有 Storage、安全区和临时文件到相册流程即可。抓取结果保存在 `/workspace/scratch/v14-research/xhs-contract-fetch.json` 与同目录 `xhs-doc-current.html`，可复查。
