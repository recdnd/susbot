from flask import Blueprint, request
import random, os, time, threading
import requests
import base64
import mimetypes
from flask_susbot.config.whitelist import WHITELISTED_GROUPS
from flask_susbot.config.state_manager import (
    is_enabled, enable_sticker, disable_sticker,
    set_strength, get_strength,
    update_last_image_time, get_last_image_time,
    update_last_sent_time, in_cooldown,
    group_waiting_strength,
    reset_waiting_count, increment_waiting_count,
    get_waiting_count, stop_waiting
)
from urllib.parse import quote


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STICKER_DIR = os.path.join(BASE_DIR, "data", "stickers")

sticker_bp = Blueprint("sticker", __name__)
API_URL = "http://127.0.0.1:5700/send_group_msg"

TRIGGER_KEYWORDS = {
    "sus貼紙", "sus贴纸", "sus貼圖", "sus贴图",
    "susstamp", "sussticker",
    "sus模擬", "sus模拟",
    "sus調", "sus调", "sus頻", "sus频", 
    "sus模式", "sus模式改", "sus改", "sus改一改",
    "sus亂貼", "sus乱贴"
}

CLOSE_KEYWORDS = {"sus閉嘴", "sus闭嘴", "闭嘴sus"}
OPEN_KEYWORDS = {"對不起sus", "原諒sus", "原谅sus", "对不起sus"}
STRENGTH_WORDS = {"低", "中", "高"}

def send_group_msg(group_id, message):
    try:
        payload = {
            "group_id": group_id,
            "message": message,
            "auto_escape": False
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(API_URL, json=payload, headers=headers)
        print(f"[📤] 發送訊息回應: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[❌] 發送失敗: {e}")

def send_random_sticker(group_id):
    print(f"[📂] STICKER_DIR = {STICKER_DIR}")
    print("[📁] 所有可用貼圖如下：")
    try:
        files = []
        for root, _, filenames in os.walk(STICKER_DIR):
            print(f"➡️ 掃描資料夾：{root}")
            for f in filenames:
                print(f"    - 發現：{f}")
                if f.lower().endswith((".jpg", ".png", ".gif", ".webp")):
                    full_path = os.path.join(root, f)
                    files.append(full_path)

        if not files:
            print(f"[⚠️] 沒有可用貼圖於：{STICKER_DIR}")
            return

        chosen = random.choice(files)

        # 讀取並 base64 編碼圖片
        with open(chosen, "rb") as img_file:
            img_bytes = img_file.read()
            b64 = base64.b64encode(img_bytes).decode()

        # 推測 MIME 類型
        mime_type = mimetypes.guess_type(chosen)[0] or "image/png"

        # 組合 base64 CQ碼格式
        cq_code = f"[CQ:image,file=base64://{b64}]"

        print(f"[🖼] 發送貼圖：{cq_code}")

        send_group_msg(group_id, cq_code)
        update_last_sent_time(group_id)

    except Exception as e:
        print(f"[❌] 發圖失敗: {e}")


def schedule_sticker(group_id):
    def delayed_send():
        delay = random.randint(3, 196)
        time.sleep(delay)
        if not in_cooldown(group_id) and is_enabled(group_id):
            if time.time() - get_last_image_time(group_id) >= delay:
                send_random_sticker(group_id)
    threading.Thread(target=delayed_send, daemon=True).start()

@sticker_bp.route("/message", methods=["POST"])
def handle_message():
    data = request.get_json()
    if not data or data.get("message_type") != "group":
        return {"status": "Ignored"}, 200

    self_ids = {3585262318}
    if data.get("sender", {}).get("user_id") in self_ids:
        return {"status": "Ignored"}, 200

    group_id = data["group_id"]
    message_chain = data.get("message", [])
    raw_text = "".join([seg.get("data", {}).get("text", "") for seg in message_chain if seg.get("type") == "text"])
    text = raw_text.strip()
    print(f"[📩] group_id = {group_id} | text = {text}")
    if not any(k in text for k in TRIGGER_KEYWORDS) and group_id not in group_waiting_strength:
        return {"status": "Ignored"}, 200

    if any(k in text for k in CLOSE_KEYWORDS) or ("嘴" in text and "@sus" in text):
        print(f"[🔴] 關閉貼圖功能：{group_id}")
        disable_sticker(group_id)
        send_group_msg(group_id, random.choice(["..嗚嗚...sus不發了...", "對...對不起....sus不發了.."]))
        return {"status": "Closed"}, 200

    if any(k in text for k in OPEN_KEYWORDS) or ("不起" in text and "@sus" in text):
        if group_id not in group_waiting_strength:
            print(f"[🟢] 啟用貼圖功能：{group_id}")
            enable_sticker(group_id)
            group_waiting_strength.add(group_id)
            reset_waiting_count(group_id)
            send_group_msg(group_id, "sus可以貼圖嗎..?⭐選擇強度[低//中/高]")
        return {"status": "Opened"}, 200

    extra_keywords = ["調", "频", "強度", "strength", "mode", "改"]
    if "sus" in text and any(keyword in text for keyword in extra_keywords):
        if group_id not in group_waiting_strength:
            print(f"[⚙️] 收到貼圖頻率調整請求：{group_id}")
            group_waiting_strength.add(group_id)
            reset_waiting_count(group_id)
            send_group_msg(group_id, "⭐選擇貼圖強度[低/中/高]")
        return {"status": "Adjust Strength"}, 200

    print(f"[DEBUG] 是否在白名單: {group_id in WHITELISTED_GROUPS}")
    print(f"[DEBUG] 是否命中觸發詞: {any(k in text for k in TRIGGER_KEYWORDS)}")

    if group_id in group_waiting_strength:
        for word in STRENGTH_WORDS:
            if word in text:
                print(f"[✅] 強度設定為：{word}")
                set_strength(group_id, word)
                stop_waiting(group_id)
                send_group_msg(group_id, f"當前難度為 {word}..!\n關閉指令是“閉嘴sus和對不起sus…at+指令也可以喔!”")
                schedule_sticker(group_id)
                return {"status": "Strength Set"}, 200
        increment_waiting_count(group_id)
        if get_waiting_count(group_id) >= 10:
            print(f"[⚠️] 超過10次未成功設定強度，終止監聽")
            stop_waiting(group_id)
        return {"status": "Waiting Strength"}, 200

    if group_id not in WHITELISTED_GROUPS:
        if any(k in text for k in TRIGGER_KEYWORDS):
            if group_id not in group_waiting_strength:
                print(f"[🟡] 非白名單群觸發貼圖流程：{group_id}")
                enable_sticker(group_id)
                group_waiting_strength.add(group_id)
                reset_waiting_count(group_id)
                send_group_msg(group_id, "sus可以貼圖嗎..?⭐選擇強度[低//中/高]")
            return {"status": "Triggered"}, 200

    if is_enabled(group_id) and not in_cooldown(group_id):
        for seg in message_chain:
            if seg["type"] == "image":
                update_last_image_time(group_id)
                schedule_sticker(group_id)
                return {"status": "Scheduled"}, 200  # ← 給明確回應！

    # ✅ 統一保底 return
    return {"status": "OK"}, 200
