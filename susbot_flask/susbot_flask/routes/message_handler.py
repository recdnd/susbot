from flask import Blueprint, request
import requests
import random
import re

message_bp = Blueprint("message", __name__)
API_URL = "http://127.0.0.1:5700"
last_group_msgs = {}

@message_bp.route("/message", methods=["POST"])
def handle_message():
    data = request.get_json()
    print("📨 收到消息：", data)

    if not data or data.get("post_type") != "message" or data.get("message_type") != "group":
        return "", 204

    group_id = data["group_id"]
    user_id = data["user_id"]
    raw_message = data.get("raw_message", "")
    sender = data.get("sender", {})
    name = sender.get("card") or sender.get("nickname") or str(user_id)

    match = re.match(r"sus(?:模擬|模拟|模仿)\s*(.*)", raw_message)
    target_text = ""
    if match:
        target = match.group(1).strip()
        target_id = None
        for uid, n, msg in reversed(last_group_msgs.get(group_id, [])):
            if target in n:
                target_id = uid
                break

        if not target_id:
            at_match = re.search(r"\[CQ:at,qq=(\d+)\]", target)
            if at_match:
                target_id = int(at_match.group(1))

        if target_id:
            for uid, n, msg in reversed(last_group_msgs.get(group_id, [])):
                if uid == target_id:
                    target_text = msg
                    break

        if not target_text:
            candidates = [m for m in reversed(last_group_msgs.get(group_id, [])) if m[0] != user_id]
            if candidates:
                target_text = random.choice(candidates)[2]

        if target_text:
            chance = random.random()
            exclamations = "!!" if chance < 0.2 else "!" if chance < 0.4 else ""
            reply = f"....sus「{target_text}」..{exclamations}"
        else:
            reply = "……sus全…辨認不可…"

        requests.post(f"{API_URL}/send_group_msg", json={"group_id": group_id, "message": reply})
        return "", 204

    last_group_msgs.setdefault(group_id, []).append((user_id, name, raw_message))
    if len(last_group_msgs[group_id]) > 20:
        last_group_msgs[group_id] = last_group_msgs[group_id][-20:]

    return "", 204