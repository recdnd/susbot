import os
import random
import glob
from datetime import datetime

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_apscheduler import scheduler

# 配置
GROUPS = ["648216238"]
MEME_FOLDER = "meme/r_now_meme"
USED_LIST_PATH = "used_images.txt"
BASE_DATE = datetime(2024, 5, 3)

def get_all_images():
    return glob.glob(os.path.join(MEME_FOLDER, "**", "*.*"), recursive=True)

def get_unused_image():
    all_images = get_all_images()
    if not os.path.exists(USED_LIST_PATH):
        used = set()
    else:
        with open(USED_LIST_PATH, "r", encoding="utf-8") as f:
            used = set(line.strip() for line in f)

    available = [img for img in all_images if os.path.basename(img) not in used]
    if not available:
        return None

    chosen = random.choice(available)
    with open(USED_LIST_PATH, "a", encoding="utf-8") as f:
        f.write(os.path.basename(chosen) + "\n")
    return chosen

def should_run_today():
    today = datetime.now().date()
    return (today - BASE_DATE.date()).days % 2 == 0

async def send_meme_to_groups():
    bot = get_bot()
    path = get_unused_image()
    if not path:
        return
    for group_id in GROUPS:
        await bot.send_group_msg(
            group_id=int(group_id),
            message=MessageSegment.image(f"file:///{os.path.abspath(path)}")
        )

# ✅ 啟動時就註冊定時任務（固定 12:00，若當天應發送）
if should_run_today():
    rand_minute = random.randint(0, 59)
    scheduler.add_job(
        send_meme_to_groups,
        "cron",
        hour=12,
        minute=rand_minute,
        id="sus_meme_auto",
        replace_existing=True,
    )
