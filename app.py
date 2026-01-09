from flask import Flask, request, jsonify, render_template
from logic import (
    solve_maze_bfs, solve_maze_dfs, solve_maze_astar,
    solve_puzzle_bfs, solve_puzzle_dfs, solve_puzzle_astar,
    DEFAULT_MAZE
)
from levels import MAZE_LEVELS
import json
import os

app = Flask(__name__)
LEADERBOARD_FILE = 'leaderboard.json'

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE): return []
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/levels')
def get_levels():
    return jsonify(MAZE_LEVELS)

@app.route('/api/leaderboard', methods=['GET', 'POST'])
def handle_leaderboard():
    scores = load_leaderboard()
    if request.method == 'POST':
        data = request.json
        # data: {name, level, time}
        scores.append(data)
        # Sort by level (desc) then time (asc) ?? Or just time?
        # Usually leaderboard is per level.
        # Let's save plain list and filter in frontend or here.
        save_leaderboard(scores)
        return jsonify({'status': 'saved'})
    return jsonify(scores)

@app.route('/api/solve/maze', methods=['POST'])
def solve_maze():
    data = request.json
    maze = data.get('maze')
    algorithm = data.get('algorithm')
    
    if algorithm == 'bfs':
        result = solve_maze_bfs(maze)
    elif algorithm == 'dfs':
        result = solve_maze_dfs(maze)
    elif algorithm == 'astar':
        result = solve_maze_astar(maze)
    else:
        return jsonify({'error': 'Invalid algorithm'}), 400
    
    return jsonify(result)

@app.route('/api/solve/puzzle', methods=['POST'])
def solve_puzzle():
    data = request.json
    start_state = tuple(tuple(row) for row in data.get('state'))
    algorithm = data.get('algorithm')
    
    # Simple validation
    flat = [val for row in start_state for val in row]
    if sorted(flat) != list(range(9)):
         return jsonify({'error': 'Invalid puzzle state'}), 400

    if algorithm == 'bfs':
        result = solve_puzzle_bfs(start_state)
    elif algorithm == 'dfs':
        result = solve_puzzle_dfs(start_state)
    elif algorithm == 'astar':
        result = solve_puzzle_astar(start_state)
    else:
        return jsonify({'error': 'Invalid algorithm'}), 400
        
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
