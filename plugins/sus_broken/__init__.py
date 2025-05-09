
import random

skip_words = {
    "我", "你", "要", "可能", "就是", "其實", "其实",
    "而且", "所以", "如果", "但是", "来", "会",
    "有", "好像", "感觉", "确实"
}

def make_broken_summary(msg_list):
    fragments = []
    for msg in msg_list:
        for part in msg.split():
            if part and part not in skip_words:
                fragments.append(part)
    if not fragments:
        return "..."
    random.shuffle(fragments)
    selected = fragments[:random.randint(1, 5)]
    return "…".join(selected) + "..."

def make_broken_comment(msg_list):
    fragments = []
    for msg in msg_list:
        for part in msg.split():
            if part and part not in skip_words:
                fragments.append(part)
    if not fragments:
        return "..."
    random.shuffle(fragments)
    selected = fragments[:random.randint(6, 12)]
    return "…".join(selected) + "..."
