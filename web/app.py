from flask import Flask, render_template, request, send_file, jsonify
import os
from dotenv import load_dotenv
from pathlib import Path
import tempfile
from datetime import datetime

# Import existing PDF generator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdf_generator import PDFGenerator
from puzzle_generator import generate_puzzle

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Add current year to all template contexts
@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get form data
        grid_size = int(request.form['grid_size'])
        difficulty = request.form['difficulty']
        num_puzzles = min(int(request.form['num_puzzles']), 50)  # Limit to 50 puzzles max
        
        # Validate input
        valid_grid_sizes = [4, 9, 16]
        if grid_size not in valid_grid_sizes:
            raise ValueError("Grid size must be 4x4, 9x9, or 16x16")
        
        if difficulty not in ['easy', 'medium', 'hard']:
            raise ValueError("Invalid difficulty level")
        
        if num_puzzles < 1:
            raise ValueError("Number of puzzles must be at least 1")
        
        # Generate puzzles
        puzzles = []
        for _ in range(num_puzzles):
            puzzle, solution = generate_puzzle(grid_size, difficulty)
            puzzles.append((puzzle, solution))
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
        
        # Generate PDF
        generator = PDFGenerator(grid_size=grid_size)
        generator.generate_puzzles_pdf(puzzles, difficulty)
        generator.save_pdf(pdf_path)
        
        # Send file
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'sudoku-{difficulty}-{timestamp}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
