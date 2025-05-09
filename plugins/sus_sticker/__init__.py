import os
import random
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, GroupMessageEvent
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Message
from plugins.sus_utils import subscribe_group_message

# 📁 貼圖目錄
STICKER_DIR = Path("data/sticker")
STICKER_WEIGHTED_FOLDERS = {
    "sticker_r": 3,
    "sticker_sr": 3,
    "sticker_bad": 0.2,
    "sticker_ssr": 1
}

# 📌 群組設定
MAIN_GROUP = [648216238, 375171587, 710471582]
SECONDARY_GROUPS = [894772961, 873338015, 656677831]
ALLOWED_GROUPS = { *MAIN_GROUP, *SECONDARY_GROUPS }

# ⏱ 狀態追蹤
recent_activity = {}
last_sticker_time = {}

# 🎯 圖片觸發貼圖
image_trigger = on_message(priority=1, block=False)

def get_weighted_sticker_files() -> list[Path]:
    weighted_list = []
    for folder, weight in STICKER_WEIGHTED_FOLDERS.items():
        sub_dir = STICKER_DIR / folder
        if not sub_dir.exists():
            continue
        for file in sub_dir.glob("**/*"):
            if file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                weighted_list.extend([file] * int(weight))
    return weighted_list

@image_trigger.handle()
async def _(event: MessageEvent):
    group_id = getattr(event, "group_id", None)
    if group_id is None or group_id not in ALLOWED_GROUPS:
        return

    if not any(seg.type == "image" for seg in event.message):
        return

    now = datetime.now()
    if group_id not in MAIN_GROUP:
        last_time = last_sticker_time.get(group_id)
        if last_time and (now - last_time) < timedelta(hours=2):
            print(f"[SKIP] 副群組 {group_id} 貼圖CD未到")
            return

    if recent_activity.get(group_id, False):
        print(f"[SKIP] {group_id} 正在等待中")
        return

    delay = random.randint(3, 98)
    recent_activity[group_id] = True
    print(f"[{group_id}] 偵測圖片，等待 {delay} 秒...")

    responded = False

    def callback(resp_event: GroupMessageEvent):
        nonlocal responded
        if resp_event.group_id == group_id and resp_event.time > event.time:
            responded = True
            print(f"[{group_id}] 有人發言！阻止貼圖")

    unsubscribe = subscribe_group_message(callback)

    try:
        await asyncio.sleep(delay)
    finally:
        unsubscribe()

    if not responded:
        print(f"[{group_id}] 無人發言，準備發送貼圖")
        all_stickers = get_weighted_sticker_files()
        if all_stickers:
            chosen = random.choice(all_stickers)
            image_path = chosen.resolve()
            message = MessageSegment.image(f"file:///{image_path}")

            if "sticker_ssr" in str(chosen).lower():
                message += "\n✨ 發現了 SSR 級貼紙...!"

            await image_trigger.send(message)
            last_sticker_time[group_id] = now
        else:
            print("⚠️ 無可用貼圖")
    else:
        print(f"[{group_id}] 發送取消")

    recent_activity[group_id] = False

# 🧪 手動測試貼圖指令
sticker_cmd = on_command("sticker", aliases={"/貼圖測試"}, priority=1)

@sticker_cmd.handle()
async def _(event: MessageEvent):
    all_stickers = get_weighted_sticker_files()
    if not all_stickers:
        await sticker_cmd.finish("⚠️ 無可用貼圖")
        return

    chosen = random.choice(all_stickers)
    image_path = chosen.resolve()
    message = MessageSegment.image(f"file:///{image_path}")

    if "sticker_ssr" in str(chosen).lower():
        message += "\n✨ 解鎖了 SSR 貼紙...!"

    await sticker_cmd.finish(message)