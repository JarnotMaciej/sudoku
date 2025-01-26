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

        import time
        start_time = time.time()
        max_attempts = 5
        attempt = 0
        
        grid = np.zeros((self.size, self.size), dtype=object if self.size == 16 else int)
        while attempt < max_attempts:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Failed to generate {self.size}x{self.size} puzzle within {timeout} seconds")

            attempt += 1
            grid = np.zeros((self.size, self.size), dtype=object if self.size == 16 else int)
            
            if self.fill_grid(grid):
                try:
                    # Store solution for enforce_exact_clue_count
                    self.solution = grid.copy()

                    # Apply appropriate number removal strategy
                    if symmetry:
                        puzzle = self.remove_numbers_with_symmetry(grid.copy(), num_clues=min_clues)
                    else:
                        puzzle = self.remove_numbers_exact_clues(grid.copy(), num_clues=min_clues)

                    # Ensure exact clue count while maintaining symmetry
                    puzzle = self.enforce_exact_clue_count(puzzle, min_clues, symmetry)
                    
                    # Check if the puzzle is valid
                    if min_clues <= self.size * self.size:
                        return puzzle, grid
                except Exception:
                    continue

        raise RuntimeError(f"Failed to generate valid puzzle after {max_attempts} attempts")

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

    def enforce_exact_clue_count(self, grid, min_clues, symmetry=False):
        """Ensure the puzzle has exactly `min_clues` by forcefully removing or restoring cells."""
        current_clues = sum(1 for r in range(self.size) for c in range(self.size) if grid[r][c] != 0)
        total_cells = self.size * self.size

        max_idx = self.size - 1

        if symmetry:
            # Handle symmetric restoration/removal
            if current_clues < min_clues:
                # Get all symmetric pairs of empty cells
                empty_pairs = [
                    (r1, c1, r2, c2) for r1 in range(self.size) for c1 in range(self.size)
                    for r2, c2 in [(max_idx - r1, max_idx - c1)]
                    if grid[r1][c1] == 0 and grid[r2][c2] == 0 and (r1 < r2 or (r1 == r2 and c1 <= c2))
                ]
                random.shuffle(empty_pairs)
                
                for r1, c1, r2, c2 in empty_pairs:
                    if current_clues >= min_clues:
                        break
                    if r1 == r2 and c1 == c2:  # Center cell
                        grid[r1][c1] = self.solution[r1][c1]
                        current_clues += 1
                    else:
                        grid[r1][c1] = self.solution[r1][c1]
                        grid[r2][c2] = self.solution[r2][c2]
                        current_clues += 2

            if current_clues > min_clues:
                # Get all symmetric pairs of filled cells
                filled_pairs = [
                    (r1, c1, r2, c2) for r1 in range(self.size) for c1 in range(self.size)
                    for r2, c2 in [(max_idx - r1, max_idx - c1)]
                    if grid[r1][c1] != 0 and grid[r2][c2] != 0 and (r1 < r2 or (r1 == r2 and c1 <= c2))
                ]
                random.shuffle(filled_pairs)
                
                for r1, c1, r2, c2 in filled_pairs:
                    if current_clues <= min_clues:
                        break
                    if r1 == r2 and c1 == c2:  # Center cell
                        if current_clues - 1 >= min_clues:
                            grid[r1][c1] = 0
                            current_clues -= 1
                    else:
                        grid[r1][c1] = grid[r2][c2] = 0
                        current_clues -= 2
        else:
            # Original non-symmetric logic
            if current_clues < min_clues:
                all_cells = [(r, c) for r in range(self.size) for c in range(self.size) if grid[r][c] == 0]
                random.shuffle(all_cells)
                for row, col in all_cells:
                    if current_clues >= min_clues:
                        break
                    grid[row][col] = self.solution[row][col]
                    current_clues += 1

            if current_clues > min_clues:
                all_filled_cells = [(r, c) for r in range(self.size) for c in range(self.size) if grid[r][c] != 0]
                random.shuffle(all_filled_cells)
                for row, col in all_filled_cells:
                    if current_clues <= min_clues:
                        break
                    grid[row][col] = 0
                    current_clues -= 1

        return grid
