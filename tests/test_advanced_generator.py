import pytest
import numpy as np
from advanced_sudoku_generator import AdvancedSudokuGenerator

class TestAdvancedSudokuGenerator:
    def test_generate_professional_sudoku_basic(self, advanced_generator_9x9):
        """Test basic professional Sudoku generation."""
        puzzle, solution = advanced_generator_9x9.generate_professional_sudoku(min_clues=30)
        
        # Verify puzzle dimensions
        assert puzzle.shape == (9, 9)
        assert solution.shape == (9, 9)
        
        # Count clues
        clue_count = np.count_nonzero(puzzle)
        assert clue_count >= 30
        
        # Verify solution is valid
        assert advanced_generator_9x9.has_unique_solution(puzzle)

    @pytest.mark.parametrize("difficulty,expected_min_clues", [
        ("easy", 40),
        ("medium", 35),
        ("hard", 30)
    ])
    def test_generate_professional_sudoku_difficulty(self, advanced_generator_9x9, difficulty, expected_min_clues):
        """Test professional Sudoku generation with different difficulty levels."""
        puzzle, _ = advanced_generator_9x9.generate_professional_sudoku(required_difficulty=difficulty)
        clue_count = np.count_nonzero(puzzle)
        
        # Verify clue count matches difficulty
        assert clue_count >= expected_min_clues

    def test_generate_professional_sudoku_with_symmetry(self, advanced_generator_9x9):
        """Test professional Sudoku generation with symmetry."""
        puzzle, _ = advanced_generator_9x9.generate_professional_sudoku(
            min_clues=30,
            symmetry=True
        )
        
        # Verify symmetry
        size = 9
        max_idx = size - 1
        for r in range(size):
            for c in range(size):
                # If a cell is filled, its symmetric counterpart should also be filled
                if puzzle[r][c] != 0:
                    assert puzzle[max_idx - r][max_idx - c] != 0

    def test_remove_numbers_with_symmetry(self, advanced_generator_9x9, valid_9x9_grid):
        """Test symmetric number removal."""
        result = advanced_generator_9x9.remove_numbers_with_symmetry(
            valid_9x9_grid.copy(),
            num_clues=30
        )
        
        # Verify clue count
        clue_count = np.count_nonzero(result)
        assert clue_count >= 30
        
        # Verify symmetry
        size = 9
        max_idx = size - 1
        for r in range(size):
            for c in range(size):
                # Check if value and its symmetric counterpart match in terms of being filled/empty
                is_filled = result[r][c] != 0
                symmetric_is_filled = result[max_idx - r][max_idx - c] != 0
                assert is_filled == symmetric_is_filled

    def test_enforce_exact_clue_count(self, advanced_generator_9x9, valid_9x9_grid):
        """Test enforcing exact clue count."""
        # Create a puzzle with more clues than target
        puzzle = valid_9x9_grid.copy()
        advanced_generator_9x9.solution = valid_9x9_grid.copy()
        
        # Test enforcing exact clue count
        exact_clues = 30
        result = advanced_generator_9x9.enforce_exact_clue_count(puzzle, exact_clues)
        
        # Verify exact clue count
        assert np.count_nonzero(result) == exact_clues

    def test_generate_professional_sudoku_timeout(self, advanced_generator_9x9):
        """Test timeout handling in professional generation."""
        with pytest.raises(TimeoutError):
            # Force timeout by requiring too many clues with tiny timeout
            advanced_generator_9x9.generate_professional_sudoku(min_clues=82, timeout=0.001)

    def test_generate_professional_sudoku_invalid_difficulty(self, advanced_generator_9x9):
        """Test handling of invalid difficulty level."""
        with pytest.raises(KeyError):
            advanced_generator_9x9.generate_professional_sudoku(required_difficulty="invalid")

    @pytest.mark.parametrize("size,difficulty,min_clues", [
        (4, "easy", 8),
        (4, "medium", 6),
        (4, "hard", 4),
        (9, "easy", 40),
        (9, "medium", 35),
        (9, "hard", 30),
        (16, "easy", 200),
        (16, "medium", 150),
        (16, "hard", 120)
    ])
    def test_professional_generation_all_sizes(self, size, difficulty, min_clues):
        """Test professional generation for all grid sizes and difficulties."""
        generator = AdvancedSudokuGenerator(size=size)
        puzzle, solution = generator.generate_professional_sudoku(
            required_difficulty=difficulty
        )
        
        # Verify dimensions
        assert puzzle.shape == (size, size)
        assert solution.shape == (size, size)
        
        # Verify clue count
        clue_count = np.count_nonzero(puzzle)
        assert clue_count >= min_clues

    def test_remove_numbers_unique_solution(self, advanced_generator_9x9, valid_9x9_grid):
        """Test that number removal maintains unique solutions."""
        result = advanced_generator_9x9.remove_numbers_exact_clues(
            valid_9x9_grid.copy(),
            num_clues=30
        )
        
        # Verify uniqueness
        assert advanced_generator_9x9.has_unique_solution(result)

    def test_enforce_exact_clue_count_restore(self, advanced_generator_9x9):
        """Test clue restoration when too many cells are empty."""
        # Create a puzzle with too few clues
        size = 9
        grid = np.zeros((size, size), dtype=int)
        solution = np.arange(1, 10).reshape(1, -1) * np.ones((9, 1))
        advanced_generator_9x9.solution = solution
        
        # Enforce more clues than present
        result = advanced_generator_9x9.enforce_exact_clue_count(grid, 30)
        
        # Verify clue count
        assert np.count_nonzero(result) == 30
