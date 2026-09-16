#!/usr/bin/env python3
"""Pinned archive transfer, with sanitized source-download diagnostics."""
import base64, json, os, urllib.request, urllib.error, urllib.parse, xml.etree.ElementTree as ET
repo='haliltalhaertan/llmzip'
ref='3b68d7e11018ee5f879dd25eda6d5da9c17d23d6'
path='findings/archive_2026_09_16_b1/archive_transfer.py'
req=urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/{path}?ref={ref}',headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
with urllib.request.urlopen(req,timeout=60) as r: obj=json.load(r)
code=base64.b64decode(obj['content']).decode()
original=urllib.request.urlopen
def checked_open(req,*args,**kwargs):
    url=req.full_url if isinstance(req,urllib.request.Request) else str(req)
    try:
        return original(req,*args,**kwargs)
    except urllib.error.HTTPError as e:
        if '.oaiusercontent.com/' in url:
            body=e.read(4096)
            try:
                root=ET.fromstring(body)
                print('SOURCE DIAGNOSTIC:',e.code,root.findtext('Code'),root.findtext('AuthenticationErrorDetail'),flush=True)
            except ET.ParseError:
                print('SOURCE DIAGNOSTIC:',e.code,'Non-XML error; response omitted',flush=True)
        raise
urllib.request.urlopen=checked_open
exec(compile(code,'pinned_archive_transfer.py','exec'),{'__name__':'__main__'})
