import random
import sys
import time
import os
import pygame

# 资源路径处理函数
def resource_path(relative_path):
    """ 获取打包后资源的绝对路径 """
    if getattr(sys, 'frozen', False):  # 判断是否在打包后的环境中
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 初始化Pygame
pygame.init()
try:
    pygame.mixer.init()  # 尝试初始化音频系统
    audio_available = True
except pygame.error:
    print("警告: 无法初始化音频系统，游戏将在无声模式下运行")
    audio_available = False

# 屏幕尺寸
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 方块尺寸
BLOCK_SIZE = 40

# 游戏区域尺寸
GAME_AREA_WIDTH = 6  # 方块列数
GAME_AREA_HEIGHT = 15  # 方块行数

# 游戏区域位置
GAME_AREA_X = 300
GAME_AREA_Y = 50

# 对手游戏区域位置
OPPONENT_AREA_X = 800
OPPONENT_AREA_Y = 50

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (147, 112, 219)
ORANGE = (255, 165, 0)
CYAN = (135, 206, 250)
RED = (255, 99, 71)

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("原神八奇乱斗复刻版")

# 加载背景图片
background = pygame.image.load(resource_path(os.path.join("images", "background_b.png")))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载方块图片
block_images = {
    "blue": pygame.image.load(resource_path(os.path.join("images", "blue block.png"))),
    "green": pygame.image.load(resource_path(os.path.join("images", "green block.png"))),
    "purple": pygame.image.load(resource_path(os.path.join("images", "purple block.png"))),
    "yellow": pygame.image.load(resource_path(os.path.join("images", "yellow block.png"))),
    "stone": pygame.image.load(resource_path(os.path.join("images", "stone.png")))
}

# 调整方块图片大小
for color in block_images:
    block_images[color] = pygame.transform.scale(block_images[color], (BLOCK_SIZE, BLOCK_SIZE))

# 加载八奇乱斗角色图片
character_images = {}
character_files = {
    "胡桃": "hutao.gif",
    "蓝砚": "lanyan.gif",
    "魈": "xiao.gif",
    "刻晴": "keqing.gif",
    "藤人": "hutao.gif"  # 暂时使用胡桃的图片作为藤人的图片
}

# 加载角色图片
for character, filename in character_files.items():
    try:
        # 尝试加载图片
        image_path = os.path.join("images", "characters", filename)
        char_img = pygame.image.load(resource_path(image_path))
        # 调整大小为100x100像素
        char_img = pygame.transform.scale(char_img, (100, 100))
        character_images[character] = char_img
        print(f"成功加载角色图片: {character}")
    except Exception as e:
        print(f"无法加载角色图片 {character}: {e}")
        # 创建一个临时的角色图片作为备用
        char_img = pygame.Surface((100, 100))
        if character == "胡桃":
            char_img.fill(RED)  # 红色
        elif character == "蓝砚":
            char_img.fill(CYAN)  # 蓝色
        elif character == "魈":
            char_img.fill((144, 238, 144))  # 绿色
        elif character == "刻晴":
            char_img.fill(PURPLE)  # 紫色
        # 添加文字
        font = pygame.font.SysFont(None, 24)
        text = font.render(character, True, WHITE)
        text_rect = text.get_rect(center=(50, 50))
        char_img.blit(text, text_rect)
        character_images[character] = char_img

# 加载背景音乐
if audio_available:
    try:
        pygame.mixer.music.load(resource_path(os.path.join("sounds", "z8g15-g2l2u.wav")))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # -1表示循环播放
    except pygame.error:
        print("警告: 无法加载背景音乐")

# 加载音效
sound_effects = {}
if audio_available:
    try:
        # 使用背景音乐作为所有音效的替代
        background_sound = pygame.mixer.Sound(resource_path(os.path.join("sounds", "z8g15-g2l2u.wav")))
        # 设置较低的音量，避免与背景音乐冲突
        background_sound.set_volume(0.2)
        # 为所有音效使用同一个音频文件
        sound_effects["clear"] = background_sound
        sound_effects["drop"] = background_sound
        sound_effects["rotate"] = background_sound
        sound_effects["game_over"] = background_sound
        print("成功加载音效")
    except pygame.error:
        print("警告: 无法加载音效")

# 字体
font_path = resource_path(os.path.join("fonts", "simhei.ttf"))
try:
    game_font = pygame.font.Font(font_path, 36)
    small_font = pygame.font.Font(font_path, 24)
    large_font = pygame.font.Font(font_path, 48)
    print("成功加载中文字体")
except pygame.error:
    print("警告: 无法加载中文字体，使用系统默认字体")
    game_font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    large_font = pygame.font.SysFont(None, 48)

# 游戏状态
MENU = 0
CHARACTER_SELECT = 1
GAME = 2
GAME_OVER = 3

current_state = MENU

# 菜单选项
menu_options = ["开始游戏", "角色选择", "退出"]
selected_option = 0

# 角色选择
character_options = ["胡桃", "蓝砚", "魈", "刻晴", "藤人"]
selected_character = 0
current_character = "胡桃"  # 默认角色
opponent_character = "蓝砚"  # 默认对手角色

# 角色技能定义
characters = {
    "胡桃": {
        "skill_name": "蝶引来生",
        "skill_description": "将场上所有同色方块变为当前方块颜色",
        "cooldown": 15
    },
    "蓝砚": {
        "skill_name": "水月",
        "skill_description": "将当前方块立即下落并消除下方一行方块",
        "cooldown": 8
    },
    "魈": {
        "skill_name": "靖妖傩舞",
        "skill_description": "消除场上随机3个方块，并对对手施加2个干扰方块",
        "cooldown": 10
    },
    "刻晴": {
        "skill_name": "星斗归位",
        "skill_description": "冻结对手场地3秒",
        "cooldown": 12
    },
    "藤人": {
        "skill_name": "草原核绽放",
        "skill_description": "消除场上所有相邻的方块，并对对手施加3个干扰方块",
        "cooldown": 12
    }
}

# 游戏变量
grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
opponent_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
opponent_stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

current_blocks = []  # 当前控制的方块组
score = 0
opponent_score = 0
game_time = 0
game_start_time = 0

# 技能相关
skill_energy = 0
skill_max_energy = 100
skill_cooldown = 0

# 连击相关
combo_count = 0
combo_timer = 0
COMBO_TIME = 2.0  # 连击时间窗口（秒）

# 游戏速度
speed_levels = [1, 2, 3, 4, 5]
current_speed_level = 1
game_speed = speed_levels[current_speed_level - 1]

# 干扰方块队列
interference_queue = []

# UI颜色
UI_BG_COLOR = (30, 30, 30, 200)  # 半透明黑色
UI_BORDER_COLOR = GOLD
UI_HIGHLIGHT_COLOR = (255, 255, 255, 50)  # 半透明白色


def draw_text(text, font, color, x, y, center=False):
    """绘制文本"""
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)


def draw_ui_panel(x, y, width, height, border_color=UI_BORDER_COLOR, bg_color=UI_BG_COLOR):
    """绘制UI面板"""
    # 创建半透明背景
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill(bg_color)
    screen.blit(panel, (x, y))
    # 绘制边框
    pygame.draw.rect(screen, border_color, (x, y, width, height), 2)


def draw_menu():
    """绘制菜单界面"""
    # 绘制背景
    screen.blit(background, (0, 0))

    # 绘制标题
    draw_text("原神八奇乱斗复刻版", large_font, GOLD, SCREEN_WIDTH // 2, 100, True)

    # 绘制菜单选项
    menu_y = 250
    for i, option in enumerate(menu_options):
        color = GOLD if i == selected_option else WHITE
        draw_text(option, game_font, color, SCREEN_WIDTH // 2, menu_y + i * 60, True)

    # 绘制版权信息
    draw_text("© 2023 原神八奇乱斗复刻版", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, True)


def draw_character_select():
    """绘制角色选择界面"""
    # 绘制背景
    screen.blit(background, (0, 0))

    # 绘制标题
    draw_text("选择角色", large_font, GOLD, SCREEN_WIDTH // 2, 50, True)

    # 绘制角色选项
    panel_width = 200
    panel_height = 300
    spacing = 50
    total_width = len(character_options) * panel_width + (len(character_options) - 1) * spacing
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i, character in enumerate(character_options):
        panel_x = start_x + i * (panel_width + spacing)
        panel_y = 150

        # 设置面板颜色和边框
        bg_color = UI_BG_COLOR
        border_color = UI_BORDER_COLOR
        if i == selected_character:
            border_color = GOLD
            # 添加高亮效果
            highlight = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
            highlight.fill(UI_HIGHLIGHT_COLOR)
            screen.blit(highlight, (panel_x - 5, panel_y - 5))

        draw_ui_panel(panel_x, panel_y, panel_width, panel_height, border_color, bg_color)

        # 绘制角色图片
        char_img = character_images[character]
        char_img_rect = char_img.get_rect(center=(panel_x + panel_width // 2, panel_y + 100))
        screen.blit(char_img, char_img_rect)

        # 绘制角色名称
        draw_text(character, game_font, WHITE, panel_x + panel_width // 2, panel_y + 180, True)

        # 绘制技能名称
        skill_name = characters[character]["skill_name"]
        draw_text(skill_name, small_font, GOLD, panel_x + panel_width // 2, panel_y + 220, True)

        # 绘制技能描述（可能需要换行处理）
        skill_desc = characters[character]["skill_description"]
        draw_text(skill_desc, small_font, WHITE, panel_x + 10, panel_y + 250)

    # 绘制确认按钮
    confirm_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 550, 200, 50)
    pygame.draw.rect(screen, GOLD, confirm_button_rect, 2)
    draw_text("确认选择", game_font, WHITE, SCREEN_WIDTH // 2, 575, True)


def draw_game():
    """绘制游戏界面"""
    # 绘制背景
    screen.blit(background, (0, 0))

    # 绘制游戏区域边框
    pygame.draw.rect(screen, GOLD, (GAME_AREA_X - 5, GAME_AREA_Y - 5,
                                    GAME_AREA_WIDTH * BLOCK_SIZE + 10,
                                    GAME_AREA_HEIGHT * BLOCK_SIZE + 10), 2)

    # 绘制对手游戏区域边框
    pygame.draw.rect(screen, GOLD, (OPPONENT_AREA_X - 5, OPPONENT_AREA_Y - 5,
                                    GAME_AREA_WIDTH * BLOCK_SIZE + 10,
                                    GAME_AREA_HEIGHT * BLOCK_SIZE + 10), 2)

    # 绘制玩家信息面板
    player_panel_width = 250
    player_panel_height = 200
    draw_ui_panel(GAME_AREA_X - player_panel_width - 10, GAME_AREA_Y,
                  player_panel_width, player_panel_height)

    # 绘制玩家角色图片
    player_char_img = character_images[current_character]
    player_char_rect = player_char_img.get_rect(center=(GAME_AREA_X - player_panel_width // 2 - 10, GAME_AREA_Y + 60))
    screen.blit(player_char_img, player_char_rect)

    # 绘制玩家信息
    draw_text(f"玩家: {current_character}", game_font, WHITE, GAME_AREA_X - player_panel_width, GAME_AREA_Y + 120)
    draw_text(f"分数: {score}", game_font, WHITE, GAME_AREA_X - player_panel_width, GAME_AREA_Y + 150)
    draw_text(f"技能: {characters[current_character]['skill_name']}", small_font, GOLD,
              GAME_AREA_X - player_panel_width, GAME_AREA_Y + 180)

    # 绘制技能能量条
    energy_bar_width = player_panel_width - 20
    energy_bar_height = 20
    energy_bar_x = GAME_AREA_X - player_panel_width - 10 + 10
    energy_bar_y = GAME_AREA_Y + player_panel_height - 30
    pygame.draw.rect(screen, GRAY, (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height))
    energy_width = int(energy_bar_width * (skill_energy / skill_max_energy))
    pygame.draw.rect(screen, GOLD, (energy_bar_x, energy_bar_y, energy_width, energy_bar_height))
    draw_text(f"{int(skill_energy)}%", small_font, WHITE, energy_bar_x + energy_bar_width // 2, energy_bar_y + 10, True)

    # 绘制对手信息面板
    opponent_panel_width = 250
    opponent_panel_height = 200
    draw_ui_panel(OPPONENT_AREA_X + GAME_AREA_WIDTH * BLOCK_SIZE + 10, GAME_AREA_Y,
                  opponent_panel_width, opponent_panel_height)

    # 绘制对手角色图片
    opponent_char_img = character_images[opponent_character]
    opponent_char_rect = opponent_char_img.get_rect(
        center=(OPPONENT_AREA_X + GAME_AREA_WIDTH * BLOCK_SIZE + opponent_panel_width // 2 + 10, GAME_AREA_Y + 60))
    screen.blit(opponent_char_img, opponent_char_rect)

    # 绘制对手信息
    draw_text(f"对手: {opponent_character}", game_font, WHITE, OPPONENT_AREA_X + GAME_AREA_WIDTH * BLOCK_SIZE + 10,
              GAME_AREA_Y + 120)
    draw_text(f"分数: {opponent_score}", game_font, WHITE, OPPONENT_AREA_X + GAME_AREA_WIDTH * BLOCK_SIZE + 10,
              GAME_AREA_Y + 150)

    # 绘制时间面板
    time_panel_width = 200
    time_panel_height = 50
    draw_ui_panel(SCREEN_WIDTH // 2 - time_panel_width // 2, GAME_AREA_Y - 60,
                  time_panel_width, time_panel_height)
    minutes = int(game_time) // 60
    seconds = int(game_time) % 60
    draw_text(f"时间: {minutes:02d}:{seconds:02d}", game_font, WHITE, SCREEN_WIDTH // 2, GAME_AREA_Y - 35, True)

    # 绘制速度面板
    speed_panel_width = 200
    speed_panel_height = 50
    draw_ui_panel(SCREEN_WIDTH // 2 - speed_panel_width // 2, GAME_AREA_Y + GAME_AREA_HEIGHT * BLOCK_SIZE + 20,
                  speed_panel_width, speed_panel_height)
    draw_text(f"速度: {current_speed_level}/4", game_font, WHITE, SCREEN_WIDTH // 2,
              GAME_AREA_Y + GAME_AREA_HEIGHT * BLOCK_SIZE + 45, True)
    draw_text("按+/-调整速度", small_font, WHITE, SCREEN_WIDTH // 2,
              GAME_AREA_Y + GAME_AREA_HEIGHT * BLOCK_SIZE + 70, True)

    # 绘制操作提示面板
    controls_panel_width = 400
    controls_panel_height = 50
    draw_ui_panel(SCREEN_WIDTH // 2 - controls_panel_width // 2, GAME_AREA_Y + GAME_AREA_HEIGHT * BLOCK_SIZE + 100,
                  controls_panel_width, controls_panel_height)
    draw_text("方向键移动，空格旋转", small_font, WHITE, SCREEN_WIDTH // 2,
              GAME_AREA_Y + GAME_AREA_HEIGHT * BLOCK_SIZE + 125, True)

    # 绘制网格中的方块
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            # 绘制玩家网格
            if grid[y][x] is not None:
                block_img = block_images[grid[y][x]]
                screen.blit(block_img, (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE))
            # 绘制玩家石头
            if stone_grid[y][x] is not None:
                stone_img = block_images["stone"]
                screen.blit(stone_img, (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE))

            # 绘制对手网格
            if opponent_grid[y][x] is not None:
                block_img = block_images[opponent_grid[y][x]]
                screen.blit(block_img, (OPPONENT_AREA_X + x * BLOCK_SIZE, OPPONENT_AREA_Y + y * BLOCK_SIZE))
            # 绘制对手石头
            if opponent_stone_grid[y][x] is not None:
                stone_img = block_images["stone"]
                screen.blit(stone_img, (OPPONENT_AREA_X + x * BLOCK_SIZE, OPPONENT_AREA_Y + y * BLOCK_SIZE))

    # 绘制当前控制的方块组
    for block in current_blocks:
        if block["y"] >= 0:  # 只绘制在游戏区域内的方块
            block_img = block_images[block["color"]]
            screen.blit(block_img, (GAME_AREA_X + block["x"] * BLOCK_SIZE, GAME_AREA_Y + block["y"] * BLOCK_SIZE))


def draw_game_over():
    """绘制游戏结束界面"""
    # 创建半透明覆盖层
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # 半透明黑色
    screen.blit(overlay, (0, 0))

    # 绘制游戏结束面板
    panel_width = 400
    panel_height = 300
    panel_x = SCREEN_WIDTH // 2 - panel_width // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
    draw_ui_panel(panel_x, panel_y, panel_width, panel_height)

    # 绘制游戏结束文本
    draw_text("你输了！", large_font, RED, SCREEN_WIDTH // 2, panel_y + 80, True)
    draw_text(f"最终分数: {score}", game_font, WHITE, SCREEN_WIDTH // 2, panel_y + 150, True)
    draw_text("按回车键返回主菜单", game_font, GOLD, SCREEN_WIDTH // 2, panel_y + 220, True)


def create_block_group():
    """创建新的方块组"""
    colors = ["blue", "green", "purple", "yellow"]
    color1 = random.choice(colors)
    color2 = random.choice(colors)
    x = GAME_AREA_WIDTH // 2 - 1
    y = -1  # 修改：从-1开始，这样方块组最初只有一部分可见
    return [{"color": color1, "x": x, "y": y}, {"color": color2, "x": x, "y": y + 1}]


def create_stones(count):
    """创建石头方块"""
    stones = []
    for _ in range(count):
        x = random.randint(0, GAME_AREA_WIDTH - 1)
        y = 0
        stones.append({"color": "stone", "x": x, "y": y})
    return stones


def check_collision(blocks):
    """检查方块组是否与现有方块或边界碰撞"""
    for block in blocks:
        x, y = block["x"], block["y"]
        # 检查边界
        if x < 0 or x >= GAME_AREA_WIDTH or y >= GAME_AREA_HEIGHT:
            return True
        # 检查与现有方块的碰撞（只检查在游戏区域内的方块）
        if y >= 0 and (grid[y][x] is not None or stone_grid[y][x] is not None):
            return True
    return False


def place_blocks(blocks):
    """将方块组放置到网格中"""
    for block in blocks:
        x, y = block["x"], block["y"]
        if 0 <= y < GAME_AREA_HEIGHT and 0 <= x < GAME_AREA_WIDTH:
            grid[y][x] = block["color"]

    # 检查并消除连接的方块
    cleared = check_clear()
    if cleared > 0:
        # 播放消除音效
        if audio_available and "clear" in sound_effects:
            sound_effects["clear"].play()

        # 更新分数
        global score, combo_count, combo_timer, skill_energy
        base_score = cleared * 10
        combo_count += 1
        combo_timer = time.time()
        combo_bonus = combo_count - 1
        total_score = base_score * (1 + combo_bonus * 0.5)
        score += int(total_score)

        # 增加技能能量
        skill_energy = min(skill_max_energy, skill_energy + cleared * 5)

        # 下落悬空的方块
        drop_floating_blocks()


def rotate_blocks():
    """旋转方块组"""
    if len(current_blocks) != 2:
        return

    # 获取旋转中心（第一个方块的位置）
    center_x, center_y = current_blocks[0]["x"], current_blocks[0]["y"]

    # 计算第二个方块相对于中心的位置
    rel_x = current_blocks[1]["x"] - center_x
    rel_y = current_blocks[1]["y"] - center_y

    # 旋转90度（顺时针）
    new_rel_x = -rel_y
    new_rel_y = rel_x

    # 计算旋转后的新位置
    new_x = center_x + new_rel_x
    new_y = center_y + new_rel_y

    # 创建旋转后的方块组
    new_blocks = [
        {"color": current_blocks[0]["color"], "x": center_x, "y": center_y},
        {"color": current_blocks[1]["color"], "x": new_x, "y": new_y}
    ]

    # 检查旋转后是否会碰撞
    if not check_collision(new_blocks):
        current_blocks[:] = new_blocks
        # 播放旋转音效
        if audio_available and "rotate" in sound_effects:
            sound_effects["rotate"].play()


def drop_floating_blocks():
    """下落悬空的方块"""
    for x in range(GAME_AREA_WIDTH):
        for y in range(GAME_AREA_HEIGHT - 2, -1, -1):
            if grid[y][x] is not None and grid[y + 1][x] is None and stone_grid[y + 1][x] is None:
                # 找到最远可以下落的位置
                new_y = y
                while new_y + 1 < GAME_AREA_HEIGHT and grid[new_y + 1][x] is None and stone_grid[new_y + 1][x] is None:
                    new_y += 1
                # 移动方块
                if new_y != y:
                    grid[new_y][x] = grid[y][x]
                    grid[y][x] = None


def check_clear():
    """检查并消除连接的相同颜色方块"""
    # 创建访问标记数组
    visited = [[False for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    total_cleared = 0

    # 遍历网格中的每个方块
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if grid[y][x] is not None and not visited[y][x]:
                # 找到所有连接的相同颜色方块
                color = grid[y][x]
                connected = []
                find_connected(x, y, color, visited, connected)

                # 如果连接的方块数量达到4个或以上，消除它们
                if len(connected) >= 4:
                    for cx, cy in connected:
                        grid[cy][cx] = None
                        total_cleared += 1

                    # 检查周围的石头，如果没有相邻的彩色方块，也消除它们
                    clear_isolated_stones()

    return total_cleared


def find_connected(x, y, color, visited, connected):
    """递归找到所有连接的相同颜色方块"""
    # 检查边界和已访问标记
    if x < 0 or x >= GAME_AREA_WIDTH or y < 0 or y >= GAME_AREA_HEIGHT or visited[y][x]:
        return
    # 检查颜色是否匹配
    if grid[y][x] != color:
        return

    # 标记为已访问并添加到连接列表
    visited[y][x] = True
    connected.append((x, y))

    # 递归检查四个方向
    find_connected(x + 1, y, color, visited, connected)  # 右
    find_connected(x - 1, y, color, visited, connected)  # 左
    find_connected(x, y + 1, color, visited, connected)  # 下
    find_connected(x, y - 1, color, visited, connected)  # 上


def clear_isolated_stones():
    """清除没有相邻彩色方块的石头"""
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if stone_grid[y][x] is not None:
                # 检查四个方向是否有彩色方块
                has_adjacent_color = False
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GAME_AREA_WIDTH and 0 <= ny < GAME_AREA_HEIGHT and grid[ny][nx] is not None:
                        has_adjacent_color = True
                        break
                # 如果没有相邻的彩色方块，清除这个石头
                if not has_adjacent_color:
                    stone_grid[y][x] = None


def create_interference_blocks(count):
    """创建干扰方块"""
    global interference_queue
    interference_queue.extend([1] * count)


def apply_interference_blocks():
    """应用干扰方块到对手网格"""
    global interference_queue, opponent_grid
    if not interference_queue:
        return

    # 每次应用一个干扰方块
    interference_queue.pop(0)

    # 在对手网格顶部随机位置添加一个干扰方块
    x = random.randint(0, GAME_AREA_WIDTH - 1)
    # 将上方的方块向上移动
    for y in range(1, GAME_AREA_HEIGHT):
        opponent_grid[y - 1][x] = opponent_grid[y][x]
    # 在底部添加干扰方块
    opponent_grid[GAME_AREA_HEIGHT - 1][x] = random.choice(["blue", "green", "purple", "yellow"])


def move_blocks(dx):
    """水平移动方块组"""
    new_blocks = [{"color": block["color"], "x": block["x"] + dx, "y": block["y"]} for block in current_blocks]
    if not check_collision(new_blocks):
        current_blocks[:] = new_blocks


def drop_blocks():
    """加速方块组下落"""
    while not check_collision([{"color": b["color"], "x": b["x"], "y": b["y"] + 1} for b in current_blocks]):
        for block in current_blocks:
            block["y"] += 1


def use_skill():
    """使用角色技能"""
    global skill_energy, skill_cooldown, current_blocks

    if skill_energy < skill_max_energy or skill_cooldown > 0:
        return

    # 重置技能能量和设置冷却
    skill_energy = 0
    skill_cooldown = characters[current_character]["cooldown"]

    # 根据不同角色执行不同技能
    if current_character == "雷电将军":
        # 消除场上随机3个方块，并对对手施加2个干扰方块
        clear_random_blocks(3)
        create_interference_blocks(2)
    elif current_character == "钟离":
        # 将当前方块立即下落并消除下方一行方块
        drop_blocks()
        clear_bottom_row()
    elif current_character == "甘雨":
        # 冻结对手场地3秒（在实际游戏中需要更复杂的实现）
        # 这里简化为增加自己的分数
        global score
        score += 50
    elif current_character == "胡桃":
        # 将场上所有同色方块变为当前方块颜色
        if current_blocks:
            target_color = current_blocks[0]["color"]
            convert_all_to_color(target_color)


def clear_random_blocks(count):
    """消除场上随机的方块"""
    # 收集所有非空方块的位置
    non_empty = []
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if grid[y][x] is not None:
                non_empty.append((x, y))

    # 随机选择并消除
    if non_empty:
        to_clear = random.sample(non_empty, min(count, len(non_empty)))
        for x, y in to_clear:
            grid[y][x] = None


def clear_bottom_row():
    """消除最底部的一行方块"""
    for x in range(GAME_AREA_WIDTH):
        grid[GAME_AREA_HEIGHT - 1][x] = None


def convert_all_to_color(target_color):
    """将场上所有方块转换为目标颜色"""
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if grid[y][x] is not None and grid[y][x] != "stone":
                grid[y][x] = target_color


def check_game_over():
    """检查游戏是否结束"""
    # 检查是否有方块到达顶部
    for x in range(GAME_AREA_WIDTH):
        if grid[0][x] is not None:
            return True

    # 检查时间限制（可选）
    # if time.time() - game_start_time > 180:  # 3分钟时间限制
    #     return True

    return False


def handle_menu_input(event):
    """处理菜单输入"""
    global selected_option, current_state

    if event.key == pygame.K_UP:
        selected_option = (selected_option - 1) % len(menu_options)
    elif event.key == pygame.K_DOWN:
        selected_option = (selected_option + 1) % len(menu_options)
    elif event.key == pygame.K_RETURN:
        if selected_option == 0:  # 开始游戏
            start_game()
        elif selected_option == 1:  # 角色选择
            current_state = CHARACTER_SELECT
        elif selected_option == 2:  # 退出
            pygame.quit()
            sys.exit()


def handle_character_select_input(event):
    """处理角色选择输入"""
    global selected_character, current_character, current_state

    if event.key == pygame.K_LEFT:
        selected_character = (selected_character - 1) % len(character_options)
    elif event.key == pygame.K_RIGHT:
        selected_character = (selected_character + 1) % len(character_options)
    elif event.key == pygame.K_RETURN:
        current_character = character_options[selected_character]
        start_game()
    elif event.key == pygame.K_ESCAPE:
        current_state = MENU


def handle_game_input(event):
    """处理游戏输入"""
    global current_speed_level, game_speed

    if event.key == pygame.K_LEFT:
        move_blocks(-1)
    elif event.key == pygame.K_RIGHT:
        move_blocks(1)
    elif event.key == pygame.K_DOWN:
        # 加速下落
        new_blocks = [{"color": block["color"], "x": block["x"], "y": block["y"] + 1} for block in current_blocks]
        if not check_collision(new_blocks):
            current_blocks = new_blocks
    elif event.key == pygame.K_SPACE:
        rotate_blocks()
    elif event.key == pygame.K_s:
        use_skill()
    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        # 增加速度
        current_speed_level = min(current_speed_level + 1, len(speed_levels))
        game_speed = speed_levels[current_speed_level - 1]
    elif event.key == pygame.K_MINUS:
        # 减少速度
        current_speed_level = max(current_speed_level - 1, 1)
        game_speed = speed_levels[current_speed_level - 1]
    elif event.key == pygame.K_ESCAPE:
        current_state = MENU


def handle_game_over_input(event):
    """处理游戏结束输入"""
    global current_state

    if event.key == pygame.K_RETURN:
        current_state = MENU


def start_game():
    """开始新游戏"""
    global current_state, grid, stone_grid, opponent_grid, opponent_stone_grid
    global current_blocks, score, opponent_score, game_time, game_start_time
    global skill_energy, skill_cooldown, combo_count, combo_timer

    # 重置游戏状态
    current_state = GAME
    grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    opponent_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    opponent_stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

    # 创建初始方块组
    current_blocks = create_block_group()

    # 重置分数和时间
    score = 0
    opponent_score = 0
    game_time = 0
    game_start_time = time.time()

    # 重置技能相关
    skill_energy = 0
    skill_cooldown = 0
    combo_count = 0
    combo_timer = 0


def update_opponent():
    """更新对手状态（AI行为）"""
    global opponent_score

    # 优化AI：降低得分概率和数值，使游戏更平衡
    if random.random() < 0.01:  # 降低概率从5%到1%
        opponent_score += random.randint(1, 5)  # 降低得分范围从1-10到1-5


def main():
    """主游戏循环"""
    global current_state, current_blocks, game_time, combo_count, combo_timer, skill_cooldown

    # 初始化
    clock = pygame.time.Clock()
    last_drop_time = time.time()
    last_stone_time = time.time()

    # 主循环
    running = True
    while running:
        current_time = time.time()

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_state == MENU:
                    handle_menu_input(event)
                elif current_state == CHARACTER_SELECT:
                    handle_character_select_input(event)
                elif current_state == GAME:
                    handle_game_input(event)
                elif current_state == GAME_OVER:
                    handle_game_over_input(event)

        # 更新游戏状态
        if current_state == GAME:
            # 更新游戏时间
            game_time = current_time - game_start_time

            # 更新连击计时
            if combo_count > 0 and current_time - combo_timer > COMBO_TIME:
                combo_count = 0

            # 更新技能冷却
            if skill_cooldown > 0:
                skill_cooldown = max(0, skill_cooldown - (current_time - last_drop_time))

            # 更新对手
            update_opponent()

            # 生成石头
            if current_time - last_stone_time > 5:  # 每5秒生成一个石头
                stones = create_stones(1)
                for stone in stones:
                    if not check_collision([stone]):
                        stone_grid[stone["y"]][stone["x"]] = "stone"
                last_stone_time = current_time

            # 应用干扰方块
            apply_interference_blocks()

            # 方块下落
            if current_time - last_drop_time > 1.0 / game_speed:
                new_blocks = [{"color": block["color"], "x": block["x"], "y": block["y"] + 1} for block in current_blocks]
                if check_collision(new_blocks):
                    place_blocks(current_blocks)
                    current_blocks = create_block_group()
                    # 修改：只有当新方块完全进入游戏区域后才检查碰撞
                    all_blocks_visible = all(block["y"] >= 0 for block in current_blocks)
                    if all_blocks_visible and check_collision(current_blocks):
                        current_state = GAME_OVER
                else:
                    current_blocks = new_blocks
                last_drop_time = current_time

            # 检查游戏是否结束
            if check_game_over():
                current_state = GAME_OVER

        # 绘制界面
        if current_state == MENU:
            draw_menu()
        elif current_state == CHARACTER_SELECT:
            draw_character_select()
        elif current_state == GAME:
            draw_game()
        elif current_state == GAME_OVER:
            draw_game()
            draw_game_over()

        # 更新屏幕
        pygame.display.flip()

        # 控制帧率
        clock.tick(60)


if __name__ == "__main__":
    main()
