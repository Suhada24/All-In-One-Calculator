# All-in-One Calculator

A comprehensive calculator application built with PyQt5 that includes:
- Simple Calculator
- Scientific Calculator
- Unit Converter
- Size Guide
- Calculation History
- Dark/Light Mode
- PDF Export
- Copy to Clipboard

## Features
- Modern UI with dark/light mode toggle
- SQLite database for calculation history
- PDF export functionality
- Copy results to clipboard
- Responsive design
- Error handling and user feedback

## Deployment

### Option 1: Source Distribution
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd All-in-One-Calculator
   ```
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

### Option 2: Standalone Executable
1. Ensure you have Python 3.7+ installed.
2. Run the build script:
   ```bash
   python build.py
   ```
3. The standalone executable will be created in the `dist` folder.
4. Run the executable:
   - On Windows: Double-click `AllInOneCalculator.exe` in the `dist` folder.
   - On macOS/Linux: Open a terminal, navigate to the `dist` folder, and run `./AllInOneCalculator`.

## Usage

Run the application:
```bash
python main.py
```

### Features Guide:
1. **Simple Calculator**: Basic arithmetic operations
2. **Scientific Calculator**: Advanced mathematical functions
3. **Unit Converter**: Convert between different units
4. **Size Guide**: Size conversion and visualization
5. **History**: View past calculations
6. **Dark Mode**: Toggle between light and dark themes
7. **Copy Result**: Copy calculation result to clipboard
8. **Export PDF**: Save calculation as PDF

## Requirements
- Python 3.7+
- PyQt5
- ReportLab
- Pillow

## Error Handling
The application includes comprehensive error handling for:
- Invalid calculations
- File operations
- Database operations
- Clipboard operations
- PDF generation

## Contributing
Feel free to submit issues and enhancement requests!