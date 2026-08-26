import random
import time
import os

# 定义屏幕坐标（需根据设备实际分辨率调整！）
SCREEN_WIDTH = 3000
SCREEN_HEIGHT = 1920

# 操作区域坐标（示例，需自行校准）
MOVE_AREA = (500, 800)      # 角色移动摇杆区域
ATTACK_BTN = (2485, 1512)    # 攻击按钮
JUMP_BTN = (2777, 1347)      # 跳跃按钮
FAST_BTN = (2777, 1670)      # 跳跃按钮
def random_sleep(min=1, max=3):
    """随机延迟"""
    time.sleep(random.uniform(min, max))

def adb_tap(x, y):
    """模拟点击"""
    os.system(f"adb shell input tap {x} {y}")

def adb_swipe(x1, y1, x2, y2, duration=100):
    """模拟滑动（用于转向）"""
    os.system(f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}")

def random_move():
    """随机移动方向"""
    # 长按摇杆区域并随机滑动方向
    dx = random.randint(-200, 200)
    dy = random.randint(-200, 200)
    adb_swipe(MOVE_AREA[0], MOVE_AREA[1],
              MOVE_AREA[0]+dx, MOVE_AREA[1]+dy, 1000)
    random_sleep(2, 5)

def random_attack():
    """随机攻击"""
    adb_tap(*ATTACK_BTN)
    random_sleep(0.5, 1.5)
    # 随机连击次数
    for _ in range(random.randint(1, 5)):
        adb_tap(*ATTACK_BTN)
        time.sleep(0.2)

def random_jump():
    """随机跳跃"""
    adb_tap(*JUMP_BTN)
    random_sleep(0.5, 1)

def random_fast():
    """随机跳跃"""
    adb_tap(*FAST_BTN)
    random_sleep(0.5, 1)

def random_rotate():
    """随机转换视角"""
    dx = random.randint(-300, 300)
    dy = random.randint(-300, 300)
    adb_swipe(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
              SCREEN_WIDTH//2+dx, SCREEN_HEIGHT//2+dy, 200)
    random_sleep(0.5, 1)

if __name__ == "__main__":
    try:
        while True:
            # 随机选择操作
            action = random.choice([
                random_move,
                random_attack,
                random_jump,
                random_rotate
            ])
            action()
    except KeyboardInterrupt:
        print("脚本已停止")