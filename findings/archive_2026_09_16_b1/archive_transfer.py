#!/usr/bin/env python3
"""Pinned, bounded archive transfer with fresh-URL diagnostics; never runs research."""
import base64,json,os,hashlib,urllib.request,urllib.error,xml.etree.ElementTree as ET
REPO='haliltalhaertan/llmzip'; PREFIX='findings/archive_2026_09_16_b1/'
HEAD={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'}
def read(path,ref):
    req=urllib.request.Request(f'https://api.github.com/repos/{REPO}/contents/{path}?ref={ref}',headers=HEAD)
    with urllib.request.urlopen(req,timeout=60) as r: obj=json.load(r)
    return base64.b64decode(obj['content'])
current=json.loads(read(PREFIX+'transfer_request.json',os.environ['ARCHIVE_SHA']))
original=urllib.request.urlopen
def checked_open(req,*args,**kwargs):
    url=req.full_url if isinstance(req,urllib.request.Request) else str(req)
    try: return original(req,*args,**kwargs)
    except urllib.error.HTTPError as e:
        if '.oaiusercontent.com/' in url:
            try:
                root=ET.fromstring(e.read(4096))
                print('SOURCE DIAGNOSTIC:',e.code,root.findtext('Code'),root.findtext('AuthenticationErrorDetail'),flush=True)
            except ET.ParseError: print('SOURCE DIAGNOSTIC:',e.code,'Non-XML response omitted',flush=True)
        raise
urllib.request.urlopen=checked_open
if current.get('mode')=='DIAGNOSE_SOURCE':
    try:
        with urllib.request.urlopen(current['url'],timeout=30) as r: data=r.read(1000000)
        if hashlib.sha256(data).hexdigest()!='66ddb7a424433515aeb4b0faee3cc92bf0ec5434dcb3a69eaf05844bf2585ccc': raise RuntimeError('Hash mismatch')
        print('FRESH SOURCE VERIFIED',len(data),flush=True)
    except Exception as e: print('DIAGNOSIS FAILED',type(e).__name__,flush=True); raise SystemExit(1)
else:
    code=read(PREFIX+'archive_transfer.py','3b68d7e11018ee5f879dd25eda6d5da9c17d23d6')
    ns={'__name__':'archive_impl'};exec(compile(code,'pinned_archive_transfer.py','exec'),ns)
    if current.get('refresh_urls'):
        initial=json.loads(read(PREFIX+'transfer_request.json','ddd7fcc2599e482e466ce14fb4489a07ab4d03ac'))
        for rec in initial['transports']:rec['url']=current['refresh_urls'].get(rec['name'],rec['url'])
        getter=ns['file_bytes']
        ns['file_bytes']=lambda p,r:json.dumps(initial).encode() if p==PREFIX+'transfer_request.json' else getter(p,r)
    try:ns['main']()
    except Exception as e:
        print('ARCHIVE FAILED:',str(e) if isinstance(e,RuntimeError) else type(e).__name__,flush=True)
        raise SystemExit(1)
