import pygame
import sys
import random
from collections import deque

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 500, 500
WHITE, BLACK, YELLOW, GREEN, RED = (255, 255, 255), (0, 0, 0), (255, 255, 0), (0, 255, 0), (255, 0, 0)
N_ROWS, N_COLS = 200, 200
RATIO_OF_SPACE_TO_WALL = 3
N_WALLS = N_ROWS * N_COLS // RATIO_OF_SPACE_TO_WALL
N_ROWS_TO_DISPLAY, N_COLS_TO_DISPLAY = 11, 11
MID_ROW, MID_COL = N_ROWS_TO_DISPLAY // 2, N_COLS_TO_DISPLAY // 2
WALL_WIDTH, WALL_HEIGHT = WINDOW_WIDTH / N_ROWS_TO_DISPLAY, WINDOW_HEIGHT / N_COLS_TO_DISPLAY
N_CATCHERS = 200
FONT_SIZE_LARGE, FONT_SIZE_MEDIUM = 100, 50
FPS = 60

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Get 'em")

class Map:
    def __init__(self):
        self.the_walls, self.the_tokens = {}, {}
        
    def create_random(self):
        for i in range(N_COLS):
            self.the_walls[(0, i)] = Wall(0, i)
            self.the_walls[(N_ROWS - 1, i)] = Wall(N_ROWS - 1, i)
        for i in range(N_ROWS):
            self.the_walls[(i, 0)] = Wall(i, 0)
            self.the_walls[(i, N_COLS - 1)] = Wall(i, N_COLS - 1)
        for _ in range(N_WALLS):
            a, b = random.randint(1, N_ROWS - 2), random.randint(1, N_COLS - 2)
            self.the_walls[(a, b)] = Wall(a, b)

        # Find a path from player to all tokens using BFS
        player_row, player_col = MID_ROW, MID_COL
        visited = set()
        queue = deque([(player_row, player_col)])
        while queue:
            current_row, current_col = queue.popleft()
            if (current_row, current_col) in visited or (current_row, current_col) in self.the_walls:
                continue
            visited.add((current_row, current_col))
            self.the_tokens[(current_row, current_col)] = Token(current_row, current_col)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_row, new_col = current_row + dr, current_col + dc
                if 0 <= new_row < N_ROWS and 0 <= new_col < N_COLS:
                    queue.append((new_row, new_col))

        #Fill all gaps with walls
        for i in range(N_ROWS):
            for j in range(N_COLS):
                if (i,j) not in self.the_walls and (i,j) not in self.the_tokens:
                    self.the_walls[(i,j)] = Wall(i, j)

    def remove_element(self, row, col):
        self.the_walls.pop((row, col), None)
        self.the_tokens.pop((row, col), None)
            
    def draw(self, screen, first_row_displayed, first_col_displayed):
        for i in range(first_row_displayed, first_row_displayed + N_ROWS_TO_DISPLAY):
            for j in range(first_col_displayed, first_col_displayed + N_COLS_TO_DISPLAY):
                if (i, j) in self.the_walls:
                    self.the_walls[(i, j)].draw(screen, first_row_displayed, first_col_displayed)
                if (i, j) in self.the_tokens:
                    self.the_tokens[(i, j)].draw(screen, first_row_displayed, first_col_displayed)

    def check_element(self, character, r, c):
        character_row, character_col = character.get_pos()
        new_pos = (character_row + r, character_col + c)
        if new_pos in self.the_walls:
            return 'Wall'
        if new_pos in self.the_tokens:
            return 'Token'
        return 'None/Unknown'

class Wall:
    def __init__(self, row, col):
        self.row, self.col = row, col
        
    def draw(self, screen, first_row_displayed, first_col_displayed):
        pygame.draw.rect(screen, WHITE, ((self.col - first_col_displayed) * WALL_WIDTH + 5, 
                                         (self.row - first_row_displayed) * WALL_HEIGHT + 5, 
                                         WALL_WIDTH - 10, WALL_HEIGHT - 10))

class Token:
    def __init__(self, row, col):
        self.row, self.col = row, col
        
    def draw(self, screen, first_row_displayed, first_col_displayed):
        pygame.draw.circle(screen, YELLOW, ((self.col - first_col_displayed) * WALL_WIDTH + (WALL_WIDTH / 2), 
                                            (self.row - first_row_displayed) * WALL_HEIGHT + (WALL_HEIGHT / 2)), 5)

class Character:
    def __init__(self, row, col):
        self.row, self.col = row, col

    def get_pos(self):
        return self.row, self.col

    def move(self, r, c):
        self.row += r
        self.col += c

    def get_distance(self, a_character):
        a_character_row, a_character_col = a_character.get_pos()
        return self.row - a_character_row, self.col - a_character_col

class Player(Character):
    def draw(self, screen, first_row_displayed, first_col_displayed):
        pygame.draw.circle(screen, GREEN, ((self.col - first_col_displayed) * WALL_WIDTH + (WALL_WIDTH / 2), 
                                           (self.row - first_row_displayed) * WALL_HEIGHT + (WALL_HEIGHT / 2)), 
                                           WALL_WIDTH / 2 - 5)

class Catcher(Character):
    def draw(self, screen, first_row_displayed, first_col_displayed):
        pygame.draw.circle(screen, RED, ((self.col - first_col_displayed) * WALL_WIDTH + (WALL_WIDTH / 2), 
                                         (self.row - first_row_displayed) * WALL_HEIGHT + (WALL_HEIGHT / 2)), 
                                         WALL_WIDTH / 2 - 5)

def initialize_game():
    global map, player1, catchers, score, wait, time_to_wait, running
    map = Map()
    map.create_random()
    score = 0
    player1 = Player(MID_ROW, MID_COL)
    catchers = []
    for _ in range(N_CATCHERS):
        a = random.randint(1, N_ROWS - 2)
        b = random.randint(1, N_COLS - 2)
        catchers.append(Catcher(a,b))
        map.remove_element(a,b)    
    wait, time_to_wait = 0, 60
    running = True

def handle_events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event.key)

def handle_keydown(key):
    if key == pygame.K_LEFT and map.check_element(player1, 0, -1) != 'Wall':
        player1.move(0, -1) 
    elif key == pygame.K_RIGHT and map.check_element(player1, 0, 1) != 'Wall':
        player1.move(0, 1)
    elif key == pygame.K_UP and map.check_element(player1, -1, 0) != 'Wall':
        player1.move(-1, 0)
    elif key == pygame.K_DOWN and map.check_element(player1, 1, 0) != 'Wall':
        player1.move(1, 0)

def update_characters():
    global score, wait, time_to_wait, running
    if map.check_element(player1, 0, 0) == 'Token':
        score += 1
        player1_row, player1_col = player1.get_pos()
        map.remove_element(player1_row, player1_col)
    wait += 1
    if wait >= time_to_wait:
        move_catchers()
        wait = 0
        time_to_wait = max(time_to_wait - 1, 10)
    


def move_catchers():
    for catcher in catchers:
        catcher_distance_row, catcher_distance_col = catcher.get_distance(player1)
        move_catcher(catcher, catcher_distance_row, catcher_distance_col)

def move_catcher(catcher, row_dist, col_dist):
    roll = random.randint(1, 2)
    if roll == 1 and col_dist != 0:
        move_catcher_horizontal(catcher, col_dist)
    elif roll == 2 and row_dist != 0:
        move_catcher_vertical(catcher, row_dist)
    catcher_row, catcher_col = catcher.get_pos()
    if map.check_element(catcher, 0, 0) == 'Token':
        map.remove_element(catcher_row, catcher_col)

def move_catcher_horizontal(catcher, col_dist):
    if col_dist > 0 and map.check_element(catcher, 0, -1) != 'Wall':
        catcher.move(0, -1)
    elif col_dist < 0 and map.check_element(catcher, 0, 1) != 'Wall':
        catcher.move(0, 1)

def move_catcher_vertical(catcher, row_dist):
    if row_dist > 0 and map.check_element(catcher, -1, 0) != 'Wall':
        catcher.move(-1, 0)
    elif row_dist < 0 and map.check_element(catcher, 1, 0) != 'Wall':
        catcher.move(1, 0)

def check_catcher_collision():
    for catcher in catchers:
        if catcher.get_distance(player1) == (0, 0):
            return True
    return False

def draw_game():
    screen.fill(BLACK)
    first_row_displayed, first_col_displayed = determine_display_area()
    map.draw(screen, first_row_displayed, first_col_displayed)
    player1.draw(screen, first_row_displayed, first_col_displayed)
    for catcher in catchers:
        catcher.draw(screen, first_row_displayed, first_col_displayed)
    pygame.display.flip()

def determine_display_area():
    player1_row, player1_col = player1.get_pos()
    first_row_displayed = max(min(player1_row - MID_ROW, N_ROWS - N_ROWS_TO_DISPLAY), 0)
    first_col_displayed = max(min(player1_col - MID_COL, N_COLS - N_COLS_TO_DISPLAY), 0)
    return first_row_displayed, first_col_displayed

def check_for_end_game():
    if not map.the_tokens:
        running = False
        display_win_message()
    if check_catcher_collision():
        running = False
        display_game_over()


def display_win_message():
    font1 = pygame.font.Font(None, FONT_SIZE_LARGE)
    text1 = font1.render('You Win!', True, GREEN)
    font2 = pygame.font.Font(None, FONT_SIZE_MEDIUM)
    text2 = font2.render('Score: ' + str(score), True, GREEN)
    text_rect1 = text1.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    text_rect2 = text2.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))

    # Outline text
    outline_positions1 = [(text_rect1.x + dx, text_rect1.y + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy]
    outline_positions2 = [(text_rect2.x + dx, text_rect2.y + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for pos in outline_positions1:
            screen.blit(font1.render('You Win!', True, BLACK), pos)
        screen.blit(text1, text_rect1)

        for pos in outline_positions2:
            screen.blit(font2.render('Score: ' + str(score), True, BLACK), pos)
        screen.blit(text2, text_rect2)
        pygame.display.flip()
        clock.tick(FPS)

def display_game_over():
    font1 = pygame.font.Font(None, FONT_SIZE_LARGE)
    text1 = font1.render('Game Over', True, RED)
    font2 = pygame.font.Font(None, FONT_SIZE_MEDIUM)
    text2 = font2.render('Score: ' + str(score), True, RED)
    text_rect1 = text1.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    text_rect2 = text2.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
    
    # Outline text
    outline_positions1 = [(text_rect1.x + dx, text_rect1.y + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy]
    outline_positions2 = [(text_rect2.x + dx, text_rect2.y + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy]
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for pos in outline_positions1:
            screen.blit(font1.render('Game Over', True, BLACK), pos)
        screen.blit(text1, text_rect1)

        for pos in outline_positions2:
            screen.blit(font2.render('Score: ' + str(score), True, BLACK), pos)             
        screen.blit(text2, text_rect2)
        pygame.display.flip()
        clock.tick(FPS)

# Main Game Loop
initialize_game()
while running:
    handle_events()
    update_characters()
    draw_game()
    check_for_end_game()
    clock.tick(FPS)
display_game_over()
