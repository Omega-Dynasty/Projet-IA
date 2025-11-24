import pygame
import random

# Initialize pygame
pygame.init()

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
COLORS = {
    'I': (255, 0, 0),
    'O': (0, 255, 0),
    'T': (0, 0, 255),
    'S': (255, 255, 0),
    'Z': (255, 165, 0),
    'L': (0, 255, 255),
    'J': (255, 0, 255),
}

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

SHAPES = [
    ('I', [(1, 1, 1, 1)]),       # I-shape 1x4
    ('O', [(1, 1), (1, 1)]),     # O-shape 2x2
    ('T', [(0, 1, 0), (1, 1, 1)]), # T-shape 2x3
    ('S', [(1, 1, 0), (0, 1, 1)]), # S-shape 2x3
    ('Z', [(0, 1, 1), (1, 1, 0)]), # Z-shape 2x3
    ('L', [(1, 0, 0), (1, 1, 1)]), # L-shape 2x3
    ('J', [(0, 0, 1), (1, 1, 1)])  # J-shape 2x3
]


font = pygame.font.SysFont(None, 30)  # Pour le compteur

def rotate_shape(shape):
    return [list(row) for row in zip(*shape[::-1])]

def draw_shape(shape, x, y):
    shape_label, shape_matrix = shape
    color = COLORS[shape_label]
    for row_idx, row in enumerate(shape_matrix):
        for col_idx, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, color, (x + col_idx*BLOCK_SIZE, y + row_idx*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def check_collision(grid, shape, x, y):
    shape_label, shape_matrix = shape
    for row_idx, row in enumerate(shape_matrix):
        for col_idx, val in enumerate(row):
            if val:
                if x + col_idx < 0 or x + col_idx >= SCREEN_WIDTH//BLOCK_SIZE or y + row_idx >= SCREEN_HEIGHT//BLOCK_SIZE:
                    return True
                if y + row_idx >= len(grid) or grid[y + row_idx][x + col_idx]:
                    return True
    return False

def clear_lines(grid):
    new_grid = [row for row in grid if any(col == 0 for col in row)]
    lines_cleared = len(grid) - len(new_grid)
    new_grid = [[0]*(SCREEN_WIDTH//BLOCK_SIZE) for _ in range(lines_cleared)] + new_grid
    return new_grid, lines_cleared

def rotate_current_shape(grid, shape, x, y):
    rotated = rotate_shape(shape[1])
    if not check_collision(grid, (shape[0], rotated), x, y):
        return (shape[0], rotated)
    return shape

def draw_grid_lines():
    # Lignes verticales fines grises
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)

def main(controller=None):
    clock = pygame.time.Clock()
    grid = [[0]*(SCREEN_WIDTH//BLOCK_SIZE) for _ in range(SCREEN_HEIGHT//BLOCK_SIZE)]
    current_shape = random.choice(SHAPES)
    current_x = SCREEN_WIDTH//BLOCK_SIZE//2 - len(current_shape[1][0])//2
    current_y = 0
    running = True
    fall_speed = 10
    fall_count = 0
    score = 0  # Compteur de lignes

    while running:
        screen.fill(BLACK)
        draw_grid_lines()  # Affiche les colonnes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and not check_collision(grid, current_shape, current_x-1, current_y):
            current_x -= 1
        if keys[pygame.K_RIGHT] and not check_collision(grid, current_shape, current_x+1, current_y):
            current_x += 1
        if keys[pygame.K_UP]:
            current_shape = rotate_current_shape(grid, current_shape, current_x, current_y)

        # Détection via caméra
        if controller:
            cmd = controller.command
            if cmd == "LEFT" and not check_collision(grid, current_shape, current_x-1, current_y):
                current_x -= 1
            elif cmd == "RIGHT" and not check_collision(grid, current_shape, current_x+1, current_y):
                current_x += 1
            elif cmd == "ROTATE":
                current_shape = rotate_current_shape(grid, current_shape, current_x, current_y)

        # Chute automatique
        fall_count += 1
        if fall_count >= fall_speed:
            if not check_collision(grid, current_shape, current_x, current_y+1):
                current_y += 1
            else:
                for row_idx, row in enumerate(current_shape[1]):
                    for col_idx, val in enumerate(row):
                        if val:
                            grid[current_y+row_idx][current_x+col_idx] = 1
                grid, cleared = clear_lines(grid)
                if cleared > 0:
                    score += cleared  # Incrémenter le compteur
                current_shape = random.choice(SHAPES)
                current_x = SCREEN_WIDTH//BLOCK_SIZE//2 - len(current_shape[1][0])//2
                current_y = 0
                if check_collision(grid, current_shape, current_x, current_y):
                    running = False
            fall_count = 0

        # Dessiner les blocs déjà posés
        for y_idx, row in enumerate(grid):
            for x_idx, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, WHITE, (x_idx*BLOCK_SIZE, y_idx*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        draw_shape(current_shape, current_x*BLOCK_SIZE, current_y*BLOCK_SIZE)

        # Affichage du score en haut à droite
        score_text = font.render(f"Lignes: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        pygame.display.update()
        clock.tick(30)

    pygame.quit()
    if controller:
        controller.release()
