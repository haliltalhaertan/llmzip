#!/usr/bin/env python3
"""Authorized byte-preserving archive transfer only; NEVER runs research code."""
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO = 'haliltalhaertan/llmzip'
BRANCH = 'archive/latest-findings-b1-2026-09-16'
PREFIX = 'findings/archive_2026_09_16_b1/'
TAG = 'archive-findings-b1-2026-09-16'
SOURCE_HASH = '66ddb7a424433515aeb4b0faee3cc92bf0ec5434dcb3a69eaf05844bf2585ccc'
OLD_HASH = 'f8bd13f4798b27a7bc5ef27dce98d25ddf39d04d6fb31d910c66c27ce209ea74'
API = 'https://api.github.com/repos/' + REPO
TOKEN = os.environ['GH_TOKEN']
EVENT = os.environ['ARCHIVE_SHA']
if os.environ['ARCHIVE_REPO'] != REPO or os.environ['ARCHIVE_BRANCH'] != BRANCH:
    raise SystemExit('Repository/branch guard failed')
HEADERS = {'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github+json',
           'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'LLMZIP-archive-transfer'}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

NOREDIRECT = urllib.request.build_opener(NoRedirect)

def api(path, method='GET', data=None):
    url = API + path
    raw = None if data is None else json.dumps(data, ensure_ascii=False).encode()
    headers = dict(HEADERS)
    if raw is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=raw, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        raise RuntimeError('GitHub API ' + method + ' ' + path.split('?')[0] + ': HTTP ' + str(e.code)) from None

def file_bytes(path, ref):
    obj = api('/contents/' + urllib.parse.quote(path, safe='/') + '?ref=' + urllib.parse.quote(ref, safe=''))
    if obj.get('encoding') != 'base64':
        raise RuntimeError('Unexpected contents encoding')
    return base64.b64decode(obj['content'])

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def verify(path, rec):
    if Path(path).stat().st_size != rec['bytes'] or digest(path) != rec['sha256']:
        raise RuntimeError('Byte integrity failure: ' + Path(path).name)

def safe_relative(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or not p.parts:
        raise RuntimeError('Unsafe archive path')
    return p

def download(rec):
    name = str(safe_relative(rec['name']))
    if '/' in name:
        raise RuntimeError('Transport filename must be flat')
    url = rec['url']
    u = urllib.parse.urlparse(url)
    host = (u.hostname or '').lower()
    if u.scheme != 'https' or not (host.endswith('.oaiusercontent.com') or host.endswith('.blob.core.windows.net')):
        raise RuntimeError('Unauthorized source host')
    target = Path('transport') / name
    try:
        with urllib.request.urlopen(url, timeout=120) as r, target.open('wb') as f:
            total = 0
            while True:
                b = r.read(1024*1024)
                if not b:
                    break
                total += len(b)
                if total > rec['bytes']:
                    raise RuntimeError('Source larger than manifest')
                f.write(b)
        verify(target, rec)
        print('Source bytes verified:', name, rec['bytes'], flush=True)
        return target
    except urllib.error.HTTPError as e:
        raise RuntimeError('Source transfer HTTP ' + str(e.code) + ' for ' + name) from None

def commit_files(parent, paths, message):
    branch_ref = '/git/refs/heads/' + BRANCH
    if api('/git/ref/heads/' + BRANCH)['object']['sha'] != parent:
        raise RuntimeError('Concurrent branch movement: stop, no overwrite')
    entries = []
    for rel, data in paths.items():
        if not rel.startswith(PREFIX):
            raise RuntimeError('Write outside archive namespace refused')
        blob = api('/git/blobs', 'POST', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
        expected = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob['sha'] != expected:
            raise RuntimeError('Git blob integrity failure')
        entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    tree0 = api('/git/commits/' + parent)['tree']['sha']
    tree = api('/git/trees', 'POST', {'base_tree': tree0, 'tree': entries})
    commit = api('/git/commits', 'POST', {'message': message, 'tree': tree['sha'], 'parents': [parent]})
    api(branch_ref, 'PATCH', {'sha': commit['sha'], 'force': False})
    actual = {r['path']:r for r in api('/git/trees/' + tree['sha'] + '?recursive=1')['tree']}
    for e in entries:
        if actual[e['path']]['sha'] != e['sha']:
            raise RuntimeError('Committed tree mismatch')
    return commit['sha'], len(entries)

def upload_asset(release, name, path):
    data = Path(path).read_bytes()
    url = release['upload_url'].split('{', 1)[0] + '?name=' + urllib.parse.quote(name, safe='')
    headers = dict(HEADERS)
    headers['Content-Type'] = 'application/octet-stream'
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            obj = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError('Release upload HTTP ' + str(e.code) + ': ' + name) from None
    h = hashlib.sha256(data).hexdigest()
    if obj['size'] != len(data):
        raise RuntimeError('Release asset length mismatch')
    if obj.get('digest') and obj['digest'] != 'sha256:' + h:
        raise RuntimeError('Release provider digest mismatch')
    print('Release asset uploaded:', name, len(data), flush=True)
    return {'name': name, 'id':obj['id'], 'bytes':len(data), 'sha256':h,
            'provider_digest':obj.get('digest'), 'url':obj['browser_download_url']}

def verify_asset(rec):
    # Do not forward the GitHub token to a redirect or signed blob-storage host.
    url = API + '/releases/assets/' + str(rec['id'])
    headers = dict(HEADERS); headers['Accept'] = 'application/octet-stream'
    req = urllib.request.Request(url, headers=headers)
    try:
        response = NOREDIRECT.open(req, timeout=120)
    except urllib.error.HTTPError as e:
        if e.code not in (301,302,303,307,308):
            raise RuntimeError('Asset readback HTTP ' + str(e.code)) from None
        response = urllib.request.urlopen(e.headers['Location'], timeout=120)
    with response as r:
        if 'json' in r.headers.get('Content-Type',''):
            raise RuntimeError('Asset readback returned metadata, not bytes')
        h=hashlib.sha256(); n=0
        while True:
            b=r.read(1024*1024)
            if not b: break
            n += len(b); h.update(b)
    if n != rec['bytes'] or h.hexdigest() != rec['sha256']:
        raise RuntimeError('Release readback integrity failure: ' + rec['name'])
    rec['readback_sha256_match'] = True
    print('Release readback verified:', rec['name'], flush=True)

def main():
    req = json.loads(file_bytes(PREFIX + 'transfer_request.json', EVENT))
    if req.get('schema') != 'LLMZIP_AUTHORIZED_TRANSFER_V1':
        raise RuntimeError('Invalid request schema')
    transports = req['transports']
    if len(transports) != 7 or sum(r['bytes'] for r in transports) > 400_000_000:
        raise RuntimeError('Transfer scope exceeds authorized archive')
    Path('transport').mkdir(exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(download, transports))
    source = Path('transport/LLMZIP_SON_RAPORLAR_KOD_VE_DEVIR_2026-09-16.zip')
    if digest(source) != SOURCE_HASH:
        raise RuntimeError('Unexpected source package')
    old = Path('transport/LLMZIP_TUM_BULGULAR_2026-09-15_16.zip')
    if digest(old) != OLD_HASH:
        raise RuntimeError('Unexpected prior archive')
    dest=Path('source'); dest.mkdir()
    with zipfile.ZipFile(source) as z:
        if len(z.infolist()) != 68 or sum(i.file_size for i in z.infolist()) > 20_000_000:
            raise RuntimeError('Source bundle bounds mismatch')
        if z.testzip(): raise RuntimeError('Source ZIP CRC failure')
        for i in z.infolist():
            rel=safe_relative(i.filename)
            if stat.S_ISLNK(i.external_attr>>16): raise RuntimeError('Symlink refused')
            p=dest/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(z.read(i))
    sm=json.loads((dest/'SOURCE_FILE_MANIFEST.json').read_text())
    for r in sm['files']: verify(dest/safe_relative(r['path']),r)
    manifest=json.loads((dest/'ORIGINAL_MANIFEST.json').read_text())
    assets={}
    for rec in manifest['files']:
        name=rec['basename']; safe_relative(name)
        if rec.get('transport_parts'):
            path=Path('transport')/name
            with path.open('wb') as out:
                for part in rec['transport_parts']:
                    p=Path('transport')/part['name']; verify(p,part)
                    with p.open('rb') as f:
                        for b in iter(lambda:f.read(1024*1024),b''): out.write(b)
        else: path=dest/'originals'/safe_relative(rec['path'])
        verify(path,rec)
        if name in assets: raise RuntimeError('Duplicate asset basename')
        assets[name]=path
    assert len(assets)==12
    assets[old.name]=old; assets[source.name]=source
    for name in ('DURUM_VE_DEVAM_PROMPTU_2026-09-16.md','ORIGINAL_MANIFEST.json','reassemble_verify.py'):
        assets[name]=dest/name
    paths={PREFIX+str(p.relative_to(dest)):p.read_bytes() for p in sorted(dest.rglob('*')) if p.is_file()}
    docs_commit,nfiles=commit_files(EVENT,paths,'archive: preserve 12 late artifacts, readable code and B1 handoff [skip ci]')
    body=('Archival snapshot, not a scientific or production release. '
          '12 previously unarchived originals, readable code and current handoff; '
          'the old 28-original bundle is also included to repair the earlier index-only GitHub delivery. '
          'No benchmark code is executed. Source hashes verified; release byte-readback pending. '
          'Drive: https://drive.google.com/drive/folders/1q2JVwmA_LKBmLaZtMqJTXsLWBWhT4O_m')
    release=api('/releases','POST',{'tag_name':TAG,'target_commitish':docs_commit,
           'name':'LLMZIP — verified findings archive and B1 handoff — 2026-09-16',
           'body':body,'draft':True,'prerelease':True,'make_latest':'false'})
    uploaded=[upload_asset(release,name,path) for name,path in assets.items()]
    api('/releases/'+str(release['id']),'PATCH',{'draft':False,'prerelease':True,'make_latest':'false'})
    for rec in uploaded: verify_asset(rec)
    before='59b891efda7b6c06f44da7fa0ae4fe3c13f79a2e'
    now=api('/git/ref/heads/main')['object']['sha']
    receipt={'schema':'LLMZIP_ARCHIVE_RECEIPT_V2','status':'COMPLETE_BYTE_READBACK_VERIFIED',
      'date':'2026-09-16','repository':REPO,'branch':BRANCH,'namespace':PREFIX,
      'source_commit':docs_commit,'release_id':release['id'],'release_tag':TAG,
      'release_url':'https://github.com/'+REPO+'/releases/tag/'+TAG,
      'drive_folder':'https://drive.google.com/drive/folders/1q2JVwmA_LKBmLaZtMqJTXsLWBWhT4O_m',
      'new_originals':12,'new_original_bytes':manifest['new_original_bytes'],
      'prior_originals_in_combined_bundle':28,'source_tree_files':nfiles,
      'assets':uploaded,'asset_byte_readback_verified':len(uploaded),
      'main_at_start':before,'main_at_end':now,'main_unchanged':now==before,
      'scientific_claims_revalidated':False,'research_code_executed':False,
      'independent_scientific_audit':False,'drive_transport':req.get('drive_files',[])}
    raw=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()
    Path('ARCHIVE_RECEIPT.json').write_bytes(raw)
    clean=dict(req)
    clean['transports']=[{k:v for k,v in r.items() if k!='url'} for r in transports]
    clean['status']='COMPLETED; expiring transport URLs removed from current tree'
    fin,n=commit_files(docs_commit,{PREFIX+'ARCHIVE_RECEIPT.json':raw,
        PREFIX+'transfer_request.json':(json.dumps(clean,indent=2)+'\n').encode()},
        'archive: record release byte-readback and redact expired transport URLs [skip ci]')
    r=upload_asset(release,'ARCHIVE_RECEIPT.json',Path('ARCHIVE_RECEIPT.json')); verify_asset(r)
    api('/releases/'+str(release['id']),'PATCH',{'body':body.replace('Source hashes verified; release byte-readback pending.',
        'All 17 payload assets were downloaded back and SHA-256 verified. Receipt asset also read back. '
        'Final archive branch commit: '+fin+'. Read ARCHIVE_RECEIPT.json. Original files unchanged; no scientific claims promoted.')})
    print(json.dumps({'status':'COMPLETE','commit':fin,'release_id':release['id'],'verified_assets':18,'main_unchanged':now==before}),flush=True)

if __name__=='__main__':
    try: main()
    except Exception as e:
        if isinstance(e,RuntimeError): print('ARCHIVE FAILED:',str(e),flush=True)
        else: print('ARCHIVE FAILED:',type(e).__name__,flush=True)
        sys.exit(1)
