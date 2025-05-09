from flask import Blueprint, request
from flask_susbot.routes.sticker_handler import handle_message as handle_sticker
from flask_susbot.routes.message_handler import handle_message as handle_talk
from flask_susbot.config.state_manager import group_waiting_strength

dispatcher_bp = Blueprint("dispatcher", __name__)

@dispatcher_bp.route("/message", methods=["POST"])
def handle_message():
    data = request.get_json()
    if not data or data.get("message_type") != "group":
        return "", 204

    group_id = data["group_id"]
    message_chain = data.get("message", [])
    raw_text = "".join([seg.get("data", {}).get("text", "") for seg in message_chain if seg.get("type") == "text"])
    text = raw_text.strip()

    print(f"[🛰 Dispatcher] 收到訊息: {text}")

    if any(seg.get("type") == "image" for seg in message_chain):
        print("[🖼] 偵測到圖片訊息，交給貼圖模組")
        return handle_sticker()

    if group_id in group_waiting_strength:
        print("[⏳] 貼圖等待強度中，交給貼圖模組")
        return handle_sticker()

    sticker_keywords = [
        "貼紙", "贴纸", "貼圖", "贴图", "susstamp", "sussticker",
        "強度", "频", "頻", "调", "調", "改", "模式", "低", "中", "高"
    ]
    if "sus" in text and any(kw in text for kw in sticker_keywords):
        print("[➡️] 發送至：貼圖模組")
        return handle_sticker()

    talk_keywords = ["模擬", "模拟", "說話", "語錄", "sus模擬", "sus說話"]
    if "sus" in text and any(kw in text for kw in talk_keywords):
        print("[➡️] 發送至：講話模組")
        return handle_talk()

    print("[❔] 無匹配指令，忽略")
    return "", 204
