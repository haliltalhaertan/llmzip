# Gemini betigindeki list(set(...))[:N] deterministik mi?
import subprocess, sys
code = ("import json;"
        "s=set('metin-%d'%i for i in range(1000));"
        "print(json.dumps(list(s)[:5]))")
outs = [subprocess.run([sys.executable,"-c",code],capture_output=True,text=True).stdout.strip()
        for _ in range(4)]
for i,o in enumerate(outs): print(f"  kosu {i+1}: {o}")
print("TUM KOSULAR AYNI MI:", len(set(outs))==1)
