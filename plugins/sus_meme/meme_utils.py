import json
from pathlib import Path

MEME_DIR = Path("data/memes")
DATA_FILE = Path("data/meme_record.json")

def get_all_images():
    return [
        str(p) for p in MEME_DIR.rglob("*") 
        if p.suffix.lower() in (".png", ".jpg", ".webp", ".gif")
    ]

def get_available_images():
    used = set()
    repeat = set()

    if DATA_FILE.exists():
        with DATA_FILE.open(encoding="utf-8") as f:
            record = json.load(f)
        used = set(record.get("used", []))
        repeat = set(record.get("repeat", []))
    else:
        record = {"used": [], "repeat": []}

    all_imgs = get_all_images()
    new_imgs = [
        img for img in all_imgs
        if "/r_" in img.replace("\\", "/") or img not in used
    ]

    return new_imgs, repeat, record

def update_record(img_path: str):
    try:
        if DATA_FILE.exists():
            with DATA_FILE.open(encoding="utf-8") as f:
                record = json.load(f)
        else:
            record = {"used": [], "repeat": []}

        if "/r_" in img_path.replace("\\", "/"):
            if img_path not in record["repeat"]:
                record["repeat"].append(img_path)
        elif img_path not in record["used"]:
            record["used"].append(img_path)

        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"更新記錄文件失敗: {e}")
