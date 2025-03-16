import pygame
import random
import sys
import time
import os

# 新增：资源路径处理函数
def resource_path(relative_path):
    """ 获取打包后资源的绝对路径 """
    if getattr(sys, 'frozen', False):  # 判断是否在打包后的环境中
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)  # 确保括号闭合

# 初始化Pygame
pygame.init()
pygame.mixer.init()  # 确保音频系统初始化

# 屏幕尺寸
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 1020

# 方块尺寸
BLOCK_SIZE = 90

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eight Marvels Clash")

# 加载背景图片（修改后）
background = pygame.image.load(resource_path(os.path.join("images", "background_b.png")))

# 加载方块图片（修改后）
block_images = {
    "blue": pygame.image.load(resource_path(os.path.join("images", "blue block.png"))),
    "green": pygame.image.load(resource_path(os.path.join("images", "green block.png"))),
    "purple": pygame.image.load(resource_path(os.path.join("images", "purple block.png"))),
    "yellow": pygame.image.load(resource_path(os.path.join("images", "yellow block.png"))),
    "stone": pygame.image.load(resource_path(os.path.join("images", "stone.png")))
}

# 加载背景音乐（修改后）
pygame.mixer.music.load(resource_path(os.path.join("sounds", "z8g15-g2l2u.wav")))
pygame.mixer.music.play(-1)  # 循环播放

# 字体
font = pygame.font.Font(None, 36)

# 游戏网格
grid_width = SCREEN_WIDTH // BLOCK_SIZE
grid_height = SCREEN_HEIGHT // BLOCK_SIZE
grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]  # 普通方块网格
stone_grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]  # 石头网格

# 当前方块组
current_blocks = []

# 石头计时器
stone_timer = time.time()

# 分数
score = 0

def create_block_group():
    """生成一个新的方块组（不包含石头）"""
    colors = list(block_images.keys())
    colors.remove("stone")  # 移除石头颜色
    color1 = random.choice(colors)
    color2 = random.choice(colors)
    x = grid_width // 2 - 1
    y = 0
    return [{"color": color1, "x": x, "y": y}, {"color": color2, "x": x, "y": y + 1}]

def create_stones():
    """生成4块石头，确保不与当前方块组重叠"""
    stones = []
    for _ in range(4):
        while True:
            x = random.randint(0, grid_width - 1)
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

def draw_block(x, y, color):
    """绘制方块"""
    screen.blit(block_images[color], (x * BLOCK_SIZE, y * BLOCK_SIZE))

def draw_grid():
    """绘制网格"""
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x]:
                draw_block(x, y, grid[y][x])
            if stone_grid[y][x]:
                draw_block(x, y, stone_grid[y][x])

def draw_score():
    """绘制分数"""
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def check_collision(blocks):
    """检查方块组是否与现有方块或边界碰撞"""
    for block in blocks:
        if block["x"] < 0 or block["x"] >= grid_width or block["y"] >= grid_height:
            return True
        if block["y"] >= 0 and (grid[block["y"]][block["x"]] or stone_grid[block["y"]][block["x"]]):
            return True
    return False

def place_blocks(blocks):
    """将方块组放置到网格中"""
    for block in blocks:
        if block["y"] >= 0:
            grid[block["y"]][block["x"]] = block["color"]
    apply_gravity()  # 放置后先应用重力
    check_elimination()  # 再检查消除条件

def place_stones(stones):
    """将石头放置到石头网格中"""
    for stone in stones:
        if stone["y"] >= 0:
            stone_grid[stone["y"]][stone["x"]] = stone["color"]

def check_elimination():
    """检查并消除符合条件的方块"""
    global score
    eliminated = set()
    # 使用深度优先搜索（DFS）查找所有相连的同色方块
    visited = [[False for _ in range(grid_width)] for _ in range(grid_height)]
    for y in range(grid_height):
        for x in range(grid_width):
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
                            if 0 <= ny < grid_height and 0 <= nx < grid_width:
                                if grid[ny][nx] == color and not visited[ny][nx]:
                                    stack.append((ny, nx))
                # 如果相连的方块数量大于等于4，则标记为待消除
                if len(connected) >= 4:
                    eliminated.update(connected)
    # 消除方块并计算分数
    if eliminated:
        score += len(eliminated) - 3
        for (y, x) in eliminated:
            grid[y][x] = None
        # 检查是否有石头与消除区域相邻
        check_stone_elimination(eliminated)
        apply_gravity()  # 消除后再次应用重力
        check_elimination()  # 递归检查是否有新的消除

def check_stone_elimination(eliminated):
    """检查并消除与消除区域相邻的石头"""
    for (y, x) in eliminated:
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < grid_height and 0 <= nx < grid_width:
                if stone_grid[ny][nx]:
                    stone_grid[ny][nx] = None

def apply_gravity():
    """应用重力，使普通方块下落"""
    for x in range(grid_width):
        column = [grid[y][x] for y in range(grid_height)]
        column = [block for block in column if block is not None]
        column = [None] * (grid_height - len(column)) + column
        for y in range(grid_height):
            grid[y][x] = column[y]

def apply_stone_gravity():
    """应用重力，使石头下落"""
    for x in range(grid_width):
        for y in range(grid_height - 1, -1, -1):
            if stone_grid[y][x]:
                if y + 1 < grid_height and not stone_grid[y + 1][x] and not grid[y + 1][x]:
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

def game_over():
    """游戏结束"""
    global running
    running = False
    print("Game Over! Final Score:", score)

# 初始化当前方块组
current_blocks = create_block_group()

# 游戏主循环
running = True
clock = pygame.time.Clock()
while running:
    screen.blit(background, (0, 0))
    draw_grid()
    draw_score()

    # 石头生成逻辑
    if time.time() - stone_timer > 20:  # 每隔20秒生成4块石头
        stones = create_stones()
        for stone in stones:
            if not check_collision([stone]):
                stone_grid[stone["y"]][stone["x"]] = stone["color"]
        stone_timer = time.time()

    # 石头下落逻辑
    apply_stone_gravity()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
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

    # 自动下落
    new_blocks = [{"color": block["color"], "x": block["x"], "y": block["y"] + 1} for block in current_blocks]
    if check_collision(new_blocks):
        place_blocks(current_blocks)
        current_blocks = create_block_group()
        if check_collision(current_blocks):
            game_over()
    else:
        current_blocks = new_blocks

    # 绘制当前方块组
    for block in current_blocks:
        if block["y"] >= 0:
            draw_block(block["x"], block["y"], block["color"])

    pygame.display.flip()
    clock.tick(5)

pygame.quit()
sys.exit()