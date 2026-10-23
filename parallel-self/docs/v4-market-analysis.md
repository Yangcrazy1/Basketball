# 同类产品逻辑核查与 V4 设计建议

本次实际读取了公开产品页与对应公开 GitHub 仓库；其中有些项目没有开放改作许可，不能统称为可二开的开源项目。下面是产品机制对照，不是市场份额、营收或留存率调查；没有取得的数据不作推测。公开可见也不等于可复制其题库、美术或商业使用其角色数据。

## 五个最有用的参照

| 产品 | 实际核查到的逻辑 | V4 可参考的做法 | 不应照搬或夸大的部分 |
|---|---|---|---|
| [OpenPsychometrics：Statistical “Which Character” Personality Quiz](https://openpsychometrics.org/tests/characters/) | 官方页面说明：双极形容词滑杆形成用户自评，与角色描述向量比较，返回最接近角色；题量可选 Quick 14、Recommended 36、Long 100、Exhaustive 245 等；推荐版中位耗时 185 秒。官方自述用大量志愿者描述形成约 2,000 角色库。 | 首页明确选择题量；题量对应信息覆盖与结果细节；展示多个人物相似度和“像在哪里/不同在哪里”；可把结果做成分享卡。 | 不使用其角色数据；不把我们手工设定的向量说成数百万志愿者验证。官方页标注 CC BY-NC-SA 4.0。 |
| [SBTI 开源实现](https://github.com/pingfanfan/SBTI/blob/21c945b3fe121ad3fc9c64ed256a90e8510c624d/README.md) / [实际产品页](https://pingfanfan.github.io/SBTI/) | 15 维度、每维 2 题、L/M/H 分级，按曼哈顿距离与类型模板排序；独立题库/人格/配置；结果含雷达图与分享图片；特殊类型和彩蛋可覆盖正常结果。 | 对应人群有辨识度的人格命名；数据和引擎分开；本地完成一次测试后可立即导出图片；分数必须能解释。 | “科学匹配”是其 README 的宣传，不是有效性证据；不要用随机彩蛋覆盖正经主结果；原引擎距离分母写死 30，变更维数不能直接照抄。原测试内容的授权需另核查。 |
| [CBTI](https://github.com/liyupi/cbti-test/blob/b193031710b5ff16d3c671577a8371aeb5a012a3/README.md) / [实际产品页](https://cbti.codefather.cn) | 明确面向程序员：30 题、5 模型/15 子维度、27 普通人格+1 隐藏人格；SUDO、NULL 等圈层名称搭配人物图、段子描述、分享文案；静态导出、纯前端计分。源码结果页有可复制分享文字、PNG 下载、角色图与雷达图。 | 用用户熟悉的网络语境建立共鸣；人格名字要易记、能拿来聊天；一张结果卡交代主型、角色、代表句、维度和再次测试入口。 | 未找到明确 LICENSE，不能因公开就复制代码、美术或原段子。只参考产品组织方式。 |
| [CosmosPersona](https://github.com/IseeJ/CosmosPersona/blob/5843faa05bb7e5b91f29efc46369358d26bfa516/README.md) / [实际产品页](https://iseej.github.io/CosmosPersona/) | 实际 `finalscript.js` 是 12 段连续荒诞剧情：公交车、失重、机器人、猫、吸尘器；二选一选项给不同人格轴计分，最后映射到结果角色。题目通过剧情场景表达偏好，而不是直问“你是否外向”。 | V4 的“抽象”应来自具体但荒诞的场景、连贯章节和有画面的选择；每题要真的在测一种偏好，而不是只有随机搞笑。 | README 明确限制改作/分发/商用，不复制题目、美术、叙事；原创编写新的荒诞场景。 |
| [PMD Quiz Online](https://github.com/Nrosa01/pmd-quiz-online/blob/f1a4a45c73577b139484525239d5e6dddfe0c005/README.md) | 实际 README 列出 64 个原版题目、性格描述、Normal Quiz/Full Quiz 两模式、多语言、雷达图和响应式界面。 | 短版用于低门槛体验，完整版增加覆盖；角色测试的氛围和结果可收藏性同样重要；进入测试前说清题量。 | 代码 CC0 与游戏素材版权是两回事；不使用 Nintendo/Creatures 的图片、音效、音乐或原题。 |

补充的解释透明性参照：[BigFive 官方页](https://bigfive-test.com) 与 [仓库](https://github.com/rubynor/bigfive-web/blob/e8f3caca49edafb9bc6b927eff7fbc1264312c24/README.md)。官方页明确 120 题、约 10 分钟、5 大特质和 30 个 facets，强调无优劣与无需账号；README 公开 IPIP 题项来源。V4 可以参考“维度与子维度分别解释、不给高分贴好坏标签”，不能借用其研究基础给原创搞笑题背书。

## 开源选型与当前维护核查

**核查日期：2026-10-23，时间统一为 UTC。** 本轮对以下五个仓库逐一请求 GitHub REST API 的仓库元数据和默认分支最近 20 条提交，十个请求均为 HTTP 200；另外读取了根目录、构建配置和 BigFive 的 `web/README.md`。维护判断结合实际提交时间、提交内容与间隔；`pushed_at`、`updated_at`、未归档、官网可访问或 Star 数都不能单独证明持续维护。以下部署难度来自配置和文档核查，未声称在本轮把五个上游项目各自重新安装部署过。

| 仓库与选型结论 | 部署难度与运行方式 | 可以复用什么 | 许可与边界 | 截至核查日的维护判断 |
|---|---|---|---|---|
| [pingfanfan/SBTI](https://github.com/pingfanfan/SBTI)：**二开备选首选**，不直接换皮上线 | **低**：原生 JS + Vite；`npm install`、`npm run build` 后托管 `dist/`，无业务后端。多文件构建物需额外打包才适合单机下载。 | 数据与引擎分离、向量距离匹配、题目流程、Canvas 雷达、结果图片下载、CSS 变量主题。8/16/24 题和新维度需重写计分约束。 | 代码 **MIT**；保留许可与版权声明。README 说明测试改编自其他创作者，其原题和人格内容的权利不因代码 MIT 自动解决；本项目应使用原创题库与画像。 | **首发后未见持续维护证据**：默认分支仅返回 2 条提交，均在 2026-04-09；之后约 6 个月无默认分支新提交，未归档。 |
| [liyupi/cbti-test](https://github.com/liyupi/cbti-test)：**只作产品参照**，取得许可前不复制 | **低到中**：Next.js 16 / React 19；已配置 `output: "export"`，构建为 `out/`，可静态托管，无业务后端。框架构建比纯 JS 更重。 | 可参考圈层命名、人格图鉴、分享文案、PNG/雷达的产品组织；代码、美术和文案复用须先确认许可。 | GitHub API `license=null`；本轮根目录、README 未发现明确 LICENSE。**公开源码不等于已授权二开**。 | **单次发布，未见持续维护证据**：默认分支只返回 1 条提交（2026-04-13）；未归档。 |
| [IseeJ/CosmosPersona](https://github.com/IseeJ/CosmosPersona)：**参考叙事，自建实现** | **技术上低**：普通 HTML/CSS/JS 和本地资源，可静态托管；但技术可部署不表示获得再分发许可。 | 只借鉴“连续荒诞剧情 → 行为选择 → 角色结果”的通用思路；重新编题、画图和写代码。 | README **All Rights Reserved**，明确禁止改作、再分发和商用；仅允许带署名的个人使用代码。GitHub API 无开源 license。 | **历史有迭代，当前低频**：最近 20 条提交覆盖 2025-02 至 2026-02，2026 年主要为版权说明、页脚与样式；2026-02-10 后约 8 个月无新提交，未归档。 |
| [Nrosa01/pmd-quiz-online](https://github.com/Nrosa01/pmd-quiz-online)：**可抽取通用逻辑，不选作整站底座** | **中**：Svelte 3 + Vite 3 + Tailwind；构建后为静态站，但依赖年代较早，正式发布前需兼容和依赖检查。 | 在 CC0 范围内复用题库加载结构、长短模式、计分组织、多语言和雷达组件；替换所有游戏素材与题目。 | **代码 CC0-1.0**；README 明确游戏图片、声音、音乐归 Nintendo / Creatures。代码许可不能覆盖这些素材。 | **历史有维护，当前停更较久**：最新是 2025-05 的构建/德语题库调整；再往前为 2023-08，距核查日约 17 个月无提交，未归档。 |
| [rubynor/bigfive-web](https://github.com/rubynor/bigfive-web)：**可研究模块，不选作轻量娱乐 MVP 底座** | **中到高**：Next.js 应用，包含题库/计分/结果 packages；`web` 文档要求 MongoDB 保存结果，提供 Docker Compose 和数据库环境配置，不是开箱即用的单文件离线站。 | MIT 范围内的计分、国际化、维度与子维度结果呈现；如需要严肃量表，应另核查题项、译文和适用范围。 | 仓库 **MIT**；IPIP 量表与翻译仍需追溯各自来源，不能把其研究依据转移给新编娱乐题。 | **有近期文档活动，不能判为持续功能维护**：2026-09-01 仅增加 README 外链；前一次默认分支提交为 2024-04-26 的 v2 导入，期间没有新的默认分支功能提交证据，未归档。 |

以下是本轮 API 返回的精确状态，SHA 链接固定到所核查的最后提交；并非沿用旧工作区快照：

| 仓库 / 默认分支 | `pushed_at` | `archived` | 最新提交 `committer.date` | 最新提交完整 SHA |
|---|---|---|---|---|
| pingfanfan/SBTI / main | 2026-04-09T23:31:23Z | false | 2026-04-09T23:31:04Z | [21c945b3fe121ad3fc9c64ed256a90e8510c624d](https://github.com/pingfanfan/SBTI/commit/21c945b3fe121ad3fc9c64ed256a90e8510c624d) |
| liyupi/cbti-test / main | 2026-04-13T03:13:54Z | false | 2026-04-13T03:13:04Z | [b193031710b5ff16d3c671577a8371aeb5a012a3](https://github.com/liyupi/cbti-test/commit/b193031710b5ff16d3c671577a8371aeb5a012a3) |
| IseeJ/CosmosPersona / main | 2026-02-10T05:01:08Z | false | 2026-02-10T05:01:08Z | [5843faa05bb7e5b91f29efc46369358d26bfa516](https://github.com/IseeJ/CosmosPersona/commit/5843faa05bb7e5b91f29efc46369358d26bfa516) |
| Nrosa01/pmd-quiz-online / main | 2025-05-17T19:27:08Z | false | 2025-05-17T19:27:04Z | [f1a4a45c73577b139484525239d5e6dddfe0c005](https://github.com/Nrosa01/pmd-quiz-online/commit/f1a4a45c73577b139484525239d5e6dddfe0c005) |
| rubynor/bigfive-web / master | 2026-09-01T09:52:55Z | false | 2026-09-01T09:52:55Z | [e8f3caca49edafb9bc6b927eff7fbc1264312c24](https://github.com/rubynor/bigfive-web/commit/e8f3caca49edafb9bc6b927eff7fbc1264312c24) |

可复核的仓库元数据 API：[SBTI](https://api.github.com/repos/pingfanfan/SBTI)、[CBTI](https://api.github.com/repos/liyupi/cbti-test)、[CosmosPersona](https://api.github.com/repos/IseeJ/CosmosPersona)、[PMD](https://api.github.com/repos/Nrosa01/pmd-quiz-online)、[BigFive](https://api.github.com/repos/rubynor/bigfive-web)。各仓库地址后加 `/commits?per_page=20` 可查看本轮使用的默认分支提交列表；API 内容会随仓库未来更新。维护判断只覆盖公开默认分支，不推断作者私有开发或未合并分支。

**最终选择：轻量自建业务核心，按许可复用少量通用模块。** 直接使用现有整站不能同时满足原创抽象题、8/16/24 深度档、跨圈层角色匹配和手机离线交付；完整二开会受到原计分维数、题量、框架及素材许可牵制。若必须从一个上游整站起步，选 SBTI 并替换题库与匹配引擎。当前更短的路径是保留简单前端壳，自建六维计分、人格细分与角色数据，把离线文件和手机安装包装作独立交付目标；后续微信小程序只复用数据和不依赖 DOM 的计分逻辑，界面与平台能力按小程序重做。

最小 MVP 为：两种配色、8/16/24 题入口、原创题库、六维画像、角色 Top 3 与差异解释、结果图导出和本地答题进度；首版不依赖账号、数据库或在线 AI。角色向量属于编辑设定，匹配数值只表示本测试内的距离，不宣称心理学准确率。OpenPsychometrics 是产品机制参照，本轮没有找到并核验与其官网相对应的可复用仓库，因此不编造它的 GitHub 维护或代码许可状态。

## 本次产品重做建议

1. **题目抽象，但行为含义要清楚。** 用原创的荒诞小场景，例如“电梯给你发了 offer”“群聊里出现会报销的鸭子”等；四个答案都是可想象的动作，不做从 A 到 D 由低到高的明显量表排列。每项可以有多维权重，降低用户刻意挑最高分答案的机会。
2. **8/16/24 是深度档，不是准确率。** 首页显示大致时间、会解锁的内容。短版给方向性画像和候选角色；长版扩大情境覆盖、细分或修正结果，同时解释哪些答案产生变化。不得写“8 题准确率 80%、24 题 99%”之类未经验证数字。
3. **结果不只给一个名字。** 主人格、次人格或候选侧面、六维坐标、最接近的角色 Top 3、接近的两维、不同的一维、原创平行人生共同组成结果。
4. **人物图要有真正的出处。** “按真实名场面卡通化”和“原创示意头像”要分区/分标识。只有实际获得并核对人物/画面的图片才能进入前一类；每张保留来源 URL、场景说明、卡通生成关系和授权状态，未知的就明确未知。不将普通肖像写成名场面，也不凭想象编造人物名台词。
5. **分享闭环离线可完成。** 一键生成本地图片，长按保存/下载/系统分享各自做好降级。分享卡可有角色名、卡通图、主型与次型、代表句和测试档位，不放尚未存在的二维码或网址。
6. **交付格式是产品的一部分。** 单机 HTML 在聊天预览器和部分手机文件预览器中可能不执行脚本；APK、正式托管链接、单文件离线版应分别说明可用范围。只有实际安装/加载验证过的路径可以写“已验证”，不能把云端绝对路径写成手机网址。

## 证据文件

- 各仓库固定 SHA 和 README 快照位于研究工作区的 `market/<owner>__<repo>/`。
- 公开产品页 HTML 快照位于 `market/https_*.html`。
- OpenPsychometrics 页面快照位于 `openpsychometrics-characters.html`。
- 网络素材与单张 provenance 位于 `refs/`；实际参考图核查与商业授权核查是两件事。

## 本版图片的实际交付状态

本版展示已核查的真实参考原图，不是把这些原图重新画成卡通。8 位参考人物为虎哥、刀哥、户晨风、詹姆斯、成龙、姚明、孙笑川、葛优：

- 虎哥、刀哥、詹姆斯、成龙、葛优：对应明确出处的名场面原图。刀哥位于好果汁同框图左侧，图中同时包含虎哥，不能将右侧人物当成刀哥。
- 户晨风、孙笑川：普通肖像/模板肖像，不能说成已核实的特定名场面。
- 姚明：参考文件已经是网上流传的笑脸线稿表情，并非原始照片，也不是本版新画的卡通。
- 峰哥、美国讲师、大司马等其余旧角色：保留之前的原创示意头像，没有伪造真实照片来源。

原始参考图已按角色 ID、原文件扩展名原样复制至 `src/assets/meme-references/`；没有裁剪、改色、卡通化或其他图片编辑。每张的原始 URL、身份依据、尺寸、SHA256 和权利状态见 `v4-image-sources.json`。数据中的 `cartoonGenerated` 明确为 false。

户晨风 Commons 文件采用 Copyrighted free use 模板；其余图片的独立商业使用/改作授权尚未确认。公开网页能访问，不能据此声称已取得商业授权。本版参考展示也不代表任何人物、片方或平台背书。真实名场面卡通重绘仍未完成，不能对外把这些原图标作已卡通化。
