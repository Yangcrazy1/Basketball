#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TOOL_ROOT="${PARALLEL_ANDROID_TOOLS:-/workspace/scratch/android-delivery}"
SDK_PLATFORM="$TOOL_ROOT/sdk/android-35/android.jar"
SDK_TOOLS="$TOOL_ROOT/sdk/android-15"
ECJ="$TOOL_ROOT/cache/ecj-3.42.0.jar"
INPUT_HTML="${1:-$TASK_ROOT/../dist/parallel-self.html}"
OUTPUT_APK="${2:-$TASK_ROOT/../dist/parallel-self-android.apk}"
SIGN_KEY="${PARALLEL_ANDROID_KEYSTORE:-$TOOL_ROOT/parallel-self-debug.keystore}"
for required in "$SDK_PLATFORM" "$SDK_TOOLS/aapt" "$SDK_TOOLS/d8" "$SDK_TOOLS/zipalign" "$SDK_TOOLS/apksigner" "$ECJ" "$INPUT_HTML"; do
  test -f "$required" || { echo "Missing build prerequisite: $required" >&2; exit 1; }
done
python3 - "$INPUT_HTML" <<'PY_CHECK'
from pathlib import Path
import re,sys
html=Path(sys.argv[1]).read_text()
if not re.search(r"(?:appReady\s*=|data-app-ready)",html):
    raise SystemExit("HTML does not expose the appReady startup marker. Add document.documentElement.dataset.appReady='true' after successful startup; refusing to ship a wrapper that would diagnose normal startup as failure.")
PY_CHECK
BUILD_DIR="$TASK_ROOT/build"
rm -rf -- "$BUILD_DIR/classes" "$BUILD_DIR/gen" "$BUILD_DIR/dex"
mkdir -p "$BUILD_DIR/classes" "$BUILD_DIR/assets" "$BUILD_DIR/gen" "$BUILD_DIR/dex"
rm -f "$BUILD_DIR/resources.apk" "$BUILD_DIR/aligned.apk"
cp -- "$INPUT_HTML" "$BUILD_DIR/assets/index.html"
"$SDK_TOOLS/aapt" package -f -M "$TASK_ROOT/AndroidManifest.xml" -S "$TASK_ROOT/res" -A "$BUILD_DIR/assets" -I "$SDK_PLATFORM" -J "$BUILD_DIR/gen" -F "$BUILD_DIR/resources.apk"
mapfile -t JAVA_SOURCES < <(find "$TASK_ROOT/src" "$BUILD_DIR/gen" -name '*.java' -print)
java -jar "$ECJ" -1.8 -encoding UTF-8 -bootclasspath "$SDK_PLATFORM:$SDK_TOOLS/core-lambda-stubs.jar" -d "$BUILD_DIR/classes" "${JAVA_SOURCES[@]}"
mapfile -t CLASS_FILES < <(find "$BUILD_DIR/classes" -name '*.class' -print)
"$SDK_TOOLS/d8" --min-api 26 --lib "$SDK_PLATFORM" --output "$BUILD_DIR/dex" "${CLASS_FILES[@]}"
python3 - "$BUILD_DIR/resources.apk" "$BUILD_DIR/dex/classes.dex" <<'PY'
import pathlib,sys,zipfile
apk=pathlib.Path(sys.argv[1]);dex=pathlib.Path(sys.argv[2])
with zipfile.ZipFile(apk,'a',zipfile.ZIP_DEFLATED) as z:z.write(dex,'classes.dex')
PY
"$SDK_TOOLS/zipalign" -f -p 4 "$BUILD_DIR/resources.apk" "$BUILD_DIR/aligned.apk"
if [ ! -f "$SIGN_KEY" ]; then
  mkdir -p "$(dirname -- "$SIGN_KEY")"
  keytool -genkeypair -keystore "$SIGN_KEY" -storepass android -keypass android -alias parallel-self-local -dname 'CN=Parallel Self Local Demo,O=Local Development,C=CN' -keyalg RSA -keysize 2048 -validity 3650 -noprompt
  chmod 600 "$SIGN_KEY"
fi
mkdir -p "$(dirname -- "$OUTPUT_APK")"
"$SDK_TOOLS/apksigner" sign --ks "$SIGN_KEY" --ks-key-alias parallel-self-local --ks-pass pass:android --key-pass pass:android --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true --out "$OUTPUT_APK" "$BUILD_DIR/aligned.apk"
"$SDK_TOOLS/apksigner" verify --verbose --print-certs "$OUTPUT_APK"
"$SDK_TOOLS/zipalign" -c -p 4 "$OUTPUT_APK"
"$SDK_TOOLS/aapt" dump badging "$OUTPUT_APK"
python3 "$TASK_ROOT/verify-apk.py" "$OUTPUT_APK" "$INPUT_HTML"
echo "APK built: $OUTPUT_APK"
