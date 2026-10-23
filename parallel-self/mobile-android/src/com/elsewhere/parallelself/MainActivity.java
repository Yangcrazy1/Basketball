package com.elsewhere.parallelself;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.ConsoleMessage;
import android.webkit.WebResourceError;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import android.widget.FrameLayout;
import android.view.ViewGroup;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.UUID;

/** Offline wrapper. The only executable document is the packaged asset. */
public final class MainActivity extends Activity {
    private static final String START = "file:///android_asset/index.html";
    private static final int CREATE_IMAGE = 1701;
    private static final int MAX_BASE64 = 16 * 1024 * 1024;
    private final Handler main = new Handler(Looper.getMainLooper());
    private WebView web;
    private String pendingImageFile;
    private String pendingName;
    private StringBuilder imageChunks;
    private String imageAction;
    private boolean imageBusy;
    private boolean startupErrorVisible;
    private String lastConsoleError = "";
    private int loadAttempt;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (state != null) {
            String restored = state.getString("pendingImageFile");
            if (restored != null && restored.matches("[a-f0-9]{32}\\.png")) { pendingImageFile = restored; imageBusy = true; }
        }
        getWindow().setStatusBarColor(Color.rgb(255,249,239));
        getWindow().setNavigationBarColor(Color.rgb(255,249,239));
        try { web = new WebView(this); }
        catch (RuntimeException e) { showStartupError("系统网页组件未能初始化。", e.getClass().getSimpleName()); return; }
        FrameLayout frame = new FrameLayout(this);
        frame.setBackgroundColor(Color.rgb(255,249,239));
        frame.addView(web,new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT));
        frame.setOnApplyWindowInsetsListener((view,insets)->{
            view.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        setContentView(frame);
        WebView.setWebContentsDebuggingEnabled(false);
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setBlockNetworkLoads(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setSupportMultipleWindows(false);
        web.addJavascriptInterface(new ImageBridge(), "NativeFiles");
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onConsoleMessage(ConsoleMessage message) {
                if (message.messageLevel() == ConsoleMessage.MessageLevel.ERROR) {
                    String text = message.message();
                    lastConsoleError = (text.length() > 220 ? text.substring(0,220) : text) + " (line " + message.lineNumber() + ")";
                }
                return true;
            }
        });
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (url.equals(START) || url.startsWith(START + "#") || url.startsWith("about:blank")) return false;
                if (request.isForMainFrame() && request.hasGesture() && SourceLinks.validatedHttps(url) != null) openExternalSource(url);
                else show("只能通过来源按钮打开已核查的 HTTPS 出处。");
                return true;
            }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                String scheme = request.getUrl().getScheme();
                if ("http".equals(scheme) || "https".equals(scheme))
                    return new WebResourceResponse("text/plain", "utf-8", 403, "Offline only", java.util.Collections.<String,String>emptyMap(), new ByteArrayInputStream(new byte[0]));
                return null;
            }
            @Override public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                loadAttempt++; startupErrorVisible = false; lastConsoleError = "";
            }
            @Override public void onPageFinished(WebView view, String url) {
                if (START.equals(url)) {
                    view.evaluateJavascript(BRIDGE_SCRIPT, null);
                    checkPageReady(loadAttempt, 0);
                }
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) showStartupError("应用内置页面未能载入。", String.valueOf(error.getDescription()));
            }
            @Override public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
                showStartupError("系统网页组件停止了运行。", detail.didCrash() ? "WebView renderer crashed" : "WebView renderer exited");
                return true;
            }
        });
        web.setDownloadListener((url, agent, disposition, type, length) -> show("请使用结果卡里的下载按钮保存图片。"));
        if (state == null || web.restoreState(state) == null) web.loadUrl(START);
    }

    private void checkPageReady(final int attempt, final int poll) {
        main.postDelayed(() -> {
            if (isFinishing() || isDestroyed() || web == null || attempt != loadAttempt || startupErrorVisible) return;
            web.evaluateJavascript("document.documentElement.getAttribute('data-app-ready') === 'true'", value -> {
                if ("true".equals(value)) return;
                if (poll < 3) checkPageReady(attempt, poll+1);
                else showStartupError("页面已载入，但没有完成启动。", lastConsoleError.isEmpty() ? "appReady was not set" : lastConsoleError);
            });
        }, poll == 0 ? 1000L : 1500L);
    }
    private void showStartupError(final String summary, final String detail) {
        main.post(() -> {
            if (isFinishing() || isDestroyed() || startupErrorVisible) return;
            startupErrorVisible = true;
            String provider = "unavailable";
            try { android.content.pm.PackageInfo info = WebView.getCurrentWebViewPackage(); if (info != null) provider = info.packageName + " " + info.versionName; }
            catch (RuntimeException ignored) { }
            final String diagnostics = "应用：4.0.0 / Android " + android.os.Build.VERSION.RELEASE + "\n网页组件：" + provider + "\n诊断：" + detail;
            new AlertDialog.Builder(this).setTitle("页面未能启动")
                .setMessage(summary + "\n\n这是离线应用，无需联网打开。可先重试；仍未恢复时，请更新 Android System WebView / Chrome 后重试。")
                .setPositiveButton("重试",(dialog,which)->recreate())
                .setNeutralButton("查看诊断",(dialog,which)->new AlertDialog.Builder(this).setTitle("启动诊断").setMessage(diagnostics).setPositiveButton("知道了",(d,w)->recreate()).setNegativeButton("退出",(d,w)->finish()).show())
                .setNegativeButton("退出",(dialog,which)->finish()).show();
        });
    }

    private static final String BRIDGE_SCRIPT =
        "(function(){if(window.__nativeImageBridge)return;window.__nativeImageBridge=true;"+
        "function send(src,name,kind){if(!/^data:image\\/png;base64,/.test(src))return;"+
        "var b=src.substring(src.indexOf(',')+1);if(b.length>16777216){alert('图片过大，请截图保存');return;}"+
        "NativeFiles.beginImage(name,kind);for(var i=0;i<b.length;i+=32768)NativeFiles.appendImageChunk(b.substring(i,i+32768));NativeFiles.finishImage();}"+
        "document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('a[href],[data-action=share-poster]');if(!t)return;"+
        "var src=t.tagName==='A'?t.href:(document.querySelector('.poster-img')||{}).src;"+
        "if(src&&src.indexOf('data:image/png;base64,')===0){e.preventDefault();e.stopImmediatePropagation();send(src,'我的平行身份.png',t.tagName==='A'?'save':'share');return;}"+
        "if(t.tagName==='A'&&t.getAttribute('href').charAt(0)!=='#'){e.preventDefault();e.stopImmediatePropagation();if(e.isTrusted)NativeFiles.openSource(t.href);}},true);"+
        "window.__offlineNativeReady=true;})();";

    private void openExternalSource(String raw) {
        final String checked = SourceLinks.validatedHttps(raw);
        if (checked == null) { show("该出处链接不受支持，只允许已核查网站的 HTTPS 地址。"); return; }
        main.post(() -> {
            if (isFinishing() || isDestroyed()) return;
            try {
                Intent open = new Intent(Intent.ACTION_VIEW, Uri.parse(checked));
                open.addCategory(Intent.CATEGORY_BROWSABLE);
                startActivity(open);
            } catch (RuntimeException error) { show("未找到能打开出处的浏览器，请复制来源地址到浏览器查看。"); }
        });
    }

    public final class ImageBridge {
        @JavascriptInterface public void openSource(String url) { openExternalSource(url); }
        @JavascriptInterface public synchronized void beginImage(String name, String action) {
            if (imageBusy) { show("上一张图片仍在保存，请稍后再试。"); return; }
            imageChunks = new StringBuilder();
            pendingName = "我的平行身份.png";
            imageAction = "share".equals(action) ? "share" : "save";
        }
        @JavascriptInterface public synchronized void appendImageChunk(String chunk) {
            if (imageChunks == null || chunk == null) return;
            if (chunk.length() > 32768 || imageChunks.length() + chunk.length() > MAX_BASE64) {
                imageChunks = null;
                show("图片过大，请截图保存。");
                return;
            }
            imageChunks.append(chunk);
        }
        @JavascriptInterface public synchronized void finishImage() {
            if (imageChunks == null || imageBusy) return;
            try {
                final byte[] png = Base64.decode(imageChunks.toString(), Base64.DEFAULT);
                imageChunks = null;
                if (png.length < 8 || png[0] != (byte)137 || png[1] != 80 || png[2] != 78 || png[3] != 71) throw new IllegalArgumentException("not PNG");
                BitmapFactory.Options bounds = new BitmapFactory.Options(); bounds.inJustDecodeBounds = true;
                BitmapFactory.decodeByteArray(png, 0, png.length, bounds);
                if (bounds.outWidth <= 0 || bounds.outWidth > 4096 || bounds.outHeight <= 0 || bounds.outHeight > 4096) throw new IllegalArgumentException("invalid dimensions");
                final boolean share = "share".equals(imageAction);
                imageBusy = true;
                main.post(() -> { if (share) shareImage(png); else chooseImageLocation(png); });
            } catch (RuntimeException e) { imageChunks = null; imageBusy = false; show("图片未能保存，请截图后重试。"); }
        }
    }

    private void chooseImageLocation(byte[] png) {
        try {
            File dir = new File(getCacheDir(), "pending-images");
            if (!dir.exists() && !dir.mkdirs()) throw new java.io.IOException("no cache");
            pendingImageFile = UUID.randomUUID().toString().replace("-", "")+".png";
            try (FileOutputStream out = new FileOutputStream(new File(dir,pendingImageFile))) { out.write(png); }
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("image/png");
            intent.putExtra(Intent.EXTRA_TITLE, pendingName == null ? "我的平行身份.png" : pendingName);
            startActivityForResult(intent, CREATE_IMAGE);
        } catch (Exception e) { clearPendingImage(); imageBusy = false; show("未能打开保存界面，请截图保存。"); }
    }
    private void clearPendingImage() {
        if (pendingImageFile != null && pendingImageFile.matches("[a-f0-9]{32}\\.png"))
            new File(new File(getCacheDir(),"pending-images"),pendingImageFile).delete();
        pendingImageFile = null;
    }
    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != CREATE_IMAGE) return;
        imageBusy = false;
        if (resultCode != RESULT_OK || data == null || data.getData() == null) { clearPendingImage(); return; }
        try {
            if (pendingImageFile == null || !pendingImageFile.matches("[a-f0-9]{32}\\.png")) throw new java.io.IOException("no pending image");
            File source = new File(new File(getCacheDir(),"pending-images"),pendingImageFile);
            byte[] png = java.nio.file.Files.readAllBytes(source.toPath());
            try (OutputStream out = getContentResolver().openOutputStream(data.getData(), "w")) {
                if (out == null) throw new java.io.IOException("no output");
                out.write(png); show("图片已保存。");
            }
        } catch (Exception e) { show("图片未能保存，请选择其他文件夹或重新生成图片。"); }
        finally { clearPendingImage(); }
    }
    private void shareImage(byte[] png) {
        try {
            File dir = new File(getCacheDir(), "shared-images");
            if (!dir.exists() && !dir.mkdirs()) throw new java.io.IOException("no cache");
            for (File old : dir.listFiles()) if (old.lastModified() < System.currentTimeMillis()-86400000L) old.delete();
            File target = new File(dir, UUID.randomUUID().toString().replace("-", "")+".png");
            try (FileOutputStream out = new FileOutputStream(target)) { out.write(png); }
            Uri uri = Uri.parse("content://com.elsewhere.parallelself.images/"+target.getName());
            Intent send = new Intent(Intent.ACTION_SEND);
            send.setType("image/png");send.putExtra(Intent.EXTRA_STREAM,uri);
            send.setClipData(ClipData.newRawUri("平行身份卡",uri));send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(Intent.createChooser(send,"分享平行身份卡"));
        } catch (Exception e) { show("系统分享不可用，请使用下载图片或截图。"); }
        finally { imageBusy = false; }
    }
    private void show(final String text) { main.post(() -> Toast.makeText(MainActivity.this,text,Toast.LENGTH_LONG).show()); }
    @Override public void onBackPressed() {
        if (web == null || startupErrorVisible) { finish(); return; }
        web.evaluateJavascript("(function(){var d=document.querySelector('dialog[open]');if(d){d.close();return true;}if(!document.querySelector('.v3-home,.v4-home')){var h=document.getElementById('home-link');if(h){h.click();return true;}}return false;})()",value->{if(!"true".equals(value))new AlertDialog.Builder(this).setMessage("退出另一个我？答题进度仍保存在本机。").setPositiveButton("退出",(d,w)->finish()).setNegativeButton("继续探索",null).show();});
    }
    @Override protected void onSaveInstanceState(Bundle state) { super.onSaveInstanceState(state);if(pendingImageFile!=null)state.putString("pendingImageFile",pendingImageFile);if(web!=null)web.saveState(state); }
    @Override protected void onDestroy() { main.removeCallbacksAndMessages(null);if(web!=null){web.removeJavascriptInterface("NativeFiles");web.destroy();web=null;}super.onDestroy(); }
}
