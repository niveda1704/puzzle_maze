from collections import deque
import heapq
import copy

# --- MAZE LOGIC ---

DEFAULT_MAZE = [
    ['S','0','0','1','0','1','0','0','0','1'],
    ['1','1','0','1','0','0','0','1','0','1'],
    ['0','0','0','1','0','1','1','1','0','0'],
    ['0','1','1','1','0','0','0','0','1','0'],
    ['0','0','0','0','1','1','1','0','1','0'],
    ['1','1','1','0','0','0','1','0','0','0'],
    ['0','0','0','0','1','0','0','0','1','0'],
    ['0','1','1','1','1','1','1','1','1','0'],
    ['0','0','0','0','0','0','0','0','0','G']
]

def get_maze_dims(maze):
    return len(maze), len(maze[0])

def find_pos(maze, symbol):
    rows, cols = get_maze_dims(maze)
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == symbol:
                return i, j
    return None

def is_valid(maze, x, y):
    rows, cols = get_maze_dims(maze)
    return 0 <= x < rows and 0 <= y < cols and maze[x][y] != '1'

MAZE_MOVES = [(-1,0), (1,0), (0,-1), (0,1)]

def solve_maze_bfs(maze):
    start = find_pos(maze, 'S')
    goal = find_pos(maze, 'G')
    if not start or not goal: return {'error': 'Start or Goal missing'}
    
    queue = deque([(start, [start])])
    visited = set([start])
    visited_history = [start] # For visualization
    
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return {'status': 'success', 'path': path, 'visited': visited_history}
        
        for dx, dy in MAZE_MOVES:
            nx, ny = x+dx, y+dy
            if is_valid(maze, nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                visited_history.append((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return {'status': 'not_found', 'visited': visited_history}

def solve_maze_dfs(maze):
    start = find_pos(maze, 'S')
    goal = find_pos(maze, 'G')
    if not start or not goal: return {'error': 'Start or Goal missing'}

    stack = [(start, [start])]
    visited = set()
    visited_history = []
    
    while stack:
        (x, y), path = stack.pop()
        
        # In DFS, we often mark visited upon popping or pushing. 
        # The user's code marks before pushing children if not visited.
        # But for exact path matching, let's stick to their logic:
        # User code: if (x,y) not in visited: visited.add...
        
        if (x, y) == goal:
            visited_history.append((x,y))
            return {'status': 'success', 'path': path, 'visited': visited_history}
        
        if (x, y) not in visited:
            visited.add((x, y))
            visited_history.append((x, y))
            
            # User's MOVES: typically defined globally.
            # Note: DFS direction order matters for the shape of the path.
            for dx, dy in MAZE_MOVES:
                nx, ny = x+dx, y+dy
                if is_valid(maze, nx, ny):
                     # In user code, they don't check 'visited' here for pushing, 
                     # but they check 'if (x,y) not in visited' after popping.
                     # This effectively allows re-visiting nodes in stack but discarding them later.
                     stack.append(((nx, ny), path + [(nx, ny)]))
    return {'status': 'not_found', 'visited': visited_history}

def maze_heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def solve_maze_astar(maze):
    start = find_pos(maze, 'S')
    goal = find_pos(maze, 'G')
    if not start or not goal: return {'error': 'Start or Goal missing'}

    pq = []
    heapq.heappush(pq, (0, start, [start]))
    visited = set()
    visited_history = []

    while pq:
        f, current, path = heapq.heappop(pq)
        
        # User Logic: checks goal immediately
        if current == goal:
            visited_history.append(current)
            return {'status': 'success', 'path': path, 'visited': visited_history}
        
        if current not in visited:
            visited.add(current)
            visited_history.append(current)
            
            for dx, dy in MAZE_MOVES:
                nx, ny = current[0]+dx, current[1]+dy
                if is_valid(maze, nx, ny):
                    g = len(path)
                    h = maze_heuristic((nx, ny), goal)
                    heapq.heappush(pq, (g+h, (nx, ny), path + [(nx, ny)]))
    return {'status': 'not_found', 'visited': visited_history}


# --- 8-PUZZLE LOGIC ---

GOAL_STATE_PUZZLE = ((1,2,3),
                     (4,5,6),
                     (7,8,0))

PUZZLE_MOVES = [(-1,0),(1,0),(0,-1),(0,1)]

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def swap(state, x1, y1, x2, y2):
    state = [list(row) for row in state]
    state[x1][y1], state[x2][y2] = state[x2][y2], state[x1][y1]
    return tuple(tuple(row) for row in state)

def get_neighbors(state):
    neighbors = []
    x, y = find_zero(state)
    for dx, dy in PUZZLE_MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            neighbors.append(swap(state, x, y, nx, ny))
    return neighbors

def solve_puzzle_bfs(start):
    queue = deque([(start, [])])
    visited = set([start])
    visited_history = [start]

    while queue:
        state, path = queue.popleft()
        if state == GOAL_STATE_PUZZLE:
            return {'status': 'success', 'path': path + [state], 'visited': visited_history}

        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                visited_history.append(neighbor)
                queue.append((neighbor, path + [state]))
    return {'status': 'not_found', 'visited': visited_history}

def solve_puzzle_dfs(start):
    stack = [(start, [])]
    visited = set()
    visited_history = []

    while stack:
        state, path = stack.pop()
        if state == GOAL_STATE_PUZZLE:
            visited_history.append(state)
            return {'status': 'success', 'path': path + [state], 'visited': visited_history}

        if state not in visited:
            visited.add(state)
            visited_history.append(state)
            for neighbor in get_neighbors(state):
                stack.append((neighbor, path + [state]))
    return {'status': 'not_found', 'visited': visited_history}

def puzzle_heuristic(state):
    dist = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                x, y = divmod(val-1, 3)
                dist += abs(i-x) + abs(j-y)
    return dist

def solve_puzzle_astar(start):
    pq = []
    # (f, g, state, path)
    heapq.heappush(pq, (puzzle_heuristic(start), 0, start, []))
    visited = set()
    visited_history = []

    while pq:
        f, g, state, path = heapq.heappop(pq)

        if state == GOAL_STATE_PUZZLE:
            visited_history.append(state)
            return {'status': 'success', 'path': path + [state], 'visited': visited_history}

        if state not in visited:
            visited.add(state)
            visited_history.append(state)
            for neighbor in get_neighbors(state):
                heapq.heappush(pq,
                    (g + 1 + puzzle_heuristic(neighbor), g + 1, neighbor, path + [state]))
    return {'status': 'not_found', 'visited': visited_history}
