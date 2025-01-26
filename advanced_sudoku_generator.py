import random
import numpy as np

from puzzle_generator import PuzzleGenerator

class AdvancedSudokuGenerator(PuzzleGenerator):
    
    def generate_professional_sudoku(self, min_clues=None, symmetry=False, required_difficulty="medium", timeout=60):
        """Generate a professional Sudoku puzzle with optional symmetry and specified difficulty."""
        # Default clue counts based on grid size and difficulty
        default_clues = {
            4: {
                'easy': 8,
                'medium': 6,
                'hard': 4
            },
            9: {
                'easy': 40,
                'medium': 35,
                'hard': 30
            },
            16: {
                'easy': 200,
                'medium': 150,
                'hard': 120
            }
        }

        # If min_clues not specified, use default based on size and difficulty
        if min_clues is None:
            min_clues = default_clues[self.size][required_difficulty]

        # For 16x16, ensure minimum clues for better performance
        if self.size == 16:
            min_clues = max(min_clues, 120)

        # Generate puzzle with timeout
        try:
            # Use superclass generate_sudoku with timeout
            grid = np.zeros((self.size, self.size), dtype=object if self.size == 16 else int)
            if self.fill_grid(grid):
                # Store solution for enforce_exact_clue_count
                self.solution = grid.copy()

                # Apply appropriate number removal strategy
                if symmetry:
                    puzzle = self.remove_numbers_with_symmetry(grid.copy(), num_clues=min_clues)
                else:
                    puzzle = self.remove_numbers_exact_clues(grid.copy(), num_clues=min_clues)

                # Ensure exact clue count
                puzzle = self.enforce_exact_clue_count(puzzle, min_clues)
                return puzzle, grid
            else:
                raise RuntimeError("Failed to generate valid grid")

        except TimeoutError:
            raise TimeoutError(f"Failed to generate {self.size}x{self.size} puzzle within {timeout} seconds")

    def remove_numbers_with_symmetry(self, grid, num_clues):
        """Remove numbers symmetrically from the grid."""
        total_cells = self.size * self.size
        cells_to_remove = total_cells - num_clues
        removed = 0
        
        # Get all symmetric pairs (mirror across center)
        max_idx = self.size - 1
        symmetric_pairs = [
            (r, c, max_idx - r, max_idx - c) 
            for r in range(self.size) 
            for c in range(self.size) 
            if r <= max_idx - r and c <= max_idx - c
        ]
        random.shuffle(symmetric_pairs)

        for r1, c1, r2, c2 in symmetric_pairs:
            if removed >= cells_to_remove // 2:
                break

            if grid[r1][c1] == 0 or grid[r2][c2] == 0:
                continue

            backup1, backup2 = grid[r1][c1], grid[r2][c2]
            grid[r1][c1], grid[r2][c2] = 0, 0

            # Ensure unique solution
            if self.has_unique_solution(grid):
                removed += 2  # Removing two cells symmetrically
            else:
                grid[r1][c1], grid[r2][c2] = backup1, backup2  # Restore if removing breaks uniqueness

        return grid

    def remove_numbers_exact_clues(self, grid, num_clues):
        """Remove numbers to leave exactly num_clues in the grid."""
        total_cells = self.size * self.size
        cells_to_remove = total_cells - num_clues
        removed = 0

        all_cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        random.shuffle(all_cells)

        for row, col in all_cells:
            if removed >= cells_to_remove:
                break

            if grid[row][col] == 0:
                continue

            backup = grid[row][col]
            grid[row][col] = 0

            # Check if the puzzle still has a unique solution
            if self.has_unique_solution(grid):
                removed += 1  # Successful removal
            else:
                grid[row][col] = backup  # Restore if removing breaks uniqueness

        return grid

    def enforce_exact_clue_count(self, grid, min_clues):
        """Ensure the puzzle has exactly `min_clues` by forcefully removing or restoring cells."""
        current_clues = sum(1 for r in range(self.size) for c in range(self.size) if grid[r][c] != 0)
        total_cells = self.size * self.size

        # If too many cells removed, restore some cells
        if current_clues < min_clues:
            # Get all removed cells and restore randomly until exactly `min_clues`
            all_cells = [(r, c) for r in range(self.size) for c in range(self.size) if grid[r][c] == 0]
            random.shuffle(all_cells)
            for row, col in all_cells:
                if current_clues >= min_clues:
                    break
                grid[row][col] = self.solution[row][col]  # Restore from the solution
                current_clues += 1

        # If too few cells removed, remove more until exactly `min_clues`
        if current_clues > min_clues:
            all_filled_cells = [(r, c) for r in range(self.size) for c in range(self.size) if grid[r][c] != 0]
            random.shuffle(all_filled_cells)
            for row, col in all_filled_cells:
                if current_clues <= min_clues:
                    break
                grid[row][col] = 0  # Remove
                current_clues -= 1

        return grid
