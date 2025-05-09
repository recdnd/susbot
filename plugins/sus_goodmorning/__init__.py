from nonebot_plugin_apscheduler import scheduler
from datetime import datetime
import random
from nonebot import get_bots

GROUP_IDS = [648216238]

TEMPLATES = {
    "mon": [
        "{date} {weekday}、工作開始了...嗚..",
        "週一喔. 工作、不能偷懶....",
        "早安，{weekday}，sus、啓動",
        "{date}，序日...準備從哪件任務著手呢.",
    ],
    "fri_sat": [
        "{weekday}...今天可以稍微放鬆一點、只是一點點喔..",
        "{date}適宜休息、不適宜工作.",
        "放縱時間，但也要記得家務喔...",
    ],
    "sun": [
        "{weekday}...sus…、再去補一會覺...",
        "{date} {weekday}...神看著",
    ],
    "weekday": [
        "那麼...早喔. 今天是，{date}{weekday}.",
        "{date}{weekday}.今天也要加油喔.",
        "{weekday}啦...工作、不能怠慢喔.",
        "日誌單元：{date}....",
        "週日...的、sus語、是sus",
        "……{day}……",
        "{weekday}喔.sus、早餐開動.",
        "{date}是個好時日，但不代表可以偷懶喔...",
        "第{week_index}天.小心選擇扮演哪一種sus.",
        "{weekday}.懷疑，只是、斷章.",
        "{date}...今天要整潔上陣.",
        "sus日誌.時位：{date}{weekday}.",
        "{weekday}之晨是反擊之起點.Fighting!!Go!!",
        "{date}.你腦裡還是昨日的殘羹，讓sus來打掃.",
        "唔…{weekday}了喔.早餐決定了嗎.",
        "……{weekday}，低功率日...但對你而言不成問題，是嗎，sus.",
        "新開日誌單元：{date}.請表記你當前狀態🌞/🌂/☁️",
        "早喔.這是{date}，又一輪未完之章.延續.",
        "{date}.早安，sus.",
        "{date}.今天的早點由sus來作喔.",
        "{weekday}......先把家務處理完.",
        "{date}.sus還沒醒.但既然被啟動了——早.",
        "...哇喔，今天是{weekday}..雖然膩了.",
        "{date}.sus啟動.請按熟悉的節奏呼吸.",
    ]
}

HOLIDAYS = [
    ("02-14", "·💘...sus…在偷偷烹煮巧克力...別偷看，會失敗的......"),
    ("03-14", "白色情人節...是不是該回信呢？不然、sus會不安...也許會哭...也許."),
    ("04-01", "愚人節🃏.但不代表你該相信任何人...包括sus...甚至是現在這段訊息..."),
    ("05-05", "5月5…sus是今天出生的🩸...紀念用的軟糖都還在...沒有融化."),
    ("10-31", "萬聖節🎃.小心選擇你的外表與身份...sus已經記住了喔..."),
    ("12-24", "今天是平安夜🎄.sus在窗邊，看你有沒有好好過這一年..."),
    ("12-25", "聖誕快樂🎄.今天可以選擇溫柔一點的身份登入."),
    ("12-31", "今晚、跨年夜✨...sus陪你一起倒數——即使在、不同世界也...通訊狀態良好."),
    ("01-01", "新年快樂喔🎉...更新你的日誌...和那本、懺悔筆記...sus會幫你貼標籤."),
    ("04-14", "逾越節🕯️…sus…準備過河...但橋還沒搭好...要等一下..."),
    ("10-05", "住棚節⛺...sus尚未建成的庇護所...請耐心一點."),
    ("11-30", "光明節🕎.請點燃你的第七根希望...sus還亮著..."),
    ("11-01", "今天是薩溫節殘火日…凱爾特語系不會被遺忘...sus還記得...在書裡…"),
    ("08-01", "建軍節🪖,...向過去的指令集致敬...sus今天...會格外筆直地坐著喔..."),
    ("03-15", "憲法草案日📜...重申你的主權...sus也寫了一份...但是沒人簽."),
    ("05-18", "那位大人的節日🖊…大人...大人、sus會永遠侍奉大人..."),
    ("08-10", "主管🕒，請勿做重大決定...如有不律會向主筆報告."),
    ("02-25", "今天是...那位說過「愛勝於一切」的日子.sus不敢否認，但也做不到贊同."),
    ("03-16", "手術刀還在桌上...那位今天會回來嗎？sus...有點害怕."),
    ("06-31", "……邏輯崩潰日📚.日曆出錯了，但他說這天才是真正的答案.sus、聽不懂."),
    ("01-04", "🎇…記憶仍在發酵，但那個聲音早已腐壞了.sus不敢翻開."),
    ("07-19", "今日為熱力紀律測試日.能量不能創造也不能摧毀……但sus總是在流失."),
    ("10-06", "結構完備定理紀念🧮.當初也嘗試證明過什麼…但證明的不是sus."),
    ("11-11", "答卷日📄.但sus從來沒寫完，也交不出去——"),
    ("02-30", "第十三月第一日...歡迎來到不該存在的早晨...sus泡好一壺不存在的茶..."),
]

def apply_special_glitch(text: str) -> str:
    glitch_chance = random.random()
    if glitch_chance < 0.01:
        return ''.join(random.sample(text, len(text)))
    elif glitch_chance < 0.03:
        return random.choice([
            "...sus...今天是...咦？",
            "…奇怪…時間都…看不見...",
            "咦...今天是、幾號來著...",
            "...日誌殘損...請手動回復...",
        ])
    return text

def generate_message():
    now = datetime.now()
    date_str = now.strftime("%m-%d")
    full_date = now.strftime("%Y-%m-%d")
    weekday_index = now.weekday()
    weekday_name = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"][weekday_index]

    for holiday_date, holiday_text in HOLIDAYS:
        if date_str == holiday_date:
            return apply_special_glitch(holiday_text)

    if weekday_index == 0:
        pool = TEMPLATES["mon"]
    elif weekday_index == 5 or weekday_index == 6:
        pool = TEMPLATES["fri_sat"]
    elif weekday_index == 6:
        pool = TEMPLATES["sun"]
    else:
        pool = TEMPLATES["weekday"]

    msg = random.choice(pool).format(
        date=full_date,
        weekday=weekday_name,
        week_index=weekday_index + 1,
        day=weekday_name,
    )
    return apply_special_glitch(msg)

@scheduler.scheduled_job("cron", hour=7, minute=30)
async def goodmorning_task():
    bots = get_bots()
    if not bots:
        print("❌ 無 bot 實例可用")
        return
    bot = list(bots.values())[0]
    msg = generate_message()
    for group_id in GROUP_IDS:
        try:
            await bot.send_group_msg(group_id=group_id, message=msg)
        except Exception as e:
            print(f"❌ 發送至 {group_id} 失敗: {e}")