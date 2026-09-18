import zipfile, io, csv, os, re

DRIVE = r'C:\Users\MDP\dev\llmzip-work\drive'

# 1) variance/occupancy vector lengths from T4C3 native heterogeneity
zf = zipfile.ZipFile(os.path.join(DRIVE, 'V52_T4C3_ALL_OUTPUTS.zip'))
with zf.open('V52_T4C3_native_heterogeneity.csv') as f:
    rd = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
    hdr = next(rd)
    vi, oi = hdr.index('variance_vector'), hdr.index('occupancy_vector')
    row = next(rd)
    vl = row[vi].split(';'); ol = row[oi].split(';')
    print('variance_vector entries:', len(vl), '| first:', vl[0][:24], '| last:', vl[-1][:24])
    print('occupancy_vector entries:', len(ol), '| first:', ol[0][:24], '| last:', ol[-1][:24])
    qids_csv = [row[0]]
    for r in rd:
        qids_csv.append(r[0])
print('qids in native_heterogeneity:', len(qids_csv), 'unique:', len(set(qids_csv)))

# 2) NPZ question ids from binary geometry zip; compare
zf2 = zipfile.ZipFile(os.path.join(DRIVE, 'V52_T4C2_BINARY_GEOMETRY.zip'))
n2 = zf2.namelist()
npz = [n for n in n2 if n.lower().endswith('.npz')]
other = [n for n in n2 if not n.lower().endswith('.npz')]
qids_npz = [os.path.basename(n)[:-4] for n in npz]
print('NPZ count:', len(qids_npz), 'unique:', len(set(qids_npz)))
print('non-npz entries:', other)
print('ids match csv set:', set(qids_npz) == set(qids_csv))
print('in npz not csv:', list(set(qids_npz) - set(qids_csv))[:5])
print('in csv not npz:', list(set(qids_csv) - set(qids_npz))[:5])

# 3) V51 archive tail (entries 140+)
zf3 = zipfile.ZipFile(os.path.join(DRIVE, 'LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip'))
names = zf3.namelist()
print('\nV51 archive entries:', len(names))
for n in names[140:]:
    print('   ', name := n)
# scan all bundles for binary array extensions
print('\n=== scan every downloaded zip for array-ish extensions ===')
exts = ('.pkl', '.npy', '.npz', '.pt', '.pth', '.h5', '.hdf5', '.parquet', '.feather', '.pkl.gz', '.joblib', '.mat', '.bin', '.arrow')
for z in sorted(os.listdir(DRIVE)):
    if not z.lower().endswith('.zip'):
        continue
    try:
        zf4 = zipfile.ZipFile(os.path.join(DRIVE, z))
        hits = [n for n in zf4.namelist() if n.lower().endswith(exts)]
        if hits:
            print(f'{z}: {len(hits)} array files; sample {hits[:6]}')
    except Exception as e:
        print(z, 'ERR', e)
