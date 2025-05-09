import time
from collections import defaultdict

group_enabled = defaultdict(lambda: False)
group_mode = defaultdict(lambda: "中")
group_last_image_time = defaultdict(lambda: 0)
group_last_sent_time = defaultdict(lambda: 0)
group_cooldowns = {
    "低": 86400,
    "中": 3600,
    "高": 0
}

group_waiting_strength = set()
group_waiting_strength_count = defaultdict(lambda: 0)

def enable_sticker(group_id: int):
    group_enabled[group_id] = True
    group_last_sent_time[group_id] = 0

def disable_sticker(group_id: int):
    group_enabled[group_id] = False

def is_enabled(group_id: int) -> bool:
    return group_enabled[group_id]

def set_strength(group_id: int, level: str):
    group_mode[group_id] = level

def get_strength(group_id: int) -> str:
    return group_mode[group_id]

def update_last_image_time(group_id: int):
    group_last_image_time[group_id] = time.time()

def get_last_image_time(group_id: int) -> float:
    return group_last_image_time[group_id]

def in_cooldown(group_id: int) -> bool:
    now = time.time()
    mode = get_strength(group_id)
    cooldown = group_cooldowns[mode]
    return now - group_last_sent_time[group_id] < cooldown

def update_last_sent_time(group_id: int):
    group_last_sent_time[group_id] = time.time()

def reset_waiting_count(group_id: int):
    group_waiting_strength_count[group_id] = 0

def increment_waiting_count(group_id: int):
    group_waiting_strength_count[group_id] += 1

def get_waiting_count(group_id: int) -> int:
    return group_waiting_strength_count[group_id]

def stop_waiting(group_id: int):
    if group_id in group_waiting_strength:
        group_waiting_strength.discard(group_id)
        group_waiting_strength_count[group_id] = 0
