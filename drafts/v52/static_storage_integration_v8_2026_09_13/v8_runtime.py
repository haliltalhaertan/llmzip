from __future__ import annotations
import hashlib, itertools, os, stat, sys, types
from pathlib import Path

MAX_SOURCE_BYTES = 64 * 1024 * 1024
V7_SOURCE_SHA256 = 'f7c6749f4648e6fc0f4034dca1823bfe03a2f70429533407217d43cfbbdff4e5'
PARENT_GUARD_SHA256 = '19724919c9085e49a531e94bdb269cba96c81739f7d9449b717db982becde4c9'
CONTRACT_SHA256 = 'e395451d026f176b875856244abe73b54a7d54cdf2649eec272f14cfc609c510'
V6_PREFLIGHT_SHA256 = 'eb7165bcbe633c0a9d233e3b7167fb67590ca8b8db6076d6b205a6e1c7648b75'
LONGMEMEVAL_ANCHOR_SHA256 = 'd4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32'
LONGMEMEVAL_ID_COLUMN = 'question_id'
LONGMEMEVAL_VALUE_COLUMN = 'N_archive'
LONGMEMEVAL_EXPECTED_ROWS = 470

_O_NOFOLLOW=getattr(os,'O_NOFOLLOW',0); _O_NONBLOCK=getattr(os,'O_NONBLOCK',0)
_O_CLOEXEC=getattr(os,'O_CLOEXEC',0); _O_BINARY=getattr(os,'O_BINARY',0)
_MODULE_COUNTER=itertools.count()

class V8ValidationError(ValueError): pass

def need(c,m):
    if not c: raise V8ValidationError(m)

def digest(v,w):
    need(type(v) is str and len(v)==64 and all(c in '0123456789abcdef' for c in v), f'{w}: lowercase SHA256 required')

def discover_repo_root():
    env=os.environ.get('LLMZIP_REPO')
    if env:
        c=Path(env).resolve()
        if (c/'drafts/v52/static_storage_contract_2026_09_12').is_dir(): return c
    here=Path(__file__).resolve()
    for c in (here.parent,*here.parents):
        if (c/'drafts/v52/static_storage_contract_2026_09_12').is_dir(): return c
    return here.parent

REPO_ROOT=discover_repo_root()
V7_PATH=REPO_ROOT/'drafts/v52/static_storage_integration_v7_2026_09_13/storage_semantic_gate_v7.py'
PARENT_GUARD_PATH=REPO_ROOT/'drafts/v52/static_storage_contract_2026_09_12/measurement_plan_guard.py'
CONTRACT_PATH=REPO_ROOT/'drafts/v52/static_storage_contract_2026_09_12/MEASUREMENT_CONTRACT_TR.md'
V6_PATH=REPO_ROOT/'drafts/v52/static_storage_integration_v6_2026_09_12/storage_adapter_preflight_v6.py'

def read_regular(path,limit,where):
    path=Path(path)
    try: pre=os.stat(str(path),follow_symlinks=False)
    except (OSError,ValueError) as e: raise V8ValidationError(f'{where}: cannot stat source: {e.__class__.__name__}') from e
    need(stat.S_ISREG(pre.st_mode),f'{where}: source must be a regular file'); need(pre.st_size<=limit,f'{where}: source byte limit')
    try: fd=os.open(str(path),os.O_RDONLY|_O_NOFOLLOW|_O_NONBLOCK|_O_CLOEXEC|_O_BINARY)
    except (OSError,ValueError) as e: raise V8ValidationError(f'{where}: cannot open source: {e.__class__.__name__}') from e
    try:
        post=os.fstat(fd); need(stat.S_ISREG(post.st_mode),f'{where}: opened source is not regular')
        need((post.st_dev,post.st_ino)==(pre.st_dev,pre.st_ino),f'{where}: source changed identity between stat and open')
        chunks=[]; total=0
        while True:
            try: chunk=os.read(fd,1<<20)
            except OSError as e: raise V8ValidationError(f'{where}: source read failed: {e.__class__.__name__}') from e
            if not chunk: break
            total+=len(chunk); need(total<=limit,f'{where}: source byte limit'); chunks.append(chunk)
        return b''.join(chunks)
    finally: os.close(fd)

def authenticate_fixed(path,expected,where,limit=MAX_SOURCE_BYTES):
    digest(expected,f'{where} expected SHA256'); raw=read_regular(path,limit,where)
    need(hashlib.sha256(raw).hexdigest()==expected,f'{where}: SHA256 mismatch'); return raw

def exec_pinned_module(label,path,expected):
    '''Execute authenticated source bytes in a fresh namespace, never import cache/pyc.'''
    raw=authenticate_fixed(path,expected,f'{label} source'); path=Path(path).resolve()
    name=f'_v52_pinned_{label}_{expected[:12]}_{next(_MODULE_COUNTER)}'; mod=types.ModuleType(name)
    mod.__file__=str(path); mod.__package__=''; mod.__loader__=None
    previous=sys.modules.get(name); sys.modules[name]=mod
    try:
        try: exec(compile(raw,str(path),'exec',dont_inherit=True),mod.__dict__)
        except Exception as e: raise V8ValidationError(f'{label}: authenticated source execution failed: {e.__class__.__name__}: {e}') from e
    finally:
        if previous is None: sys.modules.pop(name,None)
        else: sys.modules[name]=previous
    return mod
