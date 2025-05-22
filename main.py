import sys
import tkinter as tk
from tkinter import ttk, messagebox
import random
import collections

# Increase recursion limit for large mazes
sys.setrecursionlimit(200000)

# --- Constants ---
GRID_SIZE = 100  # Size of the grid (100x100)
CELL_SIZE = 10  # Size of each cell in pixels
CANVAS_WIDTH = GRID_SIZE * CELL_SIZE
CANVAS_HEIGHT = GRID_SIZE * CELL_SIZE

# Colors
COLOR_BG = "#F0F0F0"
COLOR_EMPTY = "white"
COLOR_OBSTACLE = "black"
COLOR_START = "green"
COLOR_END = "red"
COLOR_PATH = "blue"
COLOR_VISITED = "lightblue"  # For BFS/DFS search visualization
COLOR_CURRENT_SEARCH = "orange"  # For visualizing the current cell being explored

# Maze cell states
EMPTY = 0
OBSTACLE = 1

# Animation delay (milliseconds)
ANIMATION_DELAY = 1  # Lower for faster animation, higher for slower


def main():
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()


class MazeApp:
    def __init__(self, master):
        self.master = master
        master.title(f"Maze Solver ({GRID_SIZE}x{GRID_SIZE})")
        master.configure(bg=COLOR_BG)

        # --- Maze Data ---
        self.grid_data = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.start_node = (0, 0)
        self.end_node = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.current_path = []
        self.visited_for_drawing = set()

        # --- UI Elements ---
        control_frame = ttk.Frame(master, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(control_frame, text="Generate Obstacles", command=self.generate_obstacles).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Solve with DFS", command=lambda: self.solve_maze("DFS")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Solve with BFS", command=lambda: self.solve_maze("BFS")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Solution", command=self.clear_solution_visualization).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset Maze", command=self.reset_maze).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Obstacle Density (%):").pack(side=tk.LEFT, padx=(10,0))
        self.obstacle_density_var = tk.DoubleVar(value=25)
        density_scale = ttk.Scale(control_frame, from_=0, to_=100, orient=tk.HORIZONTAL,
                                  variable=self.obstacle_density_var, length=100)
        density_scale.pack(side=tk.LEFT, padx=5)
        self.density_display_label = ttk.Label(control_frame, text=f"{self.obstacle_density_var.get():.0f}")
        self.density_display_label.pack(side=tk.LEFT)
        self.obstacle_density_var.trace_add("write", self._update_density_display)

        self.status_label_var = tk.StringVar(value="Ready. Generate obstacles or load a maze.")
        status_label = ttk.Label(master, textvariable=self.status_label_var, padding="5", relief=tk.SUNKEN)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                bg=COLOR_EMPTY, highlightthickness=0)
        self.canvas.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        self.cell_rects = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.draw_grid()
        self.ensure_start_end_clear()
        self.draw_maze_elements()

    def _update_density_display(self, *args):
        self.density_display_label.config(text=f"{self.obstacle_density_var.get():.0f}")

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
                self.cell_rects[r][c] = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                                        fill=COLOR_EMPTY, outline="lightgray")
        self.canvas.update()

    def draw_cell(self, r, c, color, outline_color="lightgray"):
        rect_id = self.cell_rects[r][c]
        self.canvas.itemconfig(rect_id, fill=color, outline=outline_color)

    def draw_maze_elements(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = COLOR_OBSTACLE if self.grid_data[r][c] == OBSTACLE else COLOR_EMPTY
                self.draw_cell(r, c, color)
        self.draw_cell(*self.start_node, COLOR_START)
        self.draw_cell(*self.end_node, COLOR_END)
        self.canvas.update()

    def ensure_start_end_clear(self):
        self.grid_data[self.start_node[0]][self.start_node[1]] = EMPTY
        self.grid_data[self.end_node[0]][self.end_node[1]] = EMPTY

    def generate_obstacles(self):
        self.status_label_var.set("Generating obstacles...")
        self.master.update_idletasks()
        density = self.obstacle_density_var.get()/100.0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid_data[r][c] = OBSTACLE if random.random()<density else EMPTY
        self.ensure_start_end_clear()
        self.draw_maze_elements()
        self.status_label_var.set("Obstacles generated. Ready to solve.")

    def clear_solution_visualization(self):
        self.status_label_var.set("Clearing solution...")
        self.master.update_idletasks()
        for r,c in list(self.visited_for_drawing):
            if self.grid_data[r][c]==EMPTY and (r,c)!=self.start_node and (r,c)!=self.end_node:
                self.draw_cell(r,c,COLOR_EMPTY)
        self.visited_for_drawing.clear()
        self.current_path.clear()
        self.draw_cell(*self.start_node,COLOR_START)
        self.draw_cell(*self.end_node,COLOR_END)
        self.status_label_var.set("Solution cleared. Ready for new solve.")
        self.canvas.update()

    def reset_maze(self):
        self.status_label_var.set("Resetting maze...")
        self.master.update_idletasks()
        self.grid_data = [[EMPTY]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.visited_for_drawing.clear()
        self.current_path.clear()
        self.ensure_start_end_clear()
        self.draw_maze_elements()
        self.status_label_var.set("Maze reset. Generate obstacles to start.")
        self._set_controls_state(tk.NORMAL)

    def solve_maze(self, algorithm_name):
        self.clear_solution_visualization()
        self.status_label_var.set(f"Solving with {algorithm_name}...")
        self.master.update_idletasks()
        self._set_controls_state(tk.DISABLED)

        if algorithm_name == "DFS":
            found = self._solve_dfs_recursive_animated(self.start_node, set(), [])
            if not found:
                retry = messagebox.askretrycancel(
                    "No Solution",
                    "Tidak ada jalur dari START ke FINISH.\nCoba lagi?"
                )
                if retry:
                    self.reset_maze()
                else:
                    self._set_controls_state(tk.NORMAL)

        elif algorithm_name == "BFS":
            self._solve_bfs_animated()

    def _set_controls_state(self, state):
        for w in self.master.winfo_children():
            if isinstance(w, ttk.Frame):
                for btn in w.winfo_children():
                    if isinstance(btn, (ttk.Button, ttk.Scale)):
                        btn.configure(state=state)

    def _get_neighbors(self, r, c):
        for nr, nc in [(r, c+1), (r+1, c), (r, c-1), (r-1, c)]:
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and self.grid_data[nr][nc] == EMPTY:
                yield (nr, nc)

    def _solve_dfs_recursive_animated(self, node, visited, path):
        r, c = node
        if node in visited or self.grid_data[r][c] == OBSTACLE:
            return False
        visited.add(node)
        path.append(node)
        self.visited_for_drawing.add(node)

        if node not in (self.start_node, self.end_node):
            self.draw_cell(r, c, COLOR_VISITED)
            self.canvas.update()
            self.master.after(ANIMATION_DELAY)

        if node == self.end_node:
            self.current_path = list(path)
            self.draw_final_path()
            self.status_label_var.set("DFS: Path found!")
            self._set_controls_state(tk.NORMAL)
            return True

        for nbr in self._get_neighbors(r, c):
            if self._solve_dfs_recursive_animated(nbr, visited, path):
                return True

        path.pop()
        return False

    def _solve_bfs_animated(self):
        queue = collections.deque([(self.start_node, [self.start_node])])
        visited = {self.start_node}
        self.visited_for_drawing.add(self.start_node)

        def step():
            if not queue:
                retry = messagebox.askretrycancel(
                    "No Solution",
                    "Tidak ada jalur dari START ke FINISH.\nCoba lagi?"
                )
                if retry:
                    self.reset_maze()
                else:
                    self._set_controls_state(tk.NORMAL)
                return

            node, path = queue.popleft()
            r, c = node

            if node not in (self.start_node, self.end_node):
                self.draw_cell(r, c, COLOR_CURRENT_SEARCH)

            for nbr in self._get_neighbors(r, c):
                if nbr not in visited:
                    visited.add(nbr)
                    self.visited_for_drawing.add(nbr)
                    new_path = path + [nbr]

                    if nbr == self.end_node:
                        self.current_path = new_path
                        self.draw_final_path()
                        self.status_label_var.set("BFS: Path found!")
                        self._set_controls_state(tk.NORMAL)
                        return

                    queue.append((nbr, new_path))
                    self.draw_cell(nbr[0], nbr[1], COLOR_VISITED)

            self.canvas.update()
            self.master.after(ANIMATION_DELAY, step)

        step()

    def draw_final_path(self):
        for r, c in self.current_path:
            if (r, c) not in (self.start_node, self.end_node):
                self.draw_cell(r, c, COLOR_PATH)
        self.draw_cell(*self.start_node, COLOR_START)
        self.draw_cell(*self.end_node, COLOR_END)
        self.canvas.update()


if __name__ == "__main__":
    main()
