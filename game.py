import pygame
import random
import sys
import time
import os


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

# 加载背景音乐
if audio_available:
    try:
        pygame.mixer.music.load(resource_path(os.path.join("sounds", "z8g15-g2l2u.wav")))
        pygame.mixer.music.play(-1)  # 循环播放
    except:
        print("警告: 无法加载背景音乐")

# 字体 - 使用支持中文的系统字体
try:
    # 尝试使用系统中文字体
    chinese_fonts = ['simhei', 'microsoftyahei', 'simsun', 'nsimsun', 'fangsong', 'kaiti']
    font_found = False

    for font_name in chinese_fonts:
        try:
            title_font = pygame.font.SysFont(font_name, 72)
            menu_font = pygame.font.SysFont(font_name, 48)
            game_font = pygame.font.SysFont(font_name, 36)
            small_font = pygame.font.SysFont(font_name, 24)
            font_found = True
            print(f"成功加载中文字体: {font_name}")
            break
        except:
            continue

    if not font_found:
        # 如果没有找到中文字体，使用默认字体
        print("警告: 未找到中文字体，使用默认字体")
        title_font = pygame.font.Font(None, 72)
        menu_font = pygame.font.Font(None, 48)
        game_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
except:
    # 出错时使用默认字体
    print("警告: 加载字体时出错，使用默认字体")
    title_font = pygame.font.Font(None, 72)
    menu_font = pygame.font.Font(None, 48)
    game_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

# 游戏状态
MENU = 0
CHARACTER_SELECT = 1
GAME = 2
GAME_OVER = 3
current_state = MENU

# 藤人角色定义
characters = {
    "雷电将军": {
        "skill_name": "雷罚恶曜之眼",
        "skill_description": "消除场上随机3个方块，并对对手施加2个干扰方块",
        "cooldown": 10,
        "color": PURPLE  # 紫色
    },
    "钟离": {
        "skill_name": "地心",
        "skill_description": "将当前方块立即下落并消除下方一行方块",
        "cooldown": 8,
        "color": ORANGE  # 橙色
    },
    "甘雨": {
        "skill_name": "降众天华",
        "skill_description": "冻结对手场地3秒，期间对手无法操作",
        "cooldown": 12,
        "color": CYAN  # 天蓝色
    },
    "胡桃": {
        "skill_name": "蝶引来生",
        "skill_description": "将场上所有同色方块变为当前方块颜色",
        "cooldown": 15,
        "color": RED  # 红色
    }
}

# 当前选择的角色
current_character = "雷电将军"
opponent_character = "钟离"

# 技能充能和冷却
skill_energy = 0
skill_max_energy = 100
skill_cooldown = 0

# 游戏网格
grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

# 对手网格
opponent_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
opponent_stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

# 当前方块组
current_blocks = []

# 石头计时器
stone_timer = time.time()

# 分数
score = 0
opponent_score = 0

# 连击计数
combo_count = 0
combo_timer = 0
COMBO_TIME = 2  # 连击时间窗口（秒）

# 游戏速度
game_speed = 5  # 初始速度
speed_levels = [3, 5, 8, 12]  # 速度级别
current_speed_level = 1

# 游戏时间
game_time = 0
game_start_time = 0

# 干扰方块队列
interference_queue = 0
opponent_interference_queue = 0

# 菜单选项
menu_options = ["开始游戏", "角色选择", "退出"]
selected_option = 0

# 角色选择界面
character_options = list(characters.keys())
selected_character = 0

# 按键状态
key_repeat_delay = 200  # 按键重复延迟（毫秒）
key_repeat_interval = 50  # 按键重复间隔（毫秒）
pygame.key.set_repeat(key_repeat_delay, key_repeat_interval)  # 设置按键重复

# 界面样式
UI_BORDER_COLOR = GOLD
UI_BACKGROUND_COLOR = (30, 30, 30, 180)  # 半透明深灰色
UI_HIGHLIGHT_COLOR = (255, 255, 255, 100)  # 半透明白色


def draw_text(text, font, color, x, y, centered=False):
    """绘制文本"""
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect


def draw_ui_panel(x, y, width, height, border_color=UI_BORDER_COLOR, bg_color=UI_BACKGROUND_COLOR):
    """绘制UI面板"""
    # 创建半透明背景
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill(bg_color)
    screen.blit(panel, (x, y))

    # 绘制边框
    pygame.draw.rect(screen, border_color, (x, y, width, height), 2)

    # 添加高光效果
    pygame.draw.line(screen, UI_HIGHLIGHT_COLOR, (x + 2, y + 2), (x + width - 2, y + 2), 1)
    pygame.draw.line(screen, UI_HIGHLIGHT_COLOR, (x + 2, y + 2), (x + 2, y + height - 2), 1)


def draw_menu():
    """绘制主菜单"""
    screen.blit(background, (0, 0))

    # 绘制标题面板
    title_panel_width = 600
    title_panel_height = 100
    title_panel_x = (SCREEN_WIDTH - title_panel_width) // 2
    title_panel_y = 100
    draw_ui_panel(title_panel_x, title_panel_y, title_panel_width, title_panel_height)

    # 绘制标题
    title_text = "原神八奇乱斗复刻版"
    draw_text(title_text, title_font, GOLD, SCREEN_WIDTH // 2, title_panel_y + title_panel_height // 2, True)

    # 绘制菜单面板
    menu_panel_width = 400
    menu_panel_height = 300
    menu_panel_x = (SCREEN_WIDTH - menu_panel_width) // 2
    menu_panel_y = 250
    draw_ui_panel(menu_panel_x, menu_panel_y, menu_panel_width, menu_panel_height)

    # 绘制菜单选项
    for i, option in enumerate(menu_options):
        color = GOLD if i == selected_option else WHITE
        draw_text(option, menu_font, color, SCREEN_WIDTH // 2, menu_panel_y + 70 + i * 70, True)

    # 绘制操作提示面板
    tip_panel_width = 500
    tip_panel_height = 50
    tip_panel_x = (SCREEN_WIDTH - tip_panel_width) // 2
    tip_panel_y = SCREEN_HEIGHT - 80
    draw_ui_panel(tip_panel_x, tip_panel_y, tip_panel_width, tip_panel_height)

    # 绘制操作提示
    draw_text("方向键选择，回车确认", small_font, WHITE, SCREEN_WIDTH // 2, tip_panel_y + tip_panel_height // 2, True)


def draw_character_select():
    """绘制角色选择界面"""
    screen.blit(background, (0, 0))

    # 绘制标题面板
    title_panel_width = 600
    title_panel_height = 100
    title_panel_x = (SCREEN_WIDTH - title_panel_width) // 2
    title_panel_y = 50
    draw_ui_panel(title_panel_x, title_panel_y, title_panel_width, title_panel_height)

    # 绘制标题
    draw_text("选择你的藤人角色", title_font, GOLD, SCREEN_WIDTH // 2, title_panel_y + title_panel_height // 2, True)

    # 绘制角色面板
    char_panel_width = 500
    char_panel_height = 400
    char_panel_x = (SCREEN_WIDTH - char_panel_width) // 2
    char_panel_y = 180
    draw_ui_panel(char_panel_x, char_panel_y, char_panel_width, char_panel_height)

    # 绘制角色选项
    for i, character in enumerate(character_options):
        color = GOLD if i == selected_character else WHITE
        rect = draw_text(character, menu_font, color, SCREEN_WIDTH // 2, char_panel_y + 70 + i * 70, True)

        # 绘制角色技能描述
        if i == selected_character:
            skill_name = characters[character]["skill_name"]
            skill_desc = characters[character]["skill_description"]

            # 绘制技能面板
            skill_panel_width = 450
            skill_panel_height = 100
            skill_panel_x = (SCREEN_WIDTH - skill_panel_width) // 2
            skill_panel_y = char_panel_y + char_panel_height + 20
            draw_ui_panel(skill_panel_x, skill_panel_y, skill_panel_width, skill_panel_height)

            draw_text(f"技能: {skill_name}", small_font, LIGHT_BLUE, SCREEN_WIDTH // 2, skill_panel_y + 30, True)
            draw_text(skill_desc, small_font, WHITE, SCREEN_WIDTH // 2, skill_panel_y + 60, True)

    # 绘制操作提示面板
    tip_panel_width = 500
    tip_panel_height = 50
    tip_panel_x = (SCREEN_WIDTH - tip_panel_width) // 2
    tip_panel_y = SCREEN_HEIGHT - 80
    draw_ui_panel(tip_panel_x, tip_panel_y, tip_panel_width, tip_panel_height)

    # 绘制操作提示
    draw_text("方向键选择，回车确认", small_font, WHITE, SCREEN_WIDTH // 2, tip_panel_y + tip_panel_height // 2, True)


def create_block_group():
    """生成一个新的方块组（不包含石头）"""
    colors = list(block_images.keys())
    colors.remove("stone")  # 移除石头颜色
    color1 = random.choice(colors)
    color2 = random.choice(colors)
    x = GAME_AREA_WIDTH // 2 - 1
    y = 0
    return [{"color": color1, "x": x, "y": y}, {"color": color2, "x": x, "y": y + 1}]


def create_stones(count=1):
    """生成指定数量的石头，确保不与当前方块组重叠"""
    stones = []
    for _ in range(count):
        while True:
            x = random.randint(0, GAME_AREA_WIDTH - 1)
            y = 0
            # 检查是否与当前方块组重叠
            overlap = False
            for block in current_blocks:
                if block["x"] == x and block["y"] == y:
                    overlap = True
                    break
            if not overlap:
                stones.append({"color": "stone", "x": x, "y": y})
                break
    return stones


def create_interference_blocks(count=1):
    """生成指定数量的干扰方块"""
    global opponent_interference_queue
    opponent_interference_queue += count


def apply_interference_blocks():
    """应用干扰方块到对手场地"""
    global opponent_interference_queue
    if opponent_interference_queue > 0:
        stones = create_stones(min(opponent_interference_queue, 2))  # 每次最多应用2个干扰方块
        for stone in stones:
            if not check_collision([stone], opponent_grid, opponent_stone_grid):
                opponent_stone_grid[stone["y"]][stone["x"]] = stone["color"]
        opponent_interference_queue -= len(stones)


def draw_block(x, y, color, is_opponent=False):
    """绘制方块"""
    area_x = OPPONENT_AREA_X if is_opponent else GAME_AREA_X
    area_y = OPPONENT_AREA_Y if is_opponent else GAME_AREA_Y
    screen.blit(block_images[color], (area_x + x * BLOCK_SIZE, area_y + y * BLOCK_SIZE))


def draw_game_area():
    """绘制游戏区域边框"""
    # 玩家区域
    draw_ui_panel(
        GAME_AREA_X - 10,
        GAME_AREA_Y - 10,
        GAME_AREA_WIDTH * BLOCK_SIZE + 20,
        GAME_AREA_HEIGHT * BLOCK_SIZE + 20
    )

    # 对手区域
    draw_ui_panel(
        OPPONENT_AREA_X - 10,
        OPPONENT_AREA_Y - 10,
        GAME_AREA_WIDTH * BLOCK_SIZE + 20,
        GAME_AREA_HEIGHT * BLOCK_SIZE + 20
    )


def draw_grid():
    """绘制网格"""
    # 绘制玩家网格
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if grid[y][x]:
                draw_block(x, y, grid[y][x])
            if stone_grid[y][x]:
                draw_block(x, y, stone_grid[y][x])

    # 绘制对手网格
    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if opponent_grid[y][x]:
                draw_block(x, y, opponent_grid[y][x], True)
            if opponent_stone_grid[y][x]:
                draw_block(x, y, opponent_stone_grid[y][x], True)


def draw_current_blocks():
    """绘制当前方块组"""
    for block in current_blocks:
        if block["y"] >= 0:
            draw_block(block["x"], block["y"], block["color"])


def draw_game_info():
    """绘制游戏信息"""
    # 玩家信息面板
    player_panel_width = 220
    player_panel_height = 250
    player_panel_x = 50
    player_panel_y = 50
    draw_ui_panel(player_panel_x, player_panel_y, player_panel_width, player_panel_height)

    # 玩家信息
    draw_text(f"玩家: {current_character}", game_font, WHITE, player_panel_x + 20, player_panel_y + 30)
    draw_text(f"分数: {score}", game_font, WHITE, player_panel_x + 20, player_panel_y + 70)

    # 对手信息面板
    opponent_panel_width = 220
    opponent_panel_height = 150
    opponent_panel_x = SCREEN_WIDTH - opponent_panel_width - 50
    opponent_panel_y = 50
    draw_ui_panel(opponent_panel_x, opponent_panel_y, opponent_panel_width, opponent_panel_height)

    # 对手信息
    draw_text(f"对手: {opponent_character}", game_font, WHITE, opponent_panel_x + 20, opponent_panel_y + 30)
    draw_text(f"分数: {opponent_score}", game_font, WHITE, opponent_panel_x + 20, opponent_panel_y + 70)

    # 游戏时间面板
    time_panel_width = 200
    time_panel_height = 50
    time_panel_x = (SCREEN_WIDTH - time_panel_width) // 2
    time_panel_y = 10
    draw_ui_panel(time_panel_x, time_panel_y, time_panel_width, time_panel_height)

    # 游戏时间
    elapsed_time = int(time.time() - game_start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    draw_text(f"时间: {minutes:02d}:{seconds:02d}", game_font, WHITE, SCREEN_WIDTH // 2,
              time_panel_y + time_panel_height // 2, True)

    # 连击信息
    if combo_count > 1 and time.time() - combo_timer < COMBO_TIME:
        combo_panel_width = 120
        combo_panel_height = 40
        combo_panel_x = GAME_AREA_X + (GAME_AREA_WIDTH * BLOCK_SIZE - combo_panel_width) // 2
        combo_panel_y = GAME_AREA_Y - 50
        draw_ui_panel(combo_panel_x, combo_panel_y, combo_panel_width, combo_panel_height)
        draw_text(f"{combo_count} 连击!", game_font, GOLD, GAME_AREA_X + GAME_AREA_WIDTH * BLOCK_SIZE // 2,
                  combo_panel_y + combo_panel_height // 2, True)

    # 技能信息
    skill_name = characters[current_character]["skill_name"]
    draw_text(f"技能: {skill_name}", game_font, LIGHT_BLUE, player_panel_x + 20, player_panel_y + 110)

    # 技能充能条
    pygame.draw.rect(screen, GRAY, (player_panel_x + 20, player_panel_y + 150, 180, 20))
    pygame.draw.rect(screen, characters[current_character]["color"],
                     (player_panel_x + 20, player_panel_y + 150, skill_energy * 1.8, 20))
    draw_text(f"{skill_energy}%", small_font, WHITE, player_panel_x + 110, player_panel_y + 160, True)

    # 技能冷却
    if skill_cooldown > 0:
        draw_text(f"冷却: {skill_cooldown:.1f}秒", game_font, WHITE, player_panel_x + 20, player_panel_y + 190)
    else:
        draw_text("按S键使用技能", game_font, GOLD, player_panel_x + 20, player_panel_y + 190)

    # 游戏速度面板
    speed_panel_width = 220
    speed_panel_height = 100
    speed_panel_x = SCREEN_WIDTH - speed_panel_width - 50
    speed_panel_y = 220
    draw_ui_panel(speed_panel_x, speed_panel_y, speed_panel_width, speed_panel_height)

    # 游戏速度
    draw_text(f"速度: {current_speed_level}/4", game_font, WHITE, speed_panel_x + 20, speed_panel_y + 30)
    draw_text("按 +/- 调整速度", small_font, WHITE, speed_panel_x + 20, speed_panel_y + 60)

    # 操作提示面板
    tip_panel_width = 400
    tip_panel_height = 40
    tip_panel_x = (SCREEN_WIDTH - tip_panel_width) // 2
    tip_panel_y = SCREEN_HEIGHT - 60
    draw_ui_panel(tip_panel_x, tip_panel_y, tip_panel_width, tip_panel_height)

    # 操作提示
    draw_text("方向键移动，空格旋转", small_font, WHITE, SCREEN_WIDTH // 2, tip_panel_y + tip_panel_height // 2, True)


def draw_game_over():
    """绘制游戏结束界面"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 半透明黑色
    screen.blit(overlay, (0, 0))

    # 结果面板
    result_panel_width = 500
    result_panel_height = 300
    result_panel_x = (SCREEN_WIDTH - result_panel_width) // 2
    result_panel_y = (SCREEN_HEIGHT - result_panel_height) // 2
    draw_ui_panel(result_panel_x, result_panel_y, result_panel_width, result_panel_height)

    if score > opponent_score:
        result_text = "你赢了!"
        color = GOLD
    else:
        result_text = "你输了!"
        color = RED

    draw_text(result_text, title_font, color, SCREEN_WIDTH // 2, result_panel_y + 80, True)
    draw_text(f"最终分数: {score}", menu_font, WHITE, SCREEN_WIDTH // 2, result_panel_y + 150, True)
    draw_text("按回车键返回主菜单", game_font, WHITE, SCREEN_WIDTH // 2, result_panel_y + 220, True)


def check_collision(blocks, check_grid=None, check_stone_grid=None):
    """检查方块组是否与现有方块或边界碰撞"""
    if check_grid is None:
        check_grid = grid
    if check_stone_grid is None:
        check_stone_grid = stone_grid

    for block in blocks:
        if block["x"] < 0 or block["x"] >= GAME_AREA_WIDTH or block["y"] >= GAME_AREA_HEIGHT:
            return True
        if block["y"] >= 0 and (
                (check_grid[block["y"]][block["x"]] is not None) or
                (check_stone_grid[block["y"]][block["x"]] is not None)
        ):
            return True
    return False


def place_blocks(blocks):
    """将方块组放置到网格中"""
    global score, combo_count, combo_timer, skill_energy

    for block in blocks:
        if block["y"] >= 0:
            grid[block["y"]][block["x"]] = block["color"]

    # 应用重力
    apply_gravity()

    # 检查消除
    eliminated = check_elimination()
    if eliminated > 0:
        # 更新分数
        score += eliminated

        # 更新连击
        if time.time() - combo_timer < COMBO_TIME:
            combo_count += 1
        else:
            combo_count = 1
        combo_timer = time.time()

        # 根据连击数增加干扰方块
        interference_count = combo_count
        create_interference_blocks(interference_count)

        # 增加技能充能
        skill_energy = min(skill_max_energy, skill_energy + eliminated * 5)

        # 应用干扰方块
        apply_interference_blocks()


def check_elimination():
    """检查并消除符合条件的方块，返回消除的方块数量"""
    eliminated_count = 0
    eliminated = set()

    # 使用深度优先搜索（DFS）查找所有相连的同色方块
    visited = [[False for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

    for y in range(GAME_AREA_HEIGHT):
        for x in range(GAME_AREA_WIDTH):
            if grid[y][x] and not visited[y][x]:
                color = grid[y][x]
                stack = [(y, x)]
                connected = []

                while stack:
                    cy, cx = stack.pop()
                    if not visited[cy][cx]:
                        visited[cy][cx] = True
                        connected.append((cy, cx))

                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < GAME_AREA_HEIGHT and 0 <= nx < GAME_AREA_WIDTH:
                                if grid[ny][nx] == color and not visited[ny][nx]:
                                    stack.append((ny, nx))

                # 如果相连的方块数量大于等于4，则标记为待消除
                if len(connected) >= 4:
                    eliminated.update(connected)
                    eliminated_count += len(connected)

    # 消除方块
    if eliminated:
        for (y, x) in eliminated:
            grid[y][x] = None

        # 检查是否有石头与消除区域相邻
        check_stone_elimination(eliminated)

        # 应用重力
        apply_gravity()

        # 递归检查是否有新的消除
        eliminated_count += check_elimination()

    return eliminated_count


def check_stone_elimination(eliminated):
    """检查并消除与消除区域相邻的石头"""
    for (y, x) in eliminated:
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < GAME_AREA_HEIGHT and 0 <= nx < GAME_AREA_WIDTH:
                if stone_grid[ny][nx]:
                    stone_grid[ny][nx] = None


def apply_gravity():
    """应用重力，使普通方块下落"""
    for x in range(GAME_AREA_WIDTH):
        column = [grid[y][x] for y in range(GAME_AREA_HEIGHT)]
        column = [block for block in column if block is not None]
        column = [None] * (GAME_AREA_HEIGHT - len(column)) + column
        for y in range(GAME_AREA_HEIGHT):
            grid[y][x] = column[y]


def apply_stone_gravity():
    """应用重力，使石头下落"""
    for x in range(GAME_AREA_WIDTH):
        for y in range(GAME_AREA_HEIGHT - 1, -1, -1):
            if stone_grid[y][x]:
                if y + 1 < GAME_AREA_HEIGHT and not stone_grid[y + 1][x] and not grid[y + 1][x]:
                    stone_grid[y + 1][x] = stone_grid[y][x]
                    stone_grid[y][x] = None


def rotate_blocks(blocks):
    """旋转方块组"""
    pivot = blocks[0]
    new_blocks = []

    for block in blocks:
        dx = block["x"] - pivot["x"]
        dy = block["y"] - pivot["y"]
        new_x = pivot["x"] - dy
        new_y = pivot["y"] + dx
        new_blocks.append({"color": block["color"], "x": new_x, "y": new_y})

    if not check_collision(new_blocks):
        return new_blocks
    return blocks


def use_skill():
    """使用当前角色的技能"""
    global skill_energy, skill_cooldown, grid, opponent_grid, current_blocks

    if skill_energy < skill_max_energy or skill_cooldown > 0:
        return

    character = current_character
    skill_cooldown = characters[character]["cooldown"]
    skill_energy = 0

    # 根据不同角色实现不同技能效果
    if character == "雷电将军":
        # 消除场上随机3个方块，并对对手施加2个干扰方块
        blocks_to_eliminate = []
        for y in range(GAME_AREA_HEIGHT):
            for x in range(GAME_AREA_WIDTH):
                if grid[y][x]:
                    blocks_to_eliminate.append((y, x))

        if blocks_to_eliminate:
            random.shuffle(blocks_to_eliminate)
            for i in range(min(3, len(blocks_to_eliminate))):
                y, x = blocks_to_eliminate[i]
                grid[y][x] = None

            create_interference_blocks(2)
            apply_gravity()
            check_elimination()

    elif character == "钟离":
        # 将当前方块立即下落并消除下方一行方块
        while not check_collision([{"color": b["color"], "x": b["x"], "y": b["y"] + 1} for b in current_blocks]):
            for block in current_blocks:
                block["y"] += 1

        place_blocks(current_blocks)
        current_blocks = create_block_group()

        # 消除最底部的一行
        bottom_row = GAME_AREA_HEIGHT - 1
        for x in range(GAME_AREA_WIDTH):
            grid[bottom_row][x] = None
            if stone_grid[bottom_row][x]:
                stone_grid[bottom_row][x] = None

        apply_gravity()
        check_elimination()

    elif character == "甘雨":
        # 冻结对手场地3秒，期间对手无法操作
        # 在实际多人游戏中实现，这里简化为增加自己的分数
        global score
        score += 50

    elif character == "胡桃":
        # 将场上所有同色方块变为当前方块颜色
        if current_blocks and current_blocks[0]["y"] >= 0:
            target_color = current_blocks[0]["color"]
            replaced_color = None

            # 找到一个不同于目标颜色的颜色
            for y in range(GAME_AREA_HEIGHT):
                for x in range(GAME_AREA_WIDTH):
                    if grid[y][x] and grid[y][x] != target_color:
                        replaced_color = grid[y][x]
                        break
                if replaced_color:
                    break

            # 替换所有该颜色的方块
            if replaced_color:
                for y in range(GAME_AREA_HEIGHT):
                    for x in range(GAME_AREA_WIDTH):
                        if grid[y][x] == replaced_color:
                            grid[y][x] = target_color

                check_elimination()


def update_opponent():
    """更新对手状态（AI行为）"""
    global opponent_score

    # 简单AI：随机增加分数和生成干扰方块
    if random.random() < 0.05:  # 5%的概率
        points = random.randint(1, 4)
        opponent_score += points

        if random.random() < 0.3:  # 30%的概率
            interference_count = random.randint(1, 2)
            for _ in range(interference_count):
                stones = create_stones(1)
                for stone in stones:
                    if not check_collision([stone], grid, stone_grid):
                        stone_grid[stone["y"]][stone["x"]] = stone["color"]


def reset_game():
    """重置游戏状态"""
    global grid, stone_grid, opponent_grid, opponent_stone_grid
    global current_blocks, score, opponent_score, game_start_time
    global skill_energy, skill_cooldown, combo_count, combo_timer
    global interference_queue, opponent_interference_queue

    # 重置网格
    grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    opponent_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]
    opponent_stone_grid = [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

    # 重置方块和分数
    current_blocks = create_block_group()
    score = 0
    opponent_score = 0

    # 重置游戏时间
    game_start_time = time.time()

    # 重置技能和连击
    skill_energy = 0
    skill_cooldown = 0
    combo_count = 0
    combo_timer = 0

    # 重置干扰队列
    interference_queue = 0
    opponent_interference_queue = 0


def check_game_over():
    """检查游戏是否结束"""
    # 检查是否有方块到达顶部
    for x in range(GAME_AREA_WIDTH):
        if grid[0][x] is not None or stone_grid[0][x] is not None:
            return True

    # 检查游戏时间（可选）
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
            reset_game()
            current_state = GAME
        elif selected_option == 1:  # 角色选择
            current_state = CHARACTER_SELECT
        elif selected_option == 2:  # 退出
            pygame.quit()
            sys.exit()


def handle_character_select_input(event):
    """处理角色选择输入"""
    global selected_character, current_character, current_state

    if event.key == pygame.K_UP:
        selected_character = (selected_character - 1) % len(character_options)
    elif event.key == pygame.K_DOWN:
        selected_character = (selected_character + 1) % len(character_options)
    elif event.key == pygame.K_RETURN:
        current_character = character_options[selected_character]
        current_state = MENU


def handle_game_input(event):
    """处理游戏输入"""
    global current_blocks, current_speed_level, game_speed

    if event.key == pygame.K_LEFT:
        new_blocks = [{"color": block["color"], "x": block["x"] - 1, "y": block["y"]} for block in current_blocks]
        if not check_collision(new_blocks):
            current_blocks = new_blocks

    elif event.key == pygame.K_RIGHT:
        new_blocks = [{"color": block["color"], "x": block["x"] + 1, "y": block["y"]} for block in current_blocks]
        if not check_collision(new_blocks):
            current_blocks = new_blocks

    elif event.key == pygame.K_DOWN:
        new_blocks = [{"color": block["color"], "x": block["x"], "y": block["y"] + 1} for block in current_blocks]
        if not check_collision(new_blocks):
            current_blocks = new_blocks

    elif event.key == pygame.K_SPACE:
        current_blocks = rotate_blocks(current_blocks)

    elif event.key == pygame.K_s:
        use_skill()

    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        current_speed_level = min(current_speed_level + 1, len(speed_levels) - 1)
        game_speed = speed_levels[current_speed_level]

    elif event.key == pygame.K_MINUS:
        current_speed_level = max(current_speed_level - 1, 0)
        game_speed = speed_levels[current_speed_level]


def handle_game_over_input(event):
    """处理游戏结束输入"""
    global current_state

    if event.key == pygame.K_RETURN:
        current_state = MENU


# 游戏主循环
running = True
clock = pygame.time.Clock()
last_move_time = 0
move_delay = 100  # 移动延迟（毫秒）
last_drop_time = 0
drop_delay = 1000  # 下落延迟（毫秒）

while running:
    current_time = pygame.time.get_ticks()

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

    # 持续按键检测（用于游戏状态）
    if current_state == GAME and current_time - last_move_time > move_delay:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            new_blocks = [{"color": block["color"], "x": block["x"] - 1, "y": block["y"]} for block in current_blocks]
            if not check_collision(new_blocks):
                current_blocks = new_blocks
                last_move_time = current_time

        elif keys[pygame.K_RIGHT]:
            new_blocks = [{"color": block["color"], "x": block["x"] + 1, "y": block["y"]} for block in current_blocks]
            if not check_collision(new_blocks):
                current_blocks = new_blocks
                last_move_time = current_time

        elif keys[pygame.K_DOWN]:
            new_blocks = [{"color": block["color"], "x": block["x"], "y": block["y"] + 1} for block in current_blocks]
            if not check_collision(new_blocks):
                current_blocks = new_blocks
                last_move_time = current_time

    # 更新游戏状态
    if current_state == GAME:
        # 更新技能冷却
        if skill_cooldown > 0:
            skill_cooldown = max(0, skill_cooldown - 1 / 60)  # 假设60FPS

        # 石头生成逻辑
        if time.time() - stone_timer > 10:  # 每隔10秒生成石头
            stones = create_stones(2)
            for stone in stones:
                if not check_collision([stone]):
                    stone_grid[stone["y"]][stone["x"]] = stone["color"]
            stone_timer = time.time()

        # 石头下落逻辑
        apply_stone_gravity()

        # 更新对手
        update_opponent()

        # 自动下落
        if current_time - last_drop_time > drop_delay / game_speed:
            new_blocks = [{"color": block["color"], "x": block["x"], "y": block["y"] + 1} for block in current_blocks]
            if check_collision(new_blocks):
                place_blocks(current_blocks)
                current_blocks = create_block_group()
                if check_collision(current_blocks):
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
        screen.blit(background, (0, 0))
        draw_game_area()
        draw_grid()
        draw_current_blocks()
        draw_game_info()
    elif current_state == GAME_OVER:
        screen.blit(background, (0, 0))
        draw_game_area()
        draw_grid()
        draw_game_info()
        draw_game_over()

    pygame.display.flip()
    clock.tick(60)  # 固定帧率为60FPS

pygame.quit()
