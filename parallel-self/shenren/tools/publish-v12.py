"""Publish the tested V10-reborn release at /v12/; retain previous entry points."""
from pathlib import Path
import subprocess, os, tempfile, json

R = Path(__file__).resolve().parents[3]
A = R / 'parallel-self/shenren'
W = A / 'dist/web'
def git(*args, input=None, env=None):
    return subprocess.run(['git', *args], cwd=R, input=input, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode().strip()

parent = git('rev-parse', 'refs/heads/codex/parallel-self-web')
assert git('ls-remote', 'origin', 'refs/heads/gh-pages').split()[0] == parent
meta = json.loads((A / 'docs/v12-build-manifest.json').read_text())
assert meta['pendingAvatars'] == [] and meta['browserGroups'] == 16
base = 'v12'
with tempfile.TemporaryDirectory() as tmp:
    env = os.environ.copy()
    env['GIT_INDEX_FILE'] = tmp + '/index'
    git('read-tree', parent, env=env)
    def add(path, body):
        h = git('hash-object', '-w', '--stdin', input=body)
        git('update-index', '--add', '--cacheinfo', '100644', h, path, env=env)
    for f in W.rglob('*'):
        if f.is_file():
            add(base + '/' + f.relative_to(W).as_posix(), f.read_bytes())
    meta.update(source_commit=git('rev-parse', 'HEAD'), previous_entries_unchanged=True)
    add(base + '/build-info.json', (json.dumps(meta, ensure_ascii=False, indent=2) + '\n').encode())
    tree = git('write-tree', env=env)
    for path in ['index.html', 'play/index.html', 'build-info.json', 'download/index.html', 'preview/v11/r5/index.html']:
        assert git('rev-parse', parent + ':' + path) == git('rev-parse', tree + ':' + path), path
    commit = git('commit-tree', tree, '-p', parent, input=b'Release V10 reborn: stories, verified portraits and five-person posters at /v12/\n')
    git('update-ref', 'refs/heads/codex/parallel-self-web', commit, parent)
    git('push', 'origin', 'codex/parallel-self-web', 'codex/parallel-self-web:refs/heads/gh-pages')
    print(json.dumps(dict(url=meta['webURL'], deployment=commit, **meta), ensure_ascii=False, indent=2))
