#!/usr/bin/env python3
"""Verify the packaged document, signature, Android metadata and permission boundary."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,zipfile
apk=Path(sys.argv[1]).resolve();html=Path(sys.argv[2]).resolve()
output=Path(sys.argv[3]).resolve() if len(sys.argv)>3 else apk.with_suffix('.validation.json')
root=Path(os.environ.get('PARALLEL_ANDROID_TOOLS','/workspace/scratch/android-delivery'))
tools=root/'sdk/android-15'
def run(*args):return subprocess.run(args,check=True,text=True,capture_output=True).stdout
signatures=run(str(tools/'apksigner'),'verify','--verbose','--print-certs',str(apk))
run(str(tools/'zipalign'),'-c','-p','4',str(apk))
badging=run(str(tools/'aapt'),'dump','badging',str(apk));permissions=run(str(tools/'aapt'),'dump','permissions',str(apk))
assert "application-label:'另一个我'" in badging
assert "versionName='4.0.0'" in badging and "versionCode='4'" in badging
assert "sdkVersion:'26'" in badging and "targetSdkVersion:'35'" in badging
assert 'uses-permission:' not in permissions and 'uses-permission-sdk-23:' not in permissions
assert 'Verified using v2 scheme (APK Signature Scheme v2): true' in signatures
assert 'Verified using v3 scheme (APK Signature Scheme v3): true' in signatures
with zipfile.ZipFile(apk) as z:
 assert z.testzip() is None
 assert {'AndroidManifest.xml','classes.dex','resources.arsc','assets/index.html'} <= set(z.namelist())
 packaged=z.read('assets/index.html')
 assert packaged==html.read_bytes(), 'APK HTML does not match selected build input'
cert=re.search(r'certificate SHA-256 digest: ([0-9a-f]+)',signatures).group(1)
result={
 'artifact':str(apk),'bytes':apk.stat().st_size,'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),
 'application_label':'另一个我','package':'com.elsewhere.parallelself','version':'4.0.0','version_code':4,
 'min_sdk':26,'target_sdk':35,'requested_permissions':[],
 'signature_v2_verified':True,'signature_v3_verified':True,'signer_certificate_sha256':cert,'zip_alignment_verified':True,
 'packaged_html_matches_input':True,'html_input':str(html),'html_sha256':hashlib.sha256(packaged).hexdigest(),
 'runtime_installation_and_launch':'not_run_no_device_or_emulator',
 'phone_download_accessibility':'not_established_by_local_build',
}
output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
