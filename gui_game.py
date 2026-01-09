import pygame
import sys
import copy
import time
import json
from collections import deque
import heapq
from logic import (
    solve_maze_bfs, solve_maze_dfs, solve_maze_astar,
    solve_puzzle_bfs, solve_puzzle_dfs, solve_puzzle_astar,
    get_maze_dims, DEFAULT_MAZE, GOAL_STATE_PUZZLE
)
from levels import MAZE_LEVELS

# --- Constants & Config ---
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750
FPS = 60

# Colors
COLOR_BG = (15, 23, 42)
COLOR_CARD = (30, 41, 59)
COLOR_TEXT = (248, 250, 252)
COLOR_ACCENT = (244, 63, 94)
COLOR_PRIMARY = (59, 130, 246)
COLOR_WALL = (15, 23, 42)
COLOR_GRID = (51, 65, 85)
COLOR_START = (16, 185, 129)
COLOR_GOAL = (245, 158, 11)
COLOR_VISITED = (59, 130, 246, 100)
COLOR_PATH = (139, 92, 246)
COLOR_BTN = (59, 130, 246)
COLOR_BTN_HOVER = (37, 99, 235)

pygame.init()
FONT_TITLE = pygame.font.SysFont('Arial', 36, bold=True)
FONT_UI = pygame.font.SysFont('Arial', 18)
FONT_TILE = pygame.font.SysFont('Arial', 32, bold=True)
FONT_BIG = pygame.font.SysFont('Arial', 48, bold=True)

# --- Leaderboard Manager ---
class Leaderboard:
    def __init__(self, file='leaderboard.json'):
        self.file = file
        self.scores = self.load()

    def load(self):
        try:
            with open(self.file, 'r') as f:
                return json.load(f)
        except:
            return []

    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.scores, f)

    def add_score(self, name, level, time_val):
        self.scores.append({'name': name, 'level': level, 'time': round(time_val, 2)})
        self.scores.sort(key=lambda x: x['time']) # Sort by time
        self.save()

    def get_top_scores(self, level):
        level_scores = [s for s in self.scores if s['level'] == level]
        return sorted(level_scores, key=lambda x: x['time'])[:5]

leaderboard = Leaderboard()

# --- UI Components ---
class Button:
    def __init__(self, x, y, w, h, text, action, color=COLOR_BTN):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = color
        self.hovered = False

    def draw(self, screen):
        c = COLOR_BTN_HOVER if self.hovered else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=8)
        
        txt_surf = FONT_UI.render(self.text, True, COLOR_TEXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def update(self, mouse_pos, mouse_click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_click:
            self.action()

class GameState:
    def __init__(self):
        self.mode = 'MENU' # MENU, MAZE, PUZZLE, LEADERBOARD, NAME_INPUT
        
        # Maze
        self.current_level = 0
        self.maze = copy.deepcopy(MAZE_LEVELS[0])
        self.maze_player_pos = self.find_pos('S')
        self.maze_algo = 'bfs'
        self.maze_visualizing = False
        self.maze_vis_steps = []
        self.maze_vis_path = []
        self.maze_vis_idx = 0
        self.maze_timer_start = None
        self.maze_elapsed = 0
        self.maze_finished = False
        
        # Input
        self.player_name = ""
        
        # Puzzle
        self.puzzle_state = ((1,2,3), (4,5,6), (7,8,0))
        self.puzzle_algo = 'astar'
        self.puzzle_visualizing = False
        self.puzzle_vis_steps = []
        self.puzzle_vis_idx = 0
        
    def find_pos(self, char):
        for r, row in enumerate(self.maze):
            for c, val in enumerate(row):
                if val == char: return (r, c)
        return (0, 0)

    def switch_to_maze(self):
        self.mode = 'MAZE'
        self.load_level(self.current_level)

    def switch_to_puzzle(self):
        self.mode = 'PUZZLE'
        self.puzzle_state = ((1,2,3), (4,5,6), (7,8,0))
        self.reset_puzzle_vis()
        
    def switch_to_leaderboard(self):
        self.mode = 'LEADERBOARD'

    def load_level(self, idx):
        if idx >= len(MAZE_LEVELS): idx = 0 # Loop or stay at max
        self.current_level = idx
        self.maze = copy.deepcopy(MAZE_LEVELS[idx])
        self.maze_player_pos = self.find_pos('S')
        self.maze_timer_start = None
        self.maze_elapsed = 0
        self.maze_finished = False
        self.reset_maze_vis()

    def reset_maze_vis(self):
        self.maze_visualizing = False
        self.maze_vis_steps = []
        self.maze_vis_path = []
        self.maze_vis_idx = 0

    def reset_puzzle_vis(self):
        self.puzzle_visualizing = False
        self.puzzle_vis_steps = []
        self.puzzle_vis_idx = 0
        
    def submit_score(self):
        if self.player_name:
            leaderboard.add_score(self.player_name, self.current_level + 1, self.maze_elapsed)
            self.player_name = "" # Reset
            # Go to next level
            if self.current_level < len(MAZE_LEVELS) - 1:
                self.load_level(self.current_level + 1)
                self.mode = 'MAZE'
            else:
                self.switch_to_leaderboard() # Finished all

gameState = GameState()

# --- Logic Wrappers ---

def run_maze_solve():
    gameState.reset_maze_vis()
    algo = gameState.maze_algo
    res = {}
    if algo == 'bfs': res = solve_maze_bfs(gameState.maze)
    elif algo == 'dfs': res = solve_maze_dfs(gameState.maze)
    elif algo == 'astar': res = solve_maze_astar(gameState.maze)
    
    if res.get('status') in ['success', 'not_found']:
        gameState.maze_vis_steps = res.get('visited', [])
        gameState.maze_vis_path = res.get('path', [])
        gameState.maze_visualizing = True

def run_puzzle_solve():
    gameState.reset_puzzle_vis()
    algo = gameState.puzzle_algo
    curr = tuple(tuple(row) for row in gameState.puzzle_state)
    res = {}
    if algo == 'bfs': res = solve_puzzle_bfs(curr)
    elif algo == 'dfs': res = solve_puzzle_dfs(curr)
    elif algo == 'astar': res = solve_puzzle_astar(curr)

    if res.get('status') == 'success':
        gameState.puzzle_vis_steps = res.get('path', [])
        gameState.puzzle_visualizing = True

def run_puzzle_scramble():
    import random
    state = [list(r) for r in gameState.puzzle_state]
    empty_r, empty_c = 2, 2
    for r in range(3):
        for c in range(3):
            if state[r][c] == 0: empty_r, empty_c = r, c; break
    for _ in range(100):
        moves = []
        if empty_r > 0: moves.append((-1, 0))
        if empty_r < 2: moves.append((1, 0))
        if empty_c > 0: moves.append((0, -1))
        if empty_c < 2: moves.append((0, 1))
        dr, dc = random.choice(moves)
        nr, nc = empty_r + dr, empty_c + dc
        state[empty_r][empty_c] = state[nr][nc]
        state[nr][nc] = 0
        empty_r, empty_c = nr, nc
    gameState.puzzle_state = tuple(tuple(r) for r in state)

# --- Drawing ---

def draw_maze(screen):
    rows = len(gameState.maze)
    cols = len(gameState.maze[0])
    cell_size = min(40, 700 // cols)
    
    grid_w = cols * cell_size
    grid_h = rows * cell_size
    
    start_x = (SCREEN_WIDTH - grid_w) // 2
    start_y = 120
    
    # Cells
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * cell_size
            y = start_y + r * cell_size
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            
            char = gameState.maze[r][c]
            color = COLOR_GRID
            if char == '1': color = COLOR_WALL
            elif char == 'S': color = COLOR_START
            elif char == 'G': color = COLOR_GOAL
            
            # Vis
            if gameState.maze_visualizing:
                if (r,c) in gameState.maze_vis_path and gameState.maze_vis_idx >= len(gameState.maze_vis_steps):
                    color = COLOR_PATH
                elif (r,c) in gameState.maze_vis_steps[:gameState.maze_vis_idx]:
                    color = (59, 130, 246)

            pygame.draw.rect(screen, color, rect, border_radius=4)
            if char in ['S', 'G']:
                txt = FONT_UI.render(char, True, COLOR_TEXT)
                screen.blit(txt, txt.get_rect(center=rect.center))

    # Player
    if not gameState.maze_visualizing and not gameState.maze_finished:
        pr, pc = gameState.maze_player_pos
        px = start_x + pc * cell_size
        py = start_y + pr * cell_size
        pygame.draw.circle(screen, COLOR_ACCENT, (px + cell_size//2, py + cell_size//2), cell_size//3)

    # Info
    info_x = 20
    info_y = 100
    level_txt = FONT_TITLE.render(f"Level {gameState.current_level + 1}", True, COLOR_TEXT)
    screen.blit(level_txt, (info_x, info_y))
    
    timer_txt = FONT_TITLE.render(f"Time: {gameState.maze_elapsed:.1f}s", True, COLOR_ACCENT)
    screen.blit(timer_txt, (info_x, info_y + 50))
    
    instruct = FONT_UI.render("Arrows/WASD to move", True, COLOR_TEXT)
    screen.blit(instruct, (info_x, info_y + 100))

def draw_leaderboard(screen):
    title = FONT_BIG.render("Leaderboard", True, COLOR_ACCENT)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    y = 200
    for level in range(1, len(MAZE_LEVELS) + 1):
        lvl_title = FONT_TITLE.render(f"Level {level}", True, COLOR_PRIMARY)
        screen.blit(lvl_title, (100, y))
        
        scores = leaderboard.get_top_scores(level)
        sy = y + 40
        if not scores:
            t = FONT_UI.render("No scores yet", True, COLOR_TEXT)
            screen.blit(t, (120, sy))
        
        for s in scores:
            t = FONT_UI.render(f"{s['name']}: {s['time']}s", True, COLOR_TEXT)
            screen.blit(t, (120, sy))
            sy += 25
            
        y += 200

def draw_name_input(screen):
    # Overlay
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0,0,0,200))
    screen.blit(s, (0,0))
    
    box = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 200)
    pygame.draw.rect(screen, COLOR_CARD, box, border_radius=12)
    
    title = FONT_TITLE.render("Level Complete!", True, COLOR_GOAL)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60)))
    
    time_show = FONT_UI.render(f"Time: {gameState.maze_elapsed:.2f}s", True, COLOR_TEXT)
    screen.blit(time_show, time_show.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
    
    prompt = FONT_UI.render("Enter Name & Press Enter:", True, COLOR_TEXT)
    screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
    
    name_txt = FONT_TITLE.render(gameState.player_name + "_", True, COLOR_ACCENT)
    screen.blit(name_txt, name_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)))

    pygame.display.set_caption("Escape World")
    clock = pygame.time.Clock()
    
    # Buttons
    b_maze = Button(20, 20, 100, 40, "Maze", gameState.switch_to_maze)
    b_puz = Button(130, 20, 100, 40, "Puzzle", gameState.switch_to_puzzle)
    b_lead = Button(240, 20, 120, 40, "Leaderboard", gameState.switch_to_leaderboard)
    
    b_vis = Button(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 70, 120, 50, "Visualize", 
                   lambda: run_maze_solve() if gameState.mode == 'MAZE' else run_puzzle_solve())
    b_scram = Button(SCREEN_WIDTH - 270, SCREEN_HEIGHT - 70, 120, 50, "Scramble", run_puzzle_scramble)
    
    running = True
    while running:
        screen.fill(COLOR_BG)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: mouse_click = True
            
            elif event.type == pygame.KEYDOWN:
                if gameState.mode == 'NAME_INPUT':
                    if event.key == pygame.K_RETURN:
                        gameState.submit_score()
                    elif event.key == pygame.K_BACKSPACE:
                        gameState.player_name = gameState.player_name[:-1]
                    else:
                        if len(gameState.player_name) < 15:
                            gameState.player_name += event.unicode
                            
                elif gameState.mode == 'MAZE' and not gameState.maze_visualizing and not gameState.maze_finished:
                    if gameState.maze_timer_start is None:
                        gameState.maze_timer_start = time.time()
                        
                    pr, pc = gameState.maze_player_pos
                    dr, dc = 0, 0
                    if event.key in [pygame.K_UP, pygame.K_w]: dr = -1
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: dr = 1
                    elif event.key in [pygame.K_LEFT, pygame.K_a]: dc = -1
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: dc = 1
                    
                    nr, nc = pr + dr, pc + dc
                    if 0 <= nr < len(gameState.maze) and 0 <= nc < len(gameState.maze[0]):
                        if gameState.maze[nr][nc] != '1':
                            gameState.maze_player_pos = (nr, nc)
                            if gameState.maze[nr][nc] == 'G':
                                gameState.maze_finished = True
                                gameState.mode = 'NAME_INPUT'

        # Updates
        b_maze.update(mouse_pos, mouse_click)
        b_puz.update(mouse_pos, mouse_click)
        b_lead.update(mouse_pos, mouse_click)
        
        if gameState.mode in ['MAZE', 'PUZZLE'] and not gameState.mode == 'NAME_INPUT':
            b_vis.update(mouse_pos, mouse_click)
        if gameState.mode == 'PUZZLE':
            b_scram.update(mouse_pos, mouse_click)
            
        # Draw Top Bar
        b_maze.draw(screen)
        b_puz.draw(screen)
        b_lead.draw(screen)
        
        # Mode Draw
        if gameState.mode == 'MAZE' or gameState.mode == 'NAME_INPUT':
            if gameState.maze_timer_start and not gameState.maze_finished:
                gameState.maze_elapsed = time.time() - gameState.maze_timer_start
            
            if gameState.maze_visualizing:
                 if gameState.maze_vis_idx < len(gameState.maze_vis_steps) + 20: 
                    gameState.maze_vis_idx += 1
            
            draw_maze(screen)
            b_vis.draw(screen)
            
            if gameState.mode == 'NAME_INPUT':
                draw_name_input(screen)
                
        elif gameState.mode == 'LEADERBOARD':
            draw_leaderboard(screen)
            
        elif gameState.mode == 'PUZZLE':
            # Simplified puzzle draw for brevity - reuse rect logic
            pass # (Implement puzzle draw here similarly to before if needed or copy from previous)
            # Re-implementing puzzle draw quickly
            start_x = (SCREEN_WIDTH - 320) // 2
            start_y = 200
            for r in range(3):
                for c in range(3):
                    val = gameState.puzzle_state[r][c]
                    rect = pygame.Rect(start_x + c*110, start_y + r*110, 100, 100)
                    if val != 0:
                        pygame.draw.rect(screen, COLOR_GRID, rect, border_radius=8)
                        t = FONT_TILE.render(str(val), True, COLOR_TEXT)
                        screen.blit(t, t.get_rect(center=rect.center))
                    else:
                        pygame.draw.rect(screen, (30,30,30), rect, border_radius=8)
            b_vis.draw(screen)
            b_scram.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
