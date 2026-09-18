import zipfile, io, os, json

DRIVE = r'C:\Users\MDP\dev\llmzip-work\drive'

print('========== V52_T4C2_BINARY_GEOMETRY.zip ==========')
p = os.path.join(DRIVE, 'V52_T4C2_BINARY_GEOMETRY.zip')
zf = zipfile.ZipFile(p)
names = zf.namelist()
print('entries:', len(names))
for n in names[:60]:
    i = zf.getinfo(n)
    print(f'  {i.file_size:>10}  {n}')
if len(names) > 60:
    print(f'  ... {len(names)-60} more')
npz_inner = [n for n in names if n.lower().endswith('.npz')]
zip_inner = [n for n in names if n.lower().endswith('.zip')]
print('npz entries:', len(npz_inner), 'zip entries:', len(zip_inner))

# If there is a nested zip containing npz files, open it in memory
if zip_inner:
    nz = zip_inner[0]
    print(f'\n-- nested zip {nz}: reading in memory --')
    data = zf.read(nz)
    print('nested zip bytes:', len(data))
    zf2 = zipfile.ZipFile(io.BytesIO(data))
    n2 = zf2.namelist()
    npz2 = [x for x in n2 if x.lower().endswith('.npz')]
    print('nested entries:', len(n2), '| npz count:', len(npz2))
    print('first 5 npz:', npz2[:5])
    print('last 3 npz:', npz2[-3:])
    # inspect one npz
    if npz2:
        import numpy as np
        sample = npz2[0]
        arr = np.load(io.BytesIO(zf2.read(sample)))
        print(f'\n-- sample NPZ: {sample} --')
        for k in arr.files:
            a = arr[k]
            try:
                print(f'   {k}: shape={a.shape} dtype={a.dtype} sample={a.ravel()[:4]}')
            except Exception as e:
                print(f'   {k}: {type(a)} {e}')
elif npz_inner:
    import numpy as np
    sample = npz_inner[0]
    arr = np.load(io.BytesIO(zf.read(sample)))
    print(f'\n-- sample NPZ: {sample} --')
    for k in arr.files:
        a = arr[k]
        print(f'   {k}: shape={a.shape} dtype={a.dtype}')

print()
print('========== LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip (all entries) ==========')
p = os.path.join(DRIVE, 'LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip')
zf = zipfile.ZipFile(p)
for n in zf.namelist():
    i = zf.getinfo(n)
    print(f'  {i.file_size:>10}  {n}')
