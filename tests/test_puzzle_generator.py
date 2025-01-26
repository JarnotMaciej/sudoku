import pytest
import numpy as np
from puzzle_generator import PuzzleGenerator


class TestPuzzleGenerator:
    def test_initialization_valid_sizes(self):
        """Test initializing PuzzleGenerator with valid grid sizes."""
        for size in [4, 9, 16]:
            generator = PuzzleGenerator(size=size)
            assert generator.size == size
            assert generator.box_size == int(size ** 0.5)

    def test_initialization_invalid_size(self):
        """Test that invalid grid sizes raise ValueError."""
        with pytest.raises(ValueError, match="Grid size must be 4, 9, or 16"):
            PuzzleGenerator(size=6)

    def test_get_symbols(self):
        """Test symbol generation for different grid sizes."""
        # 4x4 grid should have symbols 1-4
        gen_4x4 = PuzzleGenerator(size=4)
        assert gen_4x4.symbols == list(range(1, 5))

        # 9x9 grid should have symbols 1-9
        gen_9x9 = PuzzleGenerator(size=9)
        assert gen_9x9.symbols == list(range(1, 10))

        # 16x16 grid should have symbols 1-9 and A-G
        gen_16x16 = PuzzleGenerator(size=16)
        expected_symbols = list(range(1, 10)) + ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        assert gen_16x16.symbols == expected_symbols

    def test_is_valid_empty_grid(self, puzzle_generator_9x9):
        """Test number validation in empty grid."""
        grid = np.zeros((9, 9), dtype=int)
        # Any number should be valid in empty grid
        for num in range(1, 10):
            assert puzzle_generator_9x9.is_valid(grid, 0, 0, num)

    def test_is_valid_row_conflict(self, puzzle_generator_9x9):
        """Test number validation with row conflicts."""
        grid = np.zeros((9, 9), dtype=int)
        grid[0, 0] = 5
        # 5 should be invalid anywhere else in row 0
        for col in range(1, 9):
            assert not puzzle_generator_9x9.is_valid(grid, 0, col, 5)

    def test_is_valid_column_conflict(self, puzzle_generator_9x9):
        """Test number validation with column conflicts."""
        grid = np.zeros((9, 9), dtype=int)
        grid[0, 0] = 5
        # 5 should be invalid anywhere else in column 0
        for row in range(1, 9):
            assert not puzzle_generator_9x9.is_valid(grid, row, 0, 5)

    def test_is_valid_box_conflict(self, puzzle_generator_9x9):
        """Test number validation with box conflicts."""
        grid = np.zeros((9, 9), dtype=int)
        grid[0, 0] = 5
        # 5 should be invalid anywhere else in the top-left 3x3 box
        for row in range(3):
            for col in range(3):
                if row == 0 and col == 0:
                    continue
                assert not puzzle_generator_9x9.is_valid(grid, row, col, 5)

    def test_find_empty_simplest_case(self, puzzle_generator_9x9):
        """Test finding empty cell in a grid with one obvious choice."""
        grid = np.array([
            [1, 2, 3, 4, 5, 6, 7, 8, 0],  # Only one empty cell
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ])
        empty = puzzle_generator_9x9._find_empty(grid)
        assert empty == (0, 8)

    def test_count_solutions_unique(self, puzzle_generator_9x9, partially_filled_9x9_grid):
        """Test solution counting for grid with unique solution."""
        count = puzzle_generator_9x9.count_solutions(partially_filled_9x9_grid)
        assert count == 1

    def test_has_unique_solution(self, puzzle_generator_9x9, partially_filled_9x9_grid):
        """Test unique solution verification."""
        assert puzzle_generator_9x9.has_unique_solution(partially_filled_9x9_grid)

    def test_generate_sudoku_basic(self, puzzle_generator_9x9):
        """Test basic Sudoku generation with minimum requirements."""
        puzzle, solution = puzzle_generator_9x9.generate_sudoku(min_clues=30)
        
        # Verify puzzle dimensions
        assert puzzle.shape == (9, 9)
        assert solution.shape == (9, 9)
        
        # Count clues in puzzle
        clue_count = np.count_nonzero(puzzle)
        assert clue_count >= 30
        
        # Verify solution validity
        for i in range(9):
            # Check rows and columns
            assert set(solution[i, :]) == set(range(1, 10))
            assert set(solution[:, i]) == set(range(1, 10))
            
            # Check 3x3 boxes
            box_row = (i // 3) * 3
            box_col = (i % 3) * 3
            box = solution[box_row:box_row + 3, box_col:box_col + 3]
            assert set(box.flatten()) == set(range(1, 10))

    def test_fill_grid_small(self, puzzle_generator_4x4):
        """Test grid filling for 4x4 puzzle."""
        grid = np.zeros((4, 4), dtype=int)
        assert puzzle_generator_4x4._fill_grid_small(grid)
        
        # Verify all numbers are valid
        for row in range(4):
            assert set(grid[row, :]) == set(range(1, 5))
            assert set(grid[:, row]) == set(range(1, 5))

    def test_fill_grid_large(self, puzzle_generator_16x16):
        """Test grid filling for 16x16 puzzle."""
        grid = np.zeros((16, 16), dtype=object)
        assert puzzle_generator_16x16._fill_grid_large(grid)
        
        # Convert symbols to set for comparison
        valid_symbols = set(puzzle_generator_16x16.symbols)
        
        # Verify all rows and columns contain valid symbols
        for i in range(16):
            assert set(grid[i, :]) == valid_symbols
            assert set(grid[:, i]) == valid_symbols

    def test_remove_numbers_exact_clues(self, puzzle_generator_9x9, valid_9x9_grid):
        """Test number removal while maintaining uniqueness."""
        grid_copy = valid_9x9_grid.copy()
        result = puzzle_generator_9x9.remove_numbers_exact_clues(grid_copy, num_clues=30)
        
        # Verify clue count
        assert np.count_nonzero(result) >= 30
        
        # Verify uniqueness
        assert puzzle_generator_9x9.has_unique_solution(result)

    def test_generate_sudoku_timeout(self, puzzle_generator_9x9):
        """Test that generation times out appropriately."""
        # Force an immediate timeout by using 0 timeout
        with pytest.raises(TimeoutError):
            puzzle_generator_9x9.generate_sudoku(min_clues=81, max_attempts=1, timeout=0)
