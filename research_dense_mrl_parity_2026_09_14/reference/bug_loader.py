# Gemini'nin load_unique_longmemeval_turns fonksiyonunun gercek veri uzerinde testi
import json, glob, os
DATA_DIR = r"C:\Users\MDP\dev\llmzip-work\drive"

def load_unique_longmemeval_turns(data_dir, target_count=500):
    unique_texts = set()
    json_files = glob.glob(os.path.join(data_dir, "**/*.json"), recursive=True) + \
                 glob.glob(os.path.join(data_dir, "**/*.jsonl"), recursive=True)
    print("  bulunan dosya:", [os.path.basename(p) for p in json_files][:5])
    for fpath in json_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    data = json.loads(line) if fpath.endswith(".jsonl") else json.load(f)
                    if isinstance(data, dict):
                        messages = data.get("messages", data.get("conversation", []))
                        for m in messages:
                            c = m.get("content","").strip()
                            if len(c) > 20: unique_texts.add(c)
                    elif isinstance(data, list):
                        for item in data:
                            for m in item.get("messages", item.get("conversation", [])):
                                c = m.get("content","").strip()
                                if len(c) > 20: unique_texts.add(c)
                    if len(unique_texts) >= target_count: break
        except Exception as e:
            print("  yutulan istisna:", type(e).__name__, str(e)[:110])
            continue
        if len(unique_texts) >= target_count: break
    texts = list(unique_texts)[:target_count]
    print(f"  -> toplanan benzersiz metin: {len(texts)}")
    if len(texts) < 100:
        raise ValueError("Yetersiz metin havuzu! En az 100 tekil metin gereklidir.")
    return texts

print("Gemini yukleyicisi, gercek LongMemEval dizininde:")
try:
    load_unique_longmemeval_turns(DATA_DIR)
    print("SONUC: calisti")
except Exception as e:
    print("SONUC: BASARISIZ ->", type(e).__name__, e)
