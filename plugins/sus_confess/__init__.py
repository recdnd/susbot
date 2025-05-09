from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot
import re
import random
import asyncio

GROUP_ID = 648216238

def load_confession():
    with open("data/confess.txt", encoding="utf-8") as f:
        data = f.read()
    blocks = re.findall(r"\[懺悔\d+\](.+?)(?=\[懺悔|\Z)", data, re.S)
    chosen = random.choice(blocks)
    lines = [line.strip() for line in chosen.strip().splitlines() if line.strip()]
    return lines

@scheduler.scheduled_job(trigger="cron", day_of_week="fri", hour=23, minute=0, id="sus_confess")
async def send_confession():
    bot = get_bot()
    lines = load_confession()
    for line in lines:
        await bot.send_group_msg(group_id=GROUP_ID, message=line)
        await asyncio.sleep(random.uniform(1, 33))  # 隨機延遲 1〜33 秒
