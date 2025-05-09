import random
import os
from pathlib import Path

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_apscheduler import scheduler

GROUP_ID = 648216238
IMAGE_ROOT = Path("data/memes")
USED_RECORD_FILE = Path("data/.used_meme_files.txt")

def get_all_image_files():
    return [p for p in IMAGE_ROOT.rglob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]]

def load_used_record():
    if USED_RECORD_FILE.exists():
        return set(USED_RECORD_FILE.read_text(encoding="utf-8").splitlines())
    return set()

def save_used_record(record: set):
    USED_RECORD_FILE.write_text("\n".join(record), encoding="utf-8")

GROUP_IDS = [648216238, 710471582]  # 支援多群

async def send_nightly_image():
    bot = get_bot()

    used = load_used_record()
    all_images = get_all_image_files()

    reusable = [p for p in all_images if any("r_" in part for part in p.parts)]
    one_time = [p for p in all_images if not any("r_" in part for part in p.parts)]

    remaining_files = [p for p in one_time if str(p) not in used]

    if remaining_files:
        choice = random.choice(remaining_files)
        used.add(str(choice))
        save_used_record(used)
    elif reusable:
        choice = random.choice(reusable)
    else:
        print("[sus_pic] ❌ 無圖片可發送")
        return

    for gid in GROUP_IDS:
        try:
            await bot.send_group_msg(
                group_id=gid,
                message=MessageSegment.image(f"file:///{choice.absolute()}")
            )
            print(f"[sus_pic] ✅ 已發送至 {gid}")
        except Exception as e:
            print(f"[sus_pic] ⚠️ 發送至 {gid} 失敗: {e}")

# ✅ 註冊定時任務
scheduler.add_job(
    send_nightly_image,
    "cron",
    hour=3,
    minute=30,
    id="suspic",
    replace_existing=True,
)
