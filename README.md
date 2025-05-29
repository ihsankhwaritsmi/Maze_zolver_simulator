# Maze Solver Simulator

| Name                         | NRP        | Class                                |
| ---------------------------- | ---------- | ------------------------------------ |
| Ainun Nadhifah Syamsiyah     | 5025221053 | Design and Analysis of Algorithm (K) |
| Muhammad Ihsan Al Khwaritsmi | 5025221211 | Design and Analysis of Algorithm (K) |
| Putu Indra Mahendra          | 5025221215 | Design and Analysis of Algorithm (K) |

A Python-based maze solver visualization tool that demonstrates different pathfinding algorithms (DFS, BFS, and A\*) in action. The application provides an interactive interface to generate random mazes and visualize how different algorithms solve them.

## Features

- Interactive 100x100 grid maze visualization
- Multiple pathfinding algorithms:
  - Depth-First Search (DFS)
  - Breadth-First Search (BFS)
  - A\* Search Algorithm
- Adjustable obstacle density (0-100%)
- Real-time visualization of algorithm exploration
- Clear visual distinction between:
  - Start point (green)
  - End point (red)
  - Obstacles (black)
  - Explored cells (light blue)
  - Current search cell (orange)
  - Final path (blue)

## Requirements

- Python 3.x
- tkinter (usually comes with Python installation)

## How to Run

1. Make sure you have Python installed on your system
2. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Launch the application
2. Use the "Generate Obstacles" button to create a random maze
3. Adjust the obstacle density using the slider if desired
4. Choose an algorithm to solve the maze:
   - "Solve with DFS" for Depth-First Search
   - "Solve with BFS" for Breadth-First Search
   - "Solve with A*" for A* Search Algorithm
5. Watch the algorithm solve the maze in real-time
6. Use "Clear Solution" to remove the current solution
7. Use "Reset Maze" to start fresh

## Notes

- The start point is always at (0,0) - top-left corner
- The end point is always at (99,99) - bottom-right corner
- The application ensures that start and end points are always accessible
- If no solution is found, you'll be prompted to try again or reset the maze
