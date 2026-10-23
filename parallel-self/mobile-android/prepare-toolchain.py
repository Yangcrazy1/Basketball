#!/usr/bin/env python3
"""Fetch pinned official build artifacts, verify upstream checksums, extract locally."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import urllib.request
import zipfile

root = Path(os.environ.get('PARALLEL_ANDROID_TOOLS', '/workspace/scratch/android-delivery')).resolve()
cache = root / 'cache'; sdk = root / 'sdk'
cache.mkdir(parents=True, exist_ok=True); sdk.mkdir(exist_ok=True)
artifacts = [
    ('platform-35_r02.zip', 'https://dl.google.com/android/repository/platform-35_r02.zip', '0bb560a90a7a2cbd0dd8348224d518b638fe7949'),
    ('build-tools_r35_linux.zip', 'https://dl.google.com/android/repository/build-tools_r35_linux.zip', '2cfaa0bbb2336e9ec18ed3ecea84fa2e2af607bc'),
    ('ecj-3.42.0.jar', 'https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.42.0/ecj-3.42.0.jar', '22b170025f5e0d849d07f4a84d421e42fae701bf'),
]

def fetch(item):
    name, url, expected = item
    path = cache / name
    if not path.exists():
        partial = cache / (name + '.part')
        with urllib.request.urlopen(url, timeout=120) as response, partial.open('wb') as output:
            while block := response.read(1024 * 1024): output.write(block)
        partial.replace(path)
    actual = hashlib.sha1(path.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(f'Upstream checksum mismatch: {name}; expected {expected}, got {actual}. Do not execute this artifact.')
    if name.endswith('.zip'):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                target = (sdk / info.filename).resolve()
                if not target.is_relative_to(sdk): raise RuntimeError('Archive path escapes tool directory')
                archive.extract(info, sdk)
                permissions = info.external_attr >> 16
                if permissions and target.exists(): target.chmod(permissions & 0o777)
    return {'name': name, 'source': url, 'upstream_sha1': actual, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(fetch, artifacts))
(root / 'toolchain-verification.json').write_text(json.dumps(results, indent=2))
print(json.dumps({'tools_root': str(root), 'verified_artifacts': results}, indent=2))
