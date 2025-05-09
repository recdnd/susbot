from nonebot import get_driver
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Message
from pathlib import Path
import random
import json
from .meme_utils import get_available_images, update_record
# 常量定義
MAIN_GROUP = 648216238

# 每天早8、中12、晚7定時發送
@scheduler.scheduled_job("cron", hour=8, minute=0)
@scheduler.scheduled_job("cron", hour=12, minute=0)
@scheduler.scheduled_job("cron", hour=19, minute=0)
async def send_daily_meme():
    try:
        imgs, repeat, _ = get_available_images()
        if not imgs:
            imgs = list(repeat)
        if not imgs:
            print("⛔ 無梗圖可發送")
            return

        img = random.choice(imgs)
        msg = Message(f"[CQ:image,file=file:///{img}]")

        bots = list(get_driver().bots.values())
        if not bots:
            print("⚠️ 無可用 bot 實例")
            return

        await bots[0].send_group_msg(group_id=MAIN_GROUP, message=msg)
        update_record(img)
        print(f"✅ 已向主群 {MAIN_GROUP} 發送梗圖：{img}")
    except Exception as e:
        print(f"❌ 梗圖發送失敗: {e}")
