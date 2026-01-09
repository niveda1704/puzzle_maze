# Escape World (Maze & 8-Puzzle)

**Escape World** is an interactive web-based visualization tool and game for pathfinding algorithms (BFS, DFS, A*). It features a playable Maze mode and an 8-Puzzle solver.

![Escape World Screenshot](https://via.placeholder.com/800x400?text=Escape+World+Preview)

## Features

-   **Maze Solver**: Visualize BFS, DFS, and A* algorithms finding paths in real-time.
-   **Play Mode**: Interactive maze game where you control the player (Red Dot) to reach the Goal (G).
    -   **Levels**: Progress through multiple levels of increasing difficulty.
    -   **Leaderboard**: Compete for the fastest time.
-   **8-Puzzle Solver**: Interactive tile puzzle with an AI auto-solver and scramble feature.
-   **Modern UI**: Glassmorphism design, neon aesthetics, and smooth animations.

## Tech Stack

-   **Frontend**: HTML5, CSS3 (Variables, Flexbox, Grid, Animations), JavaScript (Fetch API).
-   **Backend**: Python (Flask).
-   **Deployment**: Ready for Render/Heroku (includes `Procfile` and `gunicorn`).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/niveda1704/puzzle_maze.git
    cd puzzle_maze
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    python app.py
    ```
    Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Deployment on Render

1.  Create a new **Web Service** on [Render](https://render.com).
2.  Connect this repository.
3.  Use the following settings:
    -   **Runtime**: Python 3
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn app:app`
4.  Deploy!
