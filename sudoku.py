#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sudoku Puzzle Generator with multiprocessing support to use all cores
Author: [Ali Alp]
Date: September 2024
Description: Generates Sudoku puzzles of varying difficulty (easy, medium, hard),
with optional minimum clues for each difficulty level, and optionally generates an answers PDF with the solution.
Supports parallel processing to utilize all CPU cores for generating puzzles concurrently.
"""

from multiprocessing import Pool, cpu_count
from advanced_sudoku_generator import AdvancedSudokuGenerator
from pdf_generator import PDFGenerator
from argument_parser import ArgumentParser

# Helper function for multiprocessing
def generate_puzzle_task(task):
    min_clues, difficulty, use_symmetry, grid_size = task
    generator = AdvancedSudokuGenerator(size=grid_size)
    return generator.generate_professional_sudoku(min_clues=min_clues, symmetry=use_symmetry, required_difficulty=difficulty)

def get_min_clues_threshold(grid_size):
    """Get the minimum required clues based on grid size."""
    return {
        4: 4,    # 4x4 minimum clues
        9: 17,   # 9x9 minimum clues (mathematically proven)
        16: 40   # 16x16 reasonable minimum
    }[grid_size]

# Main Function
def main():
    # Use the ArgumentParser class to parse arguments
    args_parser = ArgumentParser()
    args = args_parser.parse()

    pdf_generator = PDFGenerator(grid_size=args.size)

    # Get minimum clues threshold for validation
    min_clues_threshold = get_min_clues_threshold(args.size)

    # Parse puzzle configurations
    puzzle_config = {'easy': [], 'medium': [], 'hard': []}

    # Handle the config to extract difficulty, count, and optional min_clues
    for config in args.config:
        parts = config.split(':')
        difficulty = parts[0]
        count = int(parts[1])
        min_clues = int(parts[2]) if len(parts) == 3 else get_default_min_clues(difficulty, args.size)

        # Validate minimum clues based on grid size
        if min_clues < min_clues_threshold:
            raise ValueError(
                f"Error: For {args.size}x{args.size} grid, minimum clues must be at least {min_clues_threshold}. "
                f"You provided {min_clues} for {difficulty}."
            )

        puzzle_config[difficulty].append({'count': count, 'min_clues': min_clues})

    # Prepare tasks for multiprocessing
    tasks = []
    for difficulty in ['easy', 'medium', 'hard']:
        for config in puzzle_config[difficulty]:
            for _ in range(config['count']):
                tasks.append((config['min_clues'], difficulty, args.use_symmetry, args.size))

    # Use multiprocessing to generate puzzles in parallel
    num_cores = cpu_count()  # Get the number of CPU cores available
    print(f"Generating puzzles using {num_cores} CPU cores...")

    # Check multiprocessing setup
    print(f"Number of tasks to process: {len(tasks)}")
    with Pool(processes=num_cores) as pool:
        puzzles_generated_flat = pool.map(generate_puzzle_task, tasks)

    # Restructure the puzzles back into their difficulty groups
    puzzles_generated = {'easy': [], 'medium': [], 'hard': []}
    index = 0
    for difficulty in ['easy', 'medium', 'hard']:
        for config in puzzle_config[difficulty]:
            puzzles_generated[difficulty].extend(puzzles_generated_flat[index:index + config['count']])
            index += config['count']

    # Generate and save puzzle PDFs
    for difficulty in ['easy', 'medium', 'hard']:
        if len(puzzles_generated[difficulty]) > 0:
            pdf_generator.generate_puzzles_pdf(puzzles_generated[difficulty], difficulty)

    pdf_generator.save_pdf(args.output)

    # Generate answers PDF if requested
    if args.gen_answers:
        answers_pdf_generator = PDFGenerator(grid_size=args.size)
        for difficulty in ['easy', 'medium', 'hard']:
            if len(puzzles_generated[difficulty]) > 0:
                answers_pdf_generator.generate_puzzles_pdf(puzzles_generated[difficulty], difficulty, is_answer=True)
        answers_pdf_generator.save_pdf(args.output.replace('.pdf', '_answers.pdf'))

# --- Default Min Clues Based on Difficulty ---
def get_default_min_clues(difficulty, grid_size):
    """Get the default minimum clues for a given difficulty based on grid size."""
    # Default clue counts for different grid sizes and difficulties
    clue_counts = {
        4: {  # 4x4 grid
            'easy': 8,
            'medium': 6,
            'hard': 4
        },
        9: {  # 9x9 grid (traditional)
            'easy': 40,
            'medium': 35,
            'hard': 30
        },
        16: {  # 16x16 grid
            'easy': 170,
            'medium': 140,
            'hard': 40  # Minimum required for uniqueness
        }
    }

    if difficulty not in ['easy', 'medium', 'hard']:
        raise ValueError(f"Unknown difficulty level: {difficulty}")

    return clue_counts[grid_size][difficulty]


if __name__ == "__main__":
    main()  # Ensure main() is executed directly to avoid multiprocessing issues
