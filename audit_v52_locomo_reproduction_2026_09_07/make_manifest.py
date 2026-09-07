"""Hash audit artifacts only, including this script, excluding recursive manifest."""
import hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
rows=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json']
(root/'artifact_manifest.json').write_text(json.dumps({'algorithm':'SHA-256','excludes':['artifact_manifest.json'],'files':rows},indent=2),encoding='utf-8')
print(json.dumps({'files':len(rows),'manifest_sha256':hashlib.sha256((root/'artifact_manifest.json').read_bytes()).hexdigest()},indent=2))
