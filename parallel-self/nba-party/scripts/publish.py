"""Publish only /nba/ while preserving all older original releases."""
from pathlib import Path
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
APP = Path(__file__).resolve().parents[1]
WEB = APP / 'dist/web'


def git(*args, input=None, env=None):
    return subprocess.run(['git', *args], cwd=ROOT, input=input, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


parent = git('rev-parse', 'refs/heads/codex/parallel-self-web')
assert git('ls-remote', 'origin', 'refs/heads/gh-pages').split()[0] == parent, 'Pages changed externally; inspect before publishing'
meta = json.loads((APP / 'docs/build-manifest.json').read_text())
assert meta['name'] == '整活NBA' and meta['browserChecks'] > 0
assert (WEB / 'download.html').is_file()
meta['sourceCommit'] = git('rev-parse', 'HEAD')
with tempfile.TemporaryDirectory() as tmp:
    env = os.environ.copy()
    env['GIT_INDEX_FILE'] = tmp + '/index'
    git('read-tree', parent, env=env)
    for path in sorted(WEB.rglob('*')):
        if path.is_file():
            blob = git('hash-object', '-w', '--stdin', input=path.read_bytes())
            git('update-index', '--add', '--cacheinfo', '100644', blob, 'nba/' + path.relative_to(WEB).as_posix(), env=env)
    blob = git('hash-object', '-w', '--stdin', input=(json.dumps(meta, ensure_ascii=False, indent=2) + '\n').encode())
    git('update-index', '--add', '--cacheinfo', '100644', blob, 'nba/build-info.json', env=env)
    tree = git('write-tree', env=env)
    changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', parent, tree).splitlines()
    assert changed and all(p.startswith('nba/') for p in changed), changed
    commit = git('commit-tree', tree, '-p', parent, input=b'Publish NBA entertainment quiz with court scenarios, DIY stars and native project downloads\n')
    git('update-ref', 'refs/heads/codex/parallel-self-web', commit, parent)
    git('push', 'origin', 'codex/parallel-self-web', 'codex/parallel-self-web:refs/heads/gh-pages')
    print(json.dumps({'url': meta['webURL'], 'sourceCommit': meta['sourceCommit'], 'deployment': commit, 'allPreviousPathsUnchanged': True}, ensure_ascii=False, indent=2))
