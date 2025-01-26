import random
import numpy as np

class PuzzleGenerator:
    def __init__(self, size=9):
        """Initialize the puzzle generator with a given grid size.
        
        Args:
            size (int): Size of the grid (4, 9, or 16)
        """
        if size not in [4, 9, 16]:
            raise ValueError("Grid size must be 4, 9, or 16")
        self.size = size
        self.box_size = int(size ** 0.5)  # 2 for 4x4, 3 for 9x9, 4 for 16x16
        self.symbols = self._get_symbols()

    def _get_symbols(self):
        """Get the symbols to use for the grid based on size."""
        if self.size == 4:
            return list(range(1, 5))
        elif self.size == 9:
            return list(range(1, 10))
        else:  # 16x16
            # Use 1-9 and A-G for 16x16 grid
            return list(range(1, 10)) + ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    def is_valid(self, board, row, col, num):
        """Check whether a number/symbol can be placed in a given cell."""
        # Check row and column
        for i in range(self.size):
            if board[row][i] == num or board[i][col] == num:
                return False
                
        # Check box
        box_row_start = row - row % self.box_size
        box_col_start = col - col % self.box_size
        for i in range(self.box_size):
            for j in range(self.box_size):
                if board[i + box_row_start][j + box_col_start] == num:
                    return False
        return True

    def fill_grid(self, grid):
        """Fill the grid using size-appropriate strategy."""
        if self.size <= 9:
            return self._fill_grid_small(grid)
        return self._fill_grid_large(grid)

    def _fill_grid_small(self, grid):
        """Original recursive backtracking for 4x4 and 9x9 grids."""
        empty = self._find_empty(grid)
        if not empty:
            return True
        
        row, col = empty
        for symbol in random.sample(self.symbols, len(self.symbols)):
            if self.is_valid(grid, row, col, symbol):
                grid[row][col] = symbol
                if self._fill_grid_small(grid):
                    return True
                grid[row][col] = 0
        return False

    def _fill_grid_large(self, grid):
        """Optimized filling for 16x16 grids using improved backtracking."""
        empty = self._find_empty(grid)
        if not empty:
            return True

        row, col = empty
        
        # Precompute used values for row, column and box
        used = set()
        
        # Row values
        used.update(grid[row])
        
        # Column values
        used.update(grid[i][col] for i in range(self.size))
        
        # Box values
        box_row = row - row % self.box_size
        box_col = col - col % self.box_size
        for i in range(self.box_size):
            for j in range(self.box_size):
                used.add(grid[box_row + i][box_col + j])
        
        # Get available values
        available = [s for s in self.symbols if s not in used]
        
        if not available:
            return False

        # Try available values in random order
        for symbol in random.sample(available, len(available)):
            grid[row][col] = symbol
            if self._fill_grid_large(grid):
                return True
            grid[row][col] = 0
        
        # If we get here, we need to backtrack
        return False

    def _find_empty(self, grid):
        """Find an empty cell with the fewest possible values."""
        min_options = float('inf')
        best_cell = None

        for i in range(self.size):
            for j in range(self.size):
                if grid[i][j] == 0:
                    options = sum(1 for s in self.symbols if self.is_valid(grid, i, j, s))
                    if options < min_options:
                        min_options = options
                        best_cell = (i, j)
                        if options == 1:  # Can't get better than 1
                            return best_cell
        return best_cell

    def count_solutions(self, grid, limit=2):
        """Count solutions up to limit. Returns early if more than one solution found."""
        count = [0]
        empty = self._find_empty(grid)
        if not empty:
            return 1
        
        row, col = empty
        for symbol in self.symbols:
            if count[0] >= limit:
                break
            if self.is_valid(grid, row, col, symbol):
                grid[row][col] = symbol
                if not self._find_empty(grid):
                    count[0] += 1
                else:
                    self.count_solutions(grid, limit)
                grid[row][col] = 0
        return count[0]

    def has_unique_solution(self, grid):
        """Check if the puzzle has exactly one solution."""
        return self.count_solutions(grid.copy(), limit=2) == 1

    def generate_sudoku(self, min_clues=None, max_attempts=5, timeout=120):
        """Generate a full Sudoku grid with retries and timeout."""
        import time
        start_time = time.time()

        if min_clues is None:
            min_clues = {
                4: 4,    # 4x4 minimum clues
                9: 17,   # 9x9 minimum clues (mathematically proven)
                16: 80   # 16x16 adjusted minimum for better performance
            }[self.size]

        # For 16x16, adjust clue counts to be more reasonable
        if self.size == 16:
            min_clues = max(min_clues, 80)  # Ensure at least 80 clues for 16x16

        dtype = object if self.size == 16 else int
        grid = np.zeros((self.size, self.size), dtype=dtype)

        for attempt in range(max_attempts):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Puzzle generation timed out after {timeout} seconds")

            grid = np.zeros((self.size, self.size), dtype=dtype)
            if self.fill_grid(grid):
                try:
                    puzzle = self.remove_numbers_exact_clues(grid.copy(), num_clues=min_clues)
                    return puzzle, grid
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise RuntimeError(f"Failed to generate valid puzzle after {max_attempts} attempts")
                    continue

        raise RuntimeError("Failed to generate valid grid")

    def remove_numbers_exact_clues(self, grid, num_clues):
        """Optimized number removal with batched uniqueness checks."""
        total_cells = self.size * self.size
        cells_to_remove = total_cells - num_clues
        removed = 0

        # For large grids, remove numbers in batches to reduce uniqueness checks
        if self.size > 9:
            # Adjust batch size based on grid size
            batch_size = 8 if self.size == 16 else 4
            all_cells = [(r, c) for r in range(self.size) for c in range(self.size)]
            random.shuffle(all_cells)
            
            while removed < cells_to_remove and all_cells:
                batch = []
                batch_cells = []
                
                # Try to remove a batch of numbers
                for _ in range(min(batch_size, cells_to_remove - removed)):
                    if not all_cells:
                        break
                    row, col = all_cells.pop()
                    if grid[row][col] != 0:
                        batch.append((row, col, grid[row][col]))
                        batch_cells.append((row, col))
                        grid[row][col] = 0

                # Check uniqueness after removing the batch
                if self.has_unique_solution(grid):
                    removed += len(batch)
                else:
                    # Restore the batch if solution is not unique
                    for row, col, value in batch:
                        grid[row][col] = value
                    
                    # If batch failed, try removing cells individually
                    for row, col, value in batch:
                        grid[row][col] = 0
                        if self.has_unique_solution(grid):
                            removed += 1
                        else:
                            grid[row][col] = value
        else:
            # Original logic for smaller grids
            all_cells = [(r, c) for r in range(self.size) for c in range(self.size)]
            random.shuffle(all_cells)

            for row, col in all_cells:
                if removed >= cells_to_remove:
                    break

                if grid[row][col] == 0:
                    continue

                backup = grid[row][col]
                grid[row][col] = 0

                if self.has_unique_solution(grid):
                    removed += 1
                else:
                    grid[row][col] = backup

        return grid
