import os
import random
from datetime import datetime
from pathlib import Path

from nonebot import get_bots
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_apscheduler import scheduler

GROUP_IDS = [648216238]
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = DATA_DIR / "images"
BLESS_FILE = DATA_DIR / "bless.txt"

def get_bless_message():
    pool_map = {"food": [], "book": [], "horror": [], "free": []}

    try:
        with open(BLESS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("*"):
                    content = line[1:].strip()
                    if content.startswith("food"):
                        pool_map["food"].append(content.replace("food", "", 1).strip())
                    elif content.startswith("book"):
                        pool_map["book"].append(content.replace("book", "", 1).strip())
                    elif content.startswith("horror"):
                        pool_map["horror"].append(content.replace("horror", "", 1).strip())
                    else:
                        pool_map["free"].append(content)
    except FileNotFoundError:
        print("❌ 無法讀取 bless.txt")
        return None

    image_files = [p for p in IMAGE_DIR.rglob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]]
    if not image_files:
        print("❌ 無圖片可發送")
        return None

    img = random.choice(image_files)
    img_str = str(img).lower()
    if "food" in img_str:
        msg = random.choice(pool_map["food"] or pool_map["free"])
    elif "book" in img_str:
        msg = random.choice(pool_map["book"] or pool_map["free"])
    elif "horror" in img_str:
        msg = random.choice(pool_map["horror"] or pool_map["free"])
    else:
        msg = random.choice(pool_map["free"] or ["願你擁有平靜的一日."])

    season = datetime.now().month
    if season in [3, 4, 5]:
        prefix = "時值春日. "
    elif season in [6, 7, 8]:
        prefix = "夏意正盛. "
    elif season in [9, 10, 11]:
        prefix = "正值收穫季. "
    else:
        prefix = "凜冬已至. "

    full_msg = f"又是一個週末. {prefix}{msg}"
    return MessageSegment.image(f"file:///{img}") + "\n" + full_msg

# ✅ 測試中每分鐘觸發一次
#@scheduler.scheduled_job(trigger="cron", minute="*/1", id="sus_bless")
@scheduler.scheduled_job(trigger="cron", day_of_week="fri", hour=7, minute=0, id="sus_bless")
async def send_bless():
    bots = get_bots()
    if not bots:
        print("❌ 無 bot 實例可用")
        return
    bot = list(bots.values())[0]

    bless_msg = get_bless_message()
    if bless_msg:
        for gid in GROUP_IDS:
            try:
                await bot.send_group_msg(group_id=gid, message=bless_msg)
                print(f"✅ 發送成功至 {gid}")
            except Exception as e:
                print(f"⚠️ 發送失敗: {e}")
