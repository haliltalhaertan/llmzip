import zipfile, os, io, json

DRIVE = r'C:\Users\MDP\dev\llmzip-work\drive'
zips = [z for z in os.listdir(DRIVE) if z.lower().endswith('.zip')]
flags = ['pkl', 'cache', 'npy', 'npz', 'matrix', 'tensor', 'emb', 'repr', 'c_', 'qc', 'gold', 'code', 'npz', 'vector', 'hetero', 'byte']
for z in sorted(zips):
    path = os.path.join(DRIVE, z)
    try:
        zf = zipfile.ZipFile(path)
        names = zf.namelist()
        print(f'\n##### {z}  [{len(names)} entries]')
        nested = [n for n in names if n.lower().endswith('.zip') or n.lower().endswith('.tar') or n.lower().endswith('.gz') or n.lower().endswith('.npz')]
        for n in names[:80]:
            if len(names) <= 80 or any(t in n.lower() for t in flags) or n in nested:
                try:
                    inf = zf.getinfo(n)
                    print(f'   {inf.file_size:>10}  {n}')
                except Exception:
                    print('   (dir)      ', n)
        if len(names) > 80:
            print(f'   ... ({len(names)} total; only flagged shown)')
        # count nested npz/zip entries
        npz = [n for n in names if n.lower().endswith('.npz')]
        if npz:
            print(f'   >>> nested NPZ count: {len(npz)}; samples: {npz[:3]}')
        nested_zips = [n for n in names if n.lower().endswith('.zip')]
        if nested_zips:
            print(f'   >>> nested ZIP: {nested_zips}')
    except Exception as e:
        print(z, 'ERR', e)
