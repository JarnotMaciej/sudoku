from fpdf import FPDF

class SudokuPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0)  # Pure black for e-ink
        self.cell(0, 10, 'jarnotmaciej.com', 0, 0, 'C')

class PDFGenerator:
    def __init__(self, grid_size=9):
        self.pdf = SudokuPDF()
        # Reduced margin for better page fit
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.grid_size = grid_size
        self.box_size = int(grid_size ** 0.5)
        # Optimized cell sizes for e-ink display
        self.cell_size = {
            4: 18,   # Larger cells for better visibility on 4x4
            9: 12,   # Optimized for 9x9 standard
            16: 8    # Adjusted for 16x16 readability
        }[grid_size]
        
        # Optimize for e-ink display
        self.pdf.set_fill_color(255, 255, 255)  # Pure white background
        self.pdf.set_text_color(0, 0, 0)        # Pure black text
        self.pdf.set_draw_color(0, 0, 0)        # Pure black lines

    def add_title_page(self, difficulty):
        self.pdf.add_page()
        # Calculate overall layout
        page_height = 297  # A4 height in mm
        title_height = 80  # Space for both title lines
        footer_height = 30
        available_height = page_height - title_height - footer_height
        
        # Title section
        self.pdf.set_font('Helvetica', 'B', 36)
        self.pdf.cell(0, 30, f'{difficulty.capitalize()}', ln=True, align='C')
        self.pdf.set_font('Helvetica', 'B', 24)
        self.pdf.cell(0, 15, 'Zudoku', ln=True, align='C')
        self.pdf.set_font('Helvetica', '', 18)
        self.pdf.cell(0, 15, 'Zen Sudoku', ln=True, align='C')
        
        # Add decorative grid pattern
        self.add_decorative_grid(title_height, available_height)
        
        # Website caption at bottom
        self.pdf.set_y(-30)
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.cell(0, 10, 'jarnotmaciej.com', align='C')

    def add_decorative_grid(self, title_height, available_height):
        # Add centered decorative 3x3 grid pattern
        cell_size = 25  # Larger cells for better visibility
        pattern_width = cell_size * 3
        pattern_height = cell_size * 3
        
        # Center horizontally and vertically in available space
        start_x = (210 - pattern_width) / 2   # A4 width is 210mm
        start_y = title_height + (available_height - pattern_height) / 2
        
        self.pdf.set_line_width(0.5)
        for i in range(4):
            # Vertical lines
            self.pdf.line(start_x + i * cell_size, start_y, 
                         start_x + i * cell_size, start_y + 3 * cell_size)
            # Horizontal lines
            self.pdf.line(start_x, start_y + i * cell_size,
                         start_x + 3 * cell_size, start_y + i * cell_size)

    def format_cell_value(self, value):
        """Format cell value, converting to hexadecimal for 16x16 grids if needed."""
        if value == 0:
            return ""
        if self.grid_size == 16 and isinstance(value, str):
            return value  # Already a letter A-G
        if self.grid_size == 16 and value > 9:
            return chr(ord('A') + value - 10)  # Convert 10-16 to A-G
        return str(value)

    def add_sudoku_to_pdf(self, sudoku, puzzle_num, difficulty, offset_y, title_suffix="Zudoku"):
        # Use design system typography scale
        title_font_size = 24 if self.grid_size <= 9 else 20  # h3 size
        cell_font_size = 14 if self.grid_size <= 9 else 10   # body size

        self.pdf.set_font('Helvetica', 'B', title_font_size)
        self.pdf.set_xy(0, offset_y - 15)
        self.pdf.cell(210, 10, f'{difficulty.capitalize()} {title_suffix} #{puzzle_num}', ln=True, align='C')

        # Center the puzzle grid horizontally
        grid_width = self.grid_size * self.cell_size
        offset_x = (210 - grid_width) / 2  # A4 page width is 210mm

        # Add cells with optimized styling for e-ink
        self.pdf.set_font('Helvetica', '', cell_font_size)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.pdf.set_xy(offset_x + j * self.cell_size, offset_y + i * self.cell_size)
                value = self.format_cell_value(sudoku[i, j])
                self.pdf.set_line_width(0.3)
                self.pdf.cell(self.cell_size, self.cell_size, value, border=1, align='C')

        # Add bold grid lines optimized for e-ink
        self.pdf.set_line_width(2.0)  # Increased thickness for better visibility
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
        offset_y = 30  # Top puzzle position
        offset_y2 = 160  # Bottom puzzle position (increased for better spacing)

        for i in range(0, total_puzzles, puzzles_per_page * 2):  # *2 because we'll put puzzles and solutions together
            # Add puzzle page
            self.pdf.add_page()
            
            # First puzzle
            self.add_sudoku_to_pdf(
                puzzles[i][0],
                i + 1,
                difficulty,
                offset_y=offset_y,
                title_suffix="Puzzle"
            )
            
            # Second puzzle if exists
            if i + 1 < total_puzzles and puzzles_per_page == 2:
                self.add_sudoku_to_pdf(
                    puzzles[i + 1][0],
                    i + 2,
                    difficulty,
                    offset_y=offset_y2,  # Increased spacing from first puzzle
                    title_suffix="Puzzle"
                )

            # Add solutions page
            self.pdf.add_page()
            
            # First solution
            self.add_sudoku_to_pdf(
                puzzles[i][1],
                i + 1,
                difficulty,
                offset_y=offset_y,
                title_suffix="Solution"
            )
            
            # Second solution if exists
            if i + 1 < total_puzzles and puzzles_per_page == 2:
                self.add_sudoku_to_pdf(
                    puzzles[i + 1][1],
                    i + 2,
                    difficulty,
                    offset_y=offset_y2,  # Increased spacing from first solution
                    title_suffix="Solution"
                )

    def save_pdf(self, output_file):
        self.pdf.output(output_file)
        print(f"PDF saved as: {output_file}")
