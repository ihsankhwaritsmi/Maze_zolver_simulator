import tkinter as tk
from tkinter import ttk, messagebox
import random
import collections

# --- Constants ---
GRID_SIZE = 50  # Size of the grid (100x100)
CELL_SIZE = 7  # Size of each cell in pixels
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


class MazeApp:
    def __init__(self, master):
        self.master = master
        master.title(f"Maze Solver ({GRID_SIZE}x{GRID_SIZE})")
        master.configure(bg=COLOR_BG)

        # --- Maze Data ---
        self.grid_data = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.start_node = (0, 0)  # Top-left corner
        self.end_node = (GRID_SIZE - 1, GRID_SIZE - 1)  # Bottom-right corner
        self.current_path = []
        self.visited_for_drawing = set()  # For drawing visited cells during search
        self.solving_in_progress = False  # Flag to prevent multiple solve calls

        # --- UI Elements ---
        # Control Frame
        control_frame = ttk.Frame(master, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_generate = ttk.Button(
            control_frame, text="Generate Obstacles", command=self.generate_obstacles
        )
        self.btn_generate.pack(side=tk.LEFT, padx=5)
        self.btn_dfs = ttk.Button(
            control_frame, text="Solve with DFS", command=lambda: self.solve_maze("DFS")
        )
        self.btn_dfs.pack(side=tk.LEFT, padx=5)
        self.btn_bfs = ttk.Button(
            control_frame, text="Solve with BFS", command=lambda: self.solve_maze("BFS")
        )
        self.btn_bfs.pack(side=tk.LEFT, padx=5)
        self.btn_clear = ttk.Button(
            control_frame,
            text="Clear Solution",
            command=self.clear_solution_visualization,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        self.btn_reset = ttk.Button(
            control_frame, text="Reset Maze", command=self.reset_maze
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        # Obstacle Density Control
        ttk.Label(control_frame, text="Obstacle Density (%):").pack(
            side=tk.LEFT, padx=(10, 0)
        )
        self.obstacle_density_var = tk.DoubleVar(value=25)  # Default 25%
        self.density_scale = ttk.Scale(
            control_frame,
            from_=0,
            to_=100,
            orient=tk.HORIZONTAL,
            variable=self.obstacle_density_var,
            length=100,
        )
        self.density_scale.pack(side=tk.LEFT, padx=5)
        # Using a label to display the scale value, making it dynamic
        self.density_display_label = ttk.Label(
            control_frame, text=f"{self.obstacle_density_var.get():.0f}"
        )
        self.density_display_label.pack(side=tk.LEFT)
        self.obstacle_density_var.trace_add("write", self._update_density_display)

        # Status Label
        self.status_label_var = tk.StringVar(
            value="Ready. Generate obstacles or load a maze."
        )
        status_label = ttk.Label(
            master, textvariable=self.status_label_var, padding="5", relief=tk.SUNKEN
        )
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas for Maze
        self.canvas = tk.Canvas(
            master,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=COLOR_EMPTY,
            highlightthickness=0,
        )
        self.canvas.pack(
            pady=10, padx=10, expand=True, fill=tk.BOTH
        )  # Allow canvas to expand

        # --- Initial Setup ---
        self.cell_rects = [
            [None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
        ]  # To store canvas item IDs
        self.draw_grid()
        self.ensure_start_end_clear()
        self.draw_maze_elements()

    def _update_density_display(self, *args):
        """Updates the label showing the current obstacle density."""
        self.density_display_label.config(text=f"{self.obstacle_density_var.get():.0f}")

    def draw_grid(self):
        """Draws the initial grid lines and cell rectangles."""
        self.canvas.delete("all")  # Clear previous drawings
        self.cell_rects = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                # Store rectangle ID for faster color updates
                self.cell_rects[r][c] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=COLOR_EMPTY, outline="lightgray", width=1
                )
        self.canvas.update()

    def draw_cell(self, r, c, color, outline_color="lightgray"):
        """Updates the color of a specific cell on the canvas."""
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            rect_id = self.cell_rects[r][c]
            if rect_id:
                self.canvas.itemconfig(rect_id, fill=color, outline=outline_color)
            # No fallback needed if grid is always pre-drawn with rects

    def draw_maze_elements(self):
        """Draws obstacles, start, and end points based on grid_data."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid_data[r][c] == OBSTACLE:
                    self.draw_cell(r, c, COLOR_OBSTACLE)
                else:
                    self.draw_cell(
                        r, c, COLOR_EMPTY
                    )  # Ensure non-obstacles are empty colored

        # Draw start and end points
        self.draw_cell(self.start_node[0], self.start_node[1], COLOR_START)
        self.draw_cell(self.end_node[0], self.end_node[1], COLOR_END)
        self.canvas.update()

    def ensure_start_end_clear(self):
        """Ensures that start and end nodes are not obstacles."""
        self.grid_data[self.start_node[0]][self.start_node[1]] = EMPTY
        self.grid_data[self.end_node[0]][self.end_node[1]] = EMPTY

    def generate_obstacles(self):
        """Generates random obstacles in the grid."""
        if self.solving_in_progress:
            messagebox.showwarning("Busy", "Solver is currently running. Please wait.")
            return

        self.status_label_var.set("Generating obstacles...")
        self.master.update_idletasks()  # Update GUI before potentially long operation

        self.grid_data = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_path = []
        self.visited_for_drawing.clear()

        density = self.obstacle_density_var.get() / 100.0

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if random.random() < density:
                    self.grid_data[r][c] = OBSTACLE
                else:
                    self.grid_data[r][c] = EMPTY

        self.ensure_start_end_clear()
        self.draw_maze_elements()  # Redraw all elements
        self.status_label_var.set("Obstacles generated. Ready to solve.")

    def clear_solution_visualization(self):
        """Clears only the path and visited cells visualization, keeping obstacles."""
        if self.solving_in_progress:
            messagebox.showwarning("Busy", "Solver is currently running. Please wait.")
            return

        self.status_label_var.set("Clearing solution...")
        self.master.update_idletasks()

        self.current_path = []
        # Redraw visited cells as empty (if they are not obstacles)
        for r_vis, c_vis in list(self.visited_for_drawing):  # Iterate over a copy
            if (
                self.grid_data[r_vis][c_vis] == EMPTY
                and (r_vis, c_vis) != self.start_node
                and (r_vis, c_vis) != self.end_node
            ):
                self.draw_cell(r_vis, c_vis, COLOR_EMPTY)
        self.visited_for_drawing.clear()

        # Redraw start and end to ensure they are visible and correctly colored
        self.draw_cell(self.start_node[0], self.start_node[1], COLOR_START)
        self.draw_cell(self.end_node[0], self.end_node[1], COLOR_END)

        self.status_label_var.set("Solution cleared. Ready for new solve.")
        self.canvas.update()

    def reset_maze(self):
        """Resets the entire maze to an empty grid."""
        if self.solving_in_progress:  # If a solve is happening, stop it.
            self.solving_in_progress = False  # This will stop BFS's "after" loop
            # For DFS, it's harder to interrupt cleanly mid-recursion without more complex threading.
            # But disabling controls and this flag should prevent new actions.
            self._set_controls_state(
                tk.NORMAL
            )  # Re-enable controls if they were disabled

        self.status_label_var.set("Resetting maze...")
        self.master.update_idletasks()

        self.grid_data = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_path = []
        self.visited_for_drawing.clear()
        self.ensure_start_end_clear()  # Ensures start/end are clear on the new empty grid
        self.draw_maze_elements()  # Draws start/end and empty cells
        self.status_label_var.set("Maze reset. Generate obstacles to start.")

    def solve_maze(self, algorithm_name):
        """Initiates the maze solving process using the selected algorithm."""
        if self.solving_in_progress:
            messagebox.showwarning(
                "Busy", "Another solving process is already running."
            )
            return

        self.clear_solution_visualization()  # Clear previous solution first
        self.status_label_var.set(f"Solving with {algorithm_name}...")
        self.master.update_idletasks()

        if (
            self.grid_data[self.start_node[0]][self.start_node[1]] == OBSTACLE
            or self.grid_data[self.end_node[0]][self.end_node[1]] == OBSTACLE
        ):
            messagebox.showerror(
                "Error", "Start or End node is an obstacle! Please reset or regenerate."
            )
            self.status_label_var.set("Error: Start/End is obstacle.")
            return

        self._set_controls_state(tk.DISABLED)
        self.solving_in_progress = True

        if algorithm_name == "DFS":
            visited_dfs = set()
            path_dfs = []
            # Run DFS in a way that doesn't block the UI entirely for too long if ANIMATION_DELAY > 0
            # For very small ANIMATION_DELAY, this is less of an issue.
            # A more robust solution for long DFS would be threading.
            path_found_dfs = self._solve_dfs_recursive_animated(
                self.start_node, visited_dfs, path_dfs
            )
            if not path_found_dfs:  # This check happens after DFS completes
                self.status_label_var.set("DFS: No path found.")
                self._set_controls_state(tk.NORMAL)
                self.solving_in_progress = False
                messagebox.showinfo(
                    "No Solution",
                    "DFS could not find a path. Try generating new obstacles or reducing density.",
                )
            # If path was found, status, controls, and solving_in_progress flag are handled in _solve_dfs_recursive_animated

        elif algorithm_name == "BFS":
            # BFS is naturally asynchronous due to using root.after() calls for its steps.
            # Its completion (success or fail) will handle re-enabling controls and showing messages.
            self._solve_bfs_animated()

        # Note: If DFS returns False (no path), controls are re-enabled above.
        # If DFS returns True (path found), controls are re-enabled within _solve_dfs_recursive_animated.
        # For BFS, _solve_bfs_animated handles re-enabling controls in its termination conditions (path found or queue empty).

    def _set_controls_state(self, state):
        """Enable or disable control buttons."""
        self.btn_generate.config(state=state)
        self.btn_dfs.config(state=state)
        self.btn_bfs.config(state=state)
        self.btn_clear.config(state=state)
        self.btn_reset.config(state=state)
        self.density_scale.config(state=state)

    def _get_neighbors(self, r, c):
        """Returns valid, non-obstacle neighbors of a cell."""
        neighbors = []
        # Order: Right, Down, Left, Up. This order can influence DFS path.
        potential_neighbors = [(r, c + 1), (r + 1, c), (r, c - 1), (r - 1, c)]
        for nr, nc in potential_neighbors:
            if (
                0 <= nr < GRID_SIZE
                and 0 <= nc < GRID_SIZE
                and self.grid_data[nr][nc] == EMPTY
            ):
                neighbors.append((nr, nc))
        return neighbors

    # --- DFS Implementation (Recursive with Animation) ---
    def _solve_dfs_recursive_animated(self, current_node, visited, path_accumulator):
        # If solving_in_progress was set to False externally (e.g., by Reset button), stop.
        if not self.solving_in_progress:
            return False  # Indicate that the search was aborted

        r, c = current_node

        # Base cases for recursion termination
        if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):  # Out of bounds
            return False
        if self.grid_data[r][c] == OBSTACLE:  # Hit an obstacle
            return False
        if (
            current_node in visited
        ):  # Already visited in this specific DFS exploration path
            return False

        visited.add(current_node)
        path_accumulator.append(current_node)
        self.visited_for_drawing.add(
            current_node
        )  # Add to set for clearing visualization

        # Animate the current cell being explored
        if current_node != self.start_node and current_node != self.end_node:
            self.draw_cell(r, c, COLOR_VISITED)
            self.canvas.update()  # Update canvas to show change
            # self.master.update_idletasks() # Process pending events
            if ANIMATION_DELAY > 0:  # Only delay if ANIMATION_DELAY is set
                self.master.after(
                    ANIMATION_DELAY
                )  # Use master.after for non-blocking delay

        if current_node == self.end_node:
            self.current_path = list(path_accumulator)  # Found the path
            self.draw_final_path()
            self.status_label_var.set("DFS: Path found!")
            self._set_controls_state(tk.NORMAL)  # Re-enable controls
            self.solving_in_progress = False  # Mark solving as complete
            return True  # Path found

        # Recursive step: Explore neighbors
        for neighbor_r, neighbor_c in self._get_neighbors(r, c):
            if not self.solving_in_progress:  # Check again before recursive call
                return False
            if self._solve_dfs_recursive_animated(
                (neighbor_r, neighbor_c), visited, path_accumulator
            ):
                return True  # Propagate success upwards

        # Backtrack: If no neighbor led to a solution, remove current_node from path
        path_accumulator.pop()
        # No specific visualization for backtracking in this version to keep it cleaner.

        return False

    # --- BFS Implementation (Iterative with Animation) ---
    def _solve_bfs_animated(self):
        queue = collections.deque(
            [(self.start_node, [self.start_node])]
        )  # (node, current_path_to_node)
        visited_bfs = {self.start_node}  # Keep track of visited nodes for BFS
        self.visited_for_drawing.add(
            self.start_node
        )  # For overall visualization clearing

        # Inner function for step-by-step animation using root.after()
        def bfs_step():
            if (
                not self.solving_in_progress
            ):  # If solving was cancelled externally (e.g. reset)
                self._set_controls_state(tk.NORMAL)  # Ensure controls are re-enabled
                return

            if not queue:  # Queue is empty, no path found
                self.status_label_var.set("BFS: No path found.")
                self._set_controls_state(tk.NORMAL)  # Re-enable controls
                self.solving_in_progress = False  # Mark solving as complete
                self.canvas.update()
                messagebox.showinfo(
                    "No Solution",
                    "BFS could not find a path. Try generating new obstacles or reducing density.",
                )
                return

            current_node, path_to_current = queue.popleft()
            r, c = current_node

            # Animate the current cell being processed (unless it's start/end)
            if current_node != self.start_node and current_node != self.end_node:
                self.draw_cell(
                    r, c, COLOR_VISITED
                )  # Mark as processed (part of search area)

            # Explore neighbors
            for neighbor_r, neighbor_c in self._get_neighbors(r, c):
                neighbor = (neighbor_r, neighbor_c)
                if neighbor not in visited_bfs:
                    visited_bfs.add(neighbor)
                    self.visited_for_drawing.add(neighbor)  # For clearing visualization

                    new_path = list(path_to_current)
                    new_path.append(neighbor)

                    if neighbor == self.end_node:  # Path found
                        self.current_path = new_path
                        self.draw_final_path()
                        self.status_label_var.set("BFS: Path found!")
                        self._set_controls_state(tk.NORMAL)  # Re-enable controls
                        self.solving_in_progress = False  # Mark solving as complete
                        self.canvas.update()
                        return  # BFS complete

                    queue.append((neighbor, new_path))
                    # Color cells being added to the queue (frontier)
                    if neighbor != self.end_node:  # Don't overdraw end node
                        self.draw_cell(neighbor_r, neighbor_c, COLOR_CURRENT_SEARCH)

            self.canvas.update()
            if self.solving_in_progress:  # Continue only if still solving
                if ANIMATION_DELAY > 0:
                    self.master.after(
                        ANIMATION_DELAY, bfs_step
                    )  # Schedule the next step of BFS
                else:  # If no delay, call directly but yield control to event loop periodically
                    self.master.after(0, bfs_step)

        # Start the BFS animation loop
        if ANIMATION_DELAY > 0:
            self.master.after(ANIMATION_DELAY, bfs_step)
        else:  # If no delay, start immediately but allow event loop to process
            self.master.after(0, bfs_step)

    def draw_final_path(self):
        """Draws the found path on the canvas."""
        if not self.current_path:
            return

        for r_path, c_path in self.current_path:
            if (r_path, c_path) != self.start_node and (
                r_path,
                c_path,
            ) != self.end_node:
                self.draw_cell(r_path, c_path, COLOR_PATH)

        # Ensure start and end are on top and correctly colored after path drawing
        self.draw_cell(self.start_node[0], self.start_node[1], COLOR_START)
        self.draw_cell(self.end_node[0], self.end_node[1], COLOR_END)
        self.canvas.update()


def main():
    root = tk.Tk()
    app = MazeApp(root)

    # Handle window close event to stop any ongoing animation
    def on_closing():
        if app.solving_in_progress:
            app.solving_in_progress = False  # Attempt to stop any background solving
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
