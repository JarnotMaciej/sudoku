from fpdf import FPDF

class PDFGenerator:
    def __init__(self, grid_size=9):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.grid_size = grid_size
        self.box_size = int(grid_size ** 0.5)  # 2 for 4x4, 3 for 9x9, 4 for 16x16
        # Adjust cell size based on grid size
        self.cell_size = {
            4: 15,   # Larger cells for 4x4
            9: 10,   # Standard size for 9x9
            16: 7    # Smaller cells for 16x16
        }[grid_size]

    def add_title_page(self, difficulty):
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 100, f'{difficulty.capitalize()} Sudoku Puzzles', ln=True, align='C')

    def format_cell_value(self, value):
        """Format cell value, converting to hexadecimal for 16x16 grids if needed."""
        if value == 0:
            return ""
        if self.grid_size == 16 and isinstance(value, str):
            return value  # Already a letter A-G
        if self.grid_size == 16 and value > 9:
            return chr(ord('A') + value - 10)  # Convert 10-16 to A-G
        return str(value)

    def add_sudoku_to_pdf(self, sudoku, puzzle_num, difficulty, offset_y, title_suffix="Sudoku Puzzle"):
        # Adjust font size based on grid size
        title_font_size = 16 if self.grid_size <= 9 else 14
        cell_font_size = 12 if self.grid_size <= 9 else 8

        self.pdf.set_font('Arial', 'B', title_font_size)
        self.pdf.set_xy(0, offset_y - 15)
        self.pdf.cell(210, 10, f'{difficulty.capitalize()} {title_suffix} #{puzzle_num}', ln=True, align='C')

        # Center the puzzle grid horizontally
        grid_width = self.grid_size * self.cell_size
        offset_x = (210 - grid_width) / 2  # A4 page width is 210mm

        # Add cells
        self.pdf.set_font('Arial', '', cell_font_size)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.pdf.set_xy(offset_x + j * self.cell_size, offset_y + i * self.cell_size)
                value = self.format_cell_value(sudoku[i, j])
                self.pdf.set_line_width(0.3)
                self.pdf.cell(self.cell_size, self.cell_size, value, border=1, align='C')

        # Add bold grid lines
        self.pdf.set_line_width(1.5)
        for i in range(0, self.grid_size + 1, self.box_size):
            # Vertical lines
            self.pdf.line(
                offset_x + i * self.cell_size,
                offset_y,
                offset_x + i * self.cell_size,
                offset_y + self.grid_size * self.cell_size
            )
            # Horizontal lines
            self.pdf.line(
                offset_x,
                offset_y + i * self.cell_size,
                offset_x + self.grid_size * self.cell_size,
                offset_y + i * self.cell_size
            )

    def generate_puzzles_pdf(self, puzzles, difficulty):
        self.add_title_page(difficulty)
        total_puzzles = len(puzzles)
        
        # Determine puzzles per page based on grid size
        puzzles_per_page = 1 if self.grid_size == 16 else 2
        offset_y = 40

        for i in range(0, total_puzzles, puzzles_per_page):
            # Add puzzle page
            self.pdf.add_page()
            # First puzzle
            self.add_sudoku_to_pdf(
                puzzles[i][0],
                i + 1,
                difficulty,
                offset_y=offset_y,
                title_suffix="Sudoku Puzzle"
            )
            
            # Second puzzle if using 2 per page and if it exists
            if puzzles_per_page == 2 and i + 1 < total_puzzles:
                self.add_sudoku_to_pdf(
                    puzzles[i + 1][0],
                    i + 2,
                    difficulty,
                    offset_y=180,
                    title_suffix="Sudoku Puzzle"
                )
            
            # Add solution page
            self.pdf.add_page()
            # First solution
            self.add_sudoku_to_pdf(
                puzzles[i][1],
                i + 1,
                difficulty,
                offset_y=offset_y,
                title_suffix="Solution"
            )
            
            # Second solution if using 2 per page and if it exists
            if puzzles_per_page == 2 and i + 1 < total_puzzles:
                self.add_sudoku_to_pdf(
                    puzzles[i + 1][1],
                    i + 2,
                    difficulty,
                    offset_y=180,
                    title_suffix="Solution"
                )

    def save_pdf(self, output_file):
        self.pdf.output(output_file)
        print(f"PDF saved as: {output_file}")
