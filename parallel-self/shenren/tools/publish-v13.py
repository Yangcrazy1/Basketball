"""Publish the tested V13 folder, preserving every previous release path."""
from pathlib import Path
import hashlib, json, os, subprocess, tempfile

R = Path(__file__).resolve().parents[3]
A = R / 'parallel-self/shenren'
W = A / 'dist/web'

def git(*args, input=None, env=None):
    return subprocess.run(['git', *args], cwd=R, input=input, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode().strip()

parent = git('rev-parse', 'refs/heads/codex/parallel-self-web')
assert git('ls-remote', 'origin', 'refs/heads/gh-pages').split()[0] == parent
meta = json.loads((A / 'docs/v13-build-manifest.json').read_text())
browser = json.loads((A / 'docs/browser-check-v13.json').read_text())
assert meta['version'] == 13 and meta['schemaVersion'] == 12
assert browser['status'] == 'passed' and browser['pendingAvatars'] == [] and meta['pendingAvatars'] == []
assert browser['html_sha256'] == meta['offline_html_sha256']
assert hashlib.sha256((W / 'index.html').read_bytes()).hexdigest() == meta['entry_sha256']
assert hashlib.sha256((W / 'world-another-me.html').read_bytes()).hexdigest() == meta['offline_html_sha256']
assert (W / 'review.html').is_file()
base = 'v13'
with tempfile.TemporaryDirectory() as tmp:
    env = os.environ.copy()
    env['GIT_INDEX_FILE'] = tmp + '/index'
    git('read-tree', parent, env=env)

    def add(path, body):
        blob = git('hash-object', '-w', '--stdin', input=body)
        git('update-index', '--add', '--cacheinfo', '100644', blob, path, env=env)

    for f in W.rglob('*'):
        if f.is_file():
            add(base + '/' + f.relative_to(W).as_posix(), f.read_bytes())
    meta.update(source_commit=git('rev-parse', 'HEAD'), previous_entries_unchanged=True)
    add(base + '/build-info.json', (json.dumps(meta, ensure_ascii=False, indent=2) + '\n').encode())
    tree = git('write-tree', env=env)
    # Compare all changed paths, not a small hand-picked subset of old entry points.
    changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', parent, tree).splitlines()
    assert changed and all(path.startswith(base + '/') for path in changed), changed
    for old in ['index.html', 'play/index.html', 'build-info.json', 'download/index.html', 'preview/v11/r5/index.html', 'v12/index.html', 'v12/build-info.json']:
        assert git('rev-parse', parent + ':' + old) == git('rev-parse', tree + ':' + old), old
    commit = git('commit-tree', tree, '-p', parent, input=b'Publish V13 mirror universes, expanded cast and answer-related popularity priority\n')
    git('update-ref', 'refs/heads/codex/parallel-self-web', commit, parent)
    git('push', 'origin', 'codex/parallel-self-web', 'codex/parallel-self-web:refs/heads/gh-pages')
    print(json.dumps(dict(url=meta['webURL'], deployment=commit, **meta), ensure_ascii=False, indent=2))
