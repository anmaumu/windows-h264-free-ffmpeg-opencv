import hashlib, json, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs'
LOG.mkdir(exist_ok=True)
def digest(p):
    p = Path(p).resolve()
    return {'path': str(p), 'size': p.stat().st_size, 'sha256': hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()}
def save(name, value):
    (LOG / (name + '.json')).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
def run(name, args, **kw):
    args = list(map(str, args))
    started = time.time()
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
    (LOG / (name + '.stdout.txt')).write_bytes(p.stdout)
    (LOG / (name + '.stderr.txt')).write_bytes(p.stderr)
    record = {'name': name, 'argv': args, 'cwd': str(kw.get('cwd', Path.cwd())), 'exit_code': p.returncode, 'seconds': time.time()-started}
    with (LOG / 'commands.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False)+'\n')
    print(name, 'exit=', p.returncode, flush=True)
    return p
