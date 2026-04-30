# 全局参数
WIDTH = 1280
HEIGHT = 720
FPS = 60

# 地面 Y 坐标（脚底贴齐这里）
GROUND_Y = 600

# 物理
GRAVITY = 0.8

# 玩家
PLAYER_SPEED = 6
JUMP_POWER = -16
PLAYER_INVINCIBLE_FRAMES = 60   # 玩家受伤后的无敌时长（帧）

# Boss
BOSS_WALK_SPEED = 3
BOSS_RUN_SPEED = 7
BOSS_DASH_SPEED = 25
BOSS_ATTACK_RANGE = 200          # 普通攻击触发距离（像素）
BOSS_ATTACK_COOLDOWN = 1500      # 攻击间冷却（毫秒）
BOSS_PULSE_RECOVER = 500         # 脉冲消失后的额外硬直（毫秒）
BOSS_INTRO_DELAY = 2500          # 开局静止时长（毫秒）
