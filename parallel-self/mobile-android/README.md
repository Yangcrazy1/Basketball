# Android 离线安装包封装

此目录把最终的单文件 HTML 包进 Android WebView。它解决手机浏览器/文件管理器对本地 HTML 脚本执行方式不一致的问题；APK 能否从当前聊天下载、设备能否允许安装，仍需要独立确认，不能由编译成功推断。

## 当前能力与边界

- Android 8.0 / API 26 及以上；应用名「另一个我」，版本 4.0.0。
- 不声明 INTERNET、相册读取或存储写入权限。页面只从 `file:///android_asset/index.html` 读取，HTTP/HTTPS 子请求拦截为离线错误。
- 用户明确点击的 HTTPS 出处（目前白名单：Commons、Imgflip、萌娘百科和 GitHub）交给系统浏览器，支持 target="_blank"；应用 WebView 自身仍不联网。其他 scheme、陌生 host、userinfo 和非标准端口均拒绝。
- 本地存储由系统 WebView 保存。Android System WebView / Chrome 必须支持页面所用现代 JavaScript；不是所有旧 Android 8 设备都自带足够新的网页组件。
- 首启会检查最终 HTML 的 `data-app-ready` 标记。初始化、主页面加载、JS 未完成启动或渲染进程退出时，给出原生错误与组件版本诊断、重试入口，不以空白页作为最终状态。
- PNG 下载使用系统“创建文档”界面，让用户选择文件位置，不申请广泛存储权限。待保存 PNG 放在私有缓存并记录状态，文件选择期间进程被回收后可重新读取。
- PNG 分享通过只读、逐 URI 授权的 ContentProvider 交给系统分享器；原始答题数据不发送。
- 最终 HTML 保持 `a[download]`、`.poster-img`、`[data-action=share-poster]` 标记即可接入保存/分享，无需改网页原有逻辑。
- 本目录没有第三方 Android 运行时框架，不依赖 Gradle、AndroidX 或远程 CDN。

**未完成的验收**：当前环境没有 Android SDK/模拟器预装，没有 `/dev/kvm`，也没有连接真机。已编译、签名、权限与 APK 结构检查不等同于已安装启动或手机保存/分享验收。最终 HTML 必须重新打包后测试；不能把打包旧 HTML 的结构验证产物当作 V4 成品。

## 工具与构建

Linux x86_64、Java 17+、Python 3.9+。脚本默认将官方工具安装到 `/workspace/scratch/android-delivery`，可通过 `PARALLEL_ANDROID_TOOLS` 指定其他目录。

```bash
cd /workspace/Basketball/parallel-self/mobile-android
python3 prepare-toolchain.py
./build-apk.sh ../dist/parallel-self.html ../dist/parallel-self-android.apk
```

工具固定为 Android SDK Platform 35 revision 2、Build Tools 35.0.0 和 Eclipse ECJ 3.42.0。下载经过现有 HTTPS 代理，保留 TLS 校验，按 Google SDK 元数据和 Maven Central 公布的 SHA-1 校验值验证；记录实际 SHA-256。官方来源与结果写入工具目录 `toolchain-verification.json`。不修改校验值绕过失败。

最终 HTML 在成功完成初始化后必须设置：

```javascript
document.documentElement.dataset.appReady = 'true';
```

构建脚本拒绝没有该标记契约的 HTML。启动检查约 5.5 秒内等待页面初始化；若需要较久的异步启动，可调整原生等待条件并再次验收。

首次构建自动生成本地测试签名密钥，保存在工具目录，不包含在源码包中。默认密码 `android` 仅是本地测试用途；正式发布应使用自己保管的签名密钥，通过 `PARALLEL_ANDROID_KEYSTORE` 选择。不要将测试签名密钥当成正式发行凭据。

构建输出包括 `apksigner verify --verbose --print-certs`、`zipalign -c`、`aapt dump badging`。还应检查最终 APK 内 `assets/index.html` 与选定文件逐字节一致，以及没有权限项。

## 手机安装

APK 是 Android 安装文件，不是 iPhone 安装包。手机需实际下载到文件，然后由系统安装器打开；系统可能要求用户允许当前下载来源安装应用，企业管控/设备策略也可能阻止。不能承诺绕过这些系统要求，也不能把一个云工作区文件路径当作已经公开可下载的网址。

本版使用现有 GitHub 仓库的独立测试分支提供实际文件下载，入口见 `../releases/v4/README.md`；公开 HTTPS 文件检查见同目录 `download-verification.json`。这些检查与手机安装验收分开报告，没有将聊天附件导出通道视为已验证。
