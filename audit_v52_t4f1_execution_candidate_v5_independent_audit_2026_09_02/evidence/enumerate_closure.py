#!/usr/bin/env python3
"""Recursive byte enumeration of a package namespace. Outcome-free."""
import hashlib, json, os, sys, stat

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def enumerate_tree(root):
    files, dirs, other = [], [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for d in dirnames:
            dirs.append(os.path.relpath(os.path.join(dirpath, d), root))
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            st = os.lstat(full)
            if not stat.S_ISREG(st.st_mode):
                other.append({"path": rel, "mode": oct(st.st_mode)})
                continue
            files.append({"path": rel, "size": st.st_size, "sha256": sha256(full),
                          "depth": rel.count(os.sep)})
    return {"root": root, "file_count": len(files), "dir_count": len(dirs),
            "dirs": sorted(dirs), "non_regular": other, "files": files}

if __name__ == '__main__':
    out = {}
    for root in sys.argv[1:]:
        out[os.path.basename(os.path.normpath(root))] = enumerate_tree(root)
    print(json.dumps(out, indent=2, sort_keys=True))
