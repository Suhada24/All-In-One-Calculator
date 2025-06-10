import sys
import sqlite3
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QGridLayout, QLineEdit, QComboBox, QDialog, 
    QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPalette, QColor, QIcon
import math
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class NavigationButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCheckable(True)
        self.setStyleSheet('''
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QPushButton:checked {
                background-color: #003366;
            }
        ''')

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('All-in-One Calculator')
        self.resize(900, 600)
        
        # Initialize variables
        self.buttons = []
        self.units = {}
        
        # Create resources directory if it doesn't exist
        if not os.path.exists('resources'):
            os.makedirs('resources')
            
        # Create default icons if they don't exist
        self.create_default_icons()
        
        self.init_database()
        self.setup_ui()

    def create_default_icons(self):
        # Create a simple text-based icon for copy
        copy_icon_path = os.path.join('resources', 'copy_icon.png')
        if not os.path.exists(copy_icon_path):
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (32, 32), color='white')
            d = ImageDraw.Draw(img)
            d.text((8, 8), 'C', fill='black')
            img.save(copy_icon_path)

        # Create a simple text-based icon for export
        export_icon_path = os.path.join('resources', 'export_icon.png')
        if not os.path.exists(export_icon_path):
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (32, 32), color='white')
            d = ImageDraw.Draw(img)
            d.text((8, 8), 'E', fill='black')
            img.save(export_icon_path)

    def setup_ui(self):
        self.setStyleSheet('''
            QMainWindow {
                background-color: #001f3f;
                color: white;
            }
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                border-radius: 5px;
                padding: 10px;
                font-size: 18px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox {
                background-color: #001f3f;
                color: white;
                border: 1px solid #003366;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        ''')

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Navigation bar
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        nav_widget.setFixedWidth(180)
        nav_widget.setStyleSheet('background-color: #001a33;')

        nav_items = [
            ('Simple Calc', 0),
            ('Scientific Calc', 1),
            ('Unit Converter', 2),
            ('Size Guide', 3),
            ('History', 4)
        ]
        for text, idx in nav_items:
            btn = NavigationButton(text)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            nav_layout.addWidget(btn)
            self.buttons.append(btn)
        nav_layout.addStretch(1)

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_simple_calculator_page())
        self.stacked_widget.addWidget(self.create_scientific_calculator_page())
        self.stacked_widget.addWidget(self.create_unit_converter_page())
        self.stacked_widget.addWidget(self.create_size_guide_page())
        self.stacked_widget.addWidget(self.create_history_page())

        main_layout.addWidget(nav_widget)
        main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(central_widget)

        # Theme toggle switch
        self.theme_toggle = QCheckBox('Dark Mode')
        self.theme_toggle.setChecked(False)
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        self.theme_toggle.setStyleSheet('''
            QCheckBox {
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        ''')
        main_layout.addWidget(self.theme_toggle, alignment=Qt.AlignTop | Qt.AlignRight)

    def init_database(self):
        try:
            conn = sqlite3.connect('calculator_history.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    expression TEXT,
                    result TEXT,
                    type TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            QMessageBox.warning(self, "Database Error", 
                              "Failed to initialize database. History feature may not work properly.")

    def log_calculation(self, expression, result, calc_type):
        conn = sqlite3.connect('calculator_history.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (timestamp, expression, result, type)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), expression, result, calc_type))
        conn.commit()
        conn.close()

    def create_simple_calculator_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Display
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                border-radius: 5px;
                padding: 10px;
                font-size: 18px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        ''')
        layout.addWidget(self.display)

        # Buttons
        buttons_layout = QGridLayout()
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            'C'
        ]
        positions = [(i, j) for i in range(5) for j in range(4)]
        for position, text in zip(positions, buttons):
            button = QPushButton(text)
            button.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            buttons_layout.addWidget(button, *position)
        layout.addLayout(buttons_layout)

        # Copy Result and Export PDF buttons
        action_layout = QHBoxLayout()
        copy_button = QPushButton('Copy Result')
        copy_button.clicked.connect(self.copy_result)
        copy_button.setIcon(QIcon(os.path.join('resources', 'copy_icon.png')))
        action_layout.addWidget(copy_button)

        export_button = QPushButton('Export PDF')
        export_button.clicked.connect(self.export_pdf)
        export_button.setIcon(QIcon(os.path.join('resources', 'export_icon.png')))
        action_layout.addWidget(export_button)

        layout.addLayout(action_layout)

        return page

    def on_button_click(self, text):
        if text == 'C':
            self.display.clear()
        elif text == '=':
            try:
                expr = self.display.text()
                if not expr:
                    return
                result = eval(expr)
                if isinstance(result, (int, float)):
                    if result == float('inf') or result == float('-inf'):
                        self.display.setText('Error: Division by zero')
                    else:
                        self.display.setText(str(result))
                        self.log_calculation(expr, str(result), 'simple')
                else:
                    self.display.setText('Error: Invalid result')
            except ZeroDivisionError:
                self.display.setText('Error: Division by zero')
            except Exception as e:
                self.display.setText('Error: Invalid input')
        else:
            self.display.setText(self.display.text() + text)

    def copy_result(self):
        try:
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setText(self.display.text())
            clipboard.setMimeData(mime_data)
            QMessageBox.information(self, "Success", "Result copied to clipboard!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to copy result: {str(e)}")

    def export_pdf(self):
        try:
            filename = f"calculator_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            c.drawString(100, 750, f"Expression: {self.display.text()}")
            c.drawString(100, 730, f"Result: {self.display.text()}")
            c.save()
            QMessageBox.information(self, "Success", f"PDF exported successfully to {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export PDF: {str(e)}")

    def create_scientific_calculator_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Display
        self.scientific_display = QLineEdit()
        self.scientific_display.setReadOnly(True)
        self.scientific_display.setAlignment(Qt.AlignRight)
        self.scientific_display.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                padding: 10px;
                font-size: 24px;
            }
        ''')
        layout.addWidget(self.scientific_display)

        # Navigation buttons for different sets
        nav_layout = QHBoxLayout()
        self.basic_button = QPushButton('Basic')
        self.trig_button = QPushButton('Trig')
        self.log_exp_button = QPushButton('Log/Exp')
        self.constants_button = QPushButton('Constants')

        for button in [self.basic_button, self.trig_button, self.log_exp_button, self.constants_button]:
            button.setStyleSheet('''
                QPushButton {
                    background-color: #001f3f;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #003366;
                }
            ''')
            nav_layout.addWidget(button)

        self.basic_button.clicked.connect(lambda: self.show_button_set('basic'))
        self.trig_button.clicked.connect(lambda: self.show_button_set('trig'))
        self.log_exp_button.clicked.connect(lambda: self.show_button_set('log_exp'))
        self.constants_button.clicked.connect(lambda: self.show_button_set('constants'))

        layout.addLayout(nav_layout)

        # Degree/Radian toggle
        self.degree_radian_toggle = QPushButton('Degree')
        self.degree_radian_toggle.setCheckable(True)
        self.degree_radian_toggle.setStyleSheet('''
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:checked {
                background-color: #003366;
            }
        ''')
        self.degree_radian_toggle.clicked.connect(self.toggle_degree_radian)
        layout.addWidget(self.degree_radian_toggle)

        # Grid layout for scientific calculator buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        layout.addLayout(self.grid_layout)

        # Initial button set
        self.show_button_set('basic')

        return page

    def show_button_set(self, set_name):
        # Clear existing buttons
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        if set_name == 'basic':
            buttons = [
                ('^', 0, 0), ('sqrt', 0, 1), ('%', 0, 2), ('!', 0, 3),
                ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
                ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
                ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
                ('0', 4, 0), ('=', 4, 1), ('+', 4, 2), ('C', 4, 3)
            ]
        elif set_name == 'trig':
            buttons = [
                ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('sinh', 0, 3),
                ('cosh', 1, 0), ('tanh', 1, 1), ('(', 1, 2), (')', 1, 3),
                ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3),
                ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3),
                ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3),
                ('0', 5, 0), ('=', 5, 1), ('+', 5, 2), ('C', 5, 3)
            ]
        elif set_name == 'log_exp':
            buttons = [
                ('log', 0, 0), ('ln', 0, 1), ('e^x', 0, 2), ('10^x', 0, 3),
                ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
                ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
                ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
                ('0', 4, 0), ('=', 4, 1), ('+', 4, 2), ('C', 4, 3)
            ]
        elif set_name == 'constants':
            buttons = [
                ('π', 0, 0), ('e', 0, 1), ('phi', 0, 2), ('(', 0, 3),
                ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
                ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
                ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
                ('0', 4, 0), ('=', 4, 1), ('+', 4, 2), ('C', 4, 3)
            ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.setStyleSheet('''
                QPushButton {
                    background-color: #001f3f;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #003366;
                }
            ''')
            button.clicked.connect(lambda checked, t=text: self.on_scientific_button_click(t))
            self.grid_layout.addWidget(button, row, col)

    def toggle_degree_radian(self):
        if self.degree_radian_toggle.isChecked():
            self.degree_radian_toggle.setText('Radian')
        else:
            self.degree_radian_toggle.setText('Degree')

    def on_scientific_button_click(self, text):
        if text == 'C':
            self.scientific_display.clear()
        elif text == '=':
            try:
                expr = self.scientific_display.text()
                if not expr:
                    return
                # Replace scientific functions with math module equivalents
                expr = expr.replace('sin', 'math.sin')
                expr = expr.replace('cos', 'math.cos')
                expr = expr.replace('tan', 'math.tan')
                expr = expr.replace('sinh', 'math.sinh')
                expr = expr.replace('cosh', 'math.cosh')
                expr = expr.replace('tanh', 'math.tanh')
                expr = expr.replace('log', 'math.log10')
                expr = expr.replace('ln', 'math.log')
                expr = expr.replace('sqrt', 'math.sqrt')
                expr = expr.replace('^', '**')
                expr = expr.replace('π', 'math.pi')
                expr = expr.replace('e', 'math.e')
                expr = expr.replace('phi', '1.618033988749895')

                # Convert degrees to radians if in degree mode
                if not self.degree_radian_toggle.isChecked():
                    expr = expr.replace('math.sin', 'math.sin(math.radians')
                    expr = expr.replace('math.cos', 'math.cos(math.radians')
                    expr = expr.replace('math.tan', 'math.tan(math.radians')

                # Secure evaluation
                allowed_names = {'math': math}
                result = eval(expr, {"__builtins__": {}}, allowed_names)
                if isinstance(result, (int, float)):
                    if result == float('inf') or result == float('-inf'):
                        self.scientific_display.setText('Error: Division by zero')
                    else:
                        self.scientific_display.setText(str(result))
                        self.log_calculation(expr, str(result), 'scientific')
                else:
                    self.scientific_display.setText('Error: Invalid result')
            except ZeroDivisionError:
                self.scientific_display.setText('Error: Division by zero')
            except Exception as e:
                self.scientific_display.setText('Error: Invalid input')
        else:
            self.scientific_display.setText(self.scientific_display.text() + text)

    def create_unit_converter_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Category dropdown
        self.category = QComboBox()
        self.category.addItems(['Length', 'Weight', 'Volume', 'Temperature'])
        self.category.setStyleSheet('''
            QComboBox {
                background-color: #001f3f;
                color: white;
                border: 1px solid #003366;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-family: 'Montserrat', 'Poppins', sans-serif;
            }
        ''')
        layout.addWidget(self.category)

        # From Unit dropdown
        self.from_unit = QComboBox()
        self.from_unit.setStyleSheet('''
            QComboBox {
                background-color: #001f3f;
                color: white;
                border: 1px solid #003366;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-family: 'Montserrat', 'Poppins', sans-serif;
            }
        ''')
        layout.addWidget(self.from_unit)

        # To Unit dropdown
        self.to_unit = QComboBox()
        self.to_unit.setStyleSheet('''
            QComboBox {
                background-color: #001f3f;
                color: white;
                border: 1px solid #003366;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-family: 'Montserrat', 'Poppins', sans-serif;
            }
        ''')
        layout.addWidget(self.to_unit)

        # Input field
        self.input_value = QLineEdit()
        self.input_value.setPlaceholderText('Enter value')
        self.input_value.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                border-radius: 8px;
                padding: 10px;
                font-size: 18px;
                font-family: 'Montserrat', 'Poppins', sans-serif;
            }
        ''')
        layout.addWidget(self.input_value)

        # Convert button
        self.convert_button = QPushButton('Convert')
        self.convert_button.setStyleSheet('''
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 18px;
                font-family: 'Montserrat', 'Poppins', sans-serif;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        ''')
        self.convert_button.clicked.connect(self.convert_units)
        layout.addWidget(self.convert_button)

        # Result label
        self.result_label = QLabel('Result: ')
        self.result_label.setStyleSheet('font-size: 24px; color: white; font-family: "Montserrat", "Poppins", sans-serif;')
        layout.addWidget(self.result_label)

        # Update unit dropdowns based on category
        self.category.currentTextChanged.connect(self.update_unit_dropdowns)
        self.update_unit_dropdowns(self.category.currentText())

        return page

    def update_unit_dropdowns(self, category):
        self.from_unit.clear()
        self.to_unit.clear()
        if category == 'Length':
            units = ['cm', 'm', 'km', 'in', 'ft']
        elif category == 'Weight':
            units = ['g', 'kg', 'lb', 'oz']
        elif category == 'Volume':
            units = ['ml', 'l', 'gal']
        elif category == 'Temperature':
            units = ['C', 'F', 'K']
        self.from_unit.addItems(units)
        self.to_unit.addItems(units)

    def convert_units(self):
        category = self.category.currentText()
        from_unit = self.from_unit.currentText()
        to_unit = self.to_unit.currentText()
        try:
            value = float(self.input_value.text())
            if category == 'Length':
                # Convert to meters first
                if from_unit == 'cm':
                    value = value / 100
                elif from_unit == 'km':
                    value = value * 1000
                elif from_unit == 'in':
                    value = value * 0.0254
                elif from_unit == 'ft':
                    value = value * 0.3048
                # Convert from meters to target unit
                if to_unit == 'cm':
                    value = value * 100
                elif to_unit == 'km':
                    value = value / 1000
                elif to_unit == 'in':
                    value = value / 0.0254
                elif to_unit == 'ft':
                    value = value / 0.3048
            elif category == 'Weight':
                # Convert to kilograms first
                if from_unit == 'g':
                    value = value / 1000
                elif from_unit == 'lb':
                    value = value * 0.453592
                elif from_unit == 'oz':
                    value = value * 0.0283495
                # Convert from kilograms to target unit
                if to_unit == 'g':
                    value = value * 1000
                elif to_unit == 'lb':
                    value = value / 0.453592
                elif to_unit == 'oz':
                    value = value / 0.0283495
            elif category == 'Volume':
                # Convert to liters first
                if from_unit == 'ml':
                    value = value / 1000
                elif from_unit == 'gal':
                    value = value * 3.78541
                # Convert from liters to target unit
                if to_unit == 'ml':
                    value = value * 1000
                elif to_unit == 'gal':
                    value = value / 3.78541
            elif category == 'Temperature':
                # Convert to Celsius first
                if from_unit == 'F':
                    value = (value - 32) * 5 / 9
                elif from_unit == 'K':
                    value = value - 273.15
                # Convert from Celsius to target unit
                if to_unit == 'F':
                    value = value * 9 / 5 + 32
                elif to_unit == 'K':
                    value = value + 273.15
            self.result_label.setText(f'Result: {value:.2f} {to_unit}')
        except ValueError:
            self.result_label.setText('Error: Invalid input')

    def create_size_guide_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Gender dropdown
        self.gender = QComboBox()
        self.gender.addItems(['Male', 'Female'])
        self.gender.setStyleSheet('''
            QComboBox {
                background-color: #001f3f;
                color: white;
                border: 1px solid #003366;
                padding: 5px;
                font-size: 16px;
            }
        ''')
        layout.addWidget(self.gender)

        # Input fields
        self.height = QLineEdit()
        self.height.setPlaceholderText('Height (cm)')
        self.height.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                padding: 10px;
                font-size: 18px;
            }
        ''')
        layout.addWidget(self.height)

        self.weight = QLineEdit()
        self.weight.setPlaceholderText('Weight (kg)')
        self.weight.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                padding: 10px;
                font-size: 18px;
            }
        ''')
        layout.addWidget(self.weight)

        self.chest = QLineEdit()
        self.chest.setPlaceholderText('Chest (cm)')
        self.chest.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                padding: 10px;
                font-size: 18px;
            }
        ''')
        layout.addWidget(self.chest)

        self.waist = QLineEdit()
        self.waist.setPlaceholderText('Waist (cm)')
        self.waist.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                padding: 10px;
                font-size: 18px;
            }
        ''')
        layout.addWidget(self.waist)

        # Calculate button
        self.calculate_button = QPushButton('Calculate Size')
        self.calculate_button.setStyleSheet('''
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                padding: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        ''')
        self.calculate_button.clicked.connect(self.calculate_size)
        layout.addWidget(self.calculate_button)

        # Result field
        self.size_result = QLineEdit()
        self.size_result.setReadOnly(True)
        self.size_result.setPlaceholderText('Recommended Size')
        self.size_result.setStyleSheet('''
            QLineEdit {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                padding: 10px;
                font-size: 18px;
            }
        ''')
        layout.addWidget(self.size_result)

        # Show Size Chart button
        self.show_chart_button = QPushButton('Show Size Chart')
        self.show_chart_button.setStyleSheet('''
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                padding: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        ''')
        self.show_chart_button.clicked.connect(self.show_size_chart)
        layout.addWidget(self.show_chart_button)

        return page

    def calculate_size(self):
        try:
            height = float(self.height.text())
            weight = float(self.weight.text())
            chest = float(self.chest.text())
            waist = float(self.waist.text())
            gender = self.gender.currentText()

            # Simple size calculation logic
            if gender == 'Male':
                if chest < 90 and waist < 80:
                    size = 'S'
                elif chest < 100 and waist < 90:
                    size = 'M'
                elif chest < 110 and waist < 100:
                    size = 'L'
                else:
                    size = 'XL'
            else:  # Female
                if chest < 85 and waist < 70:
                    size = 'S'
                elif chest < 95 and waist < 80:
                    size = 'M'
                elif chest < 105 and waist < 90:
                    size = 'L'
                else:
                    size = 'XL'

            self.size_result.setText(f'Recommended Size: {size}')
        except ValueError:
            self.size_result.setText('Error: Invalid input')

    def show_size_chart(self):
        chart_dialog = QDialog(self)
        chart_dialog.setWindowTitle('Size Chart')
        chart_dialog.setModal(True)
        chart_dialog.setStyleSheet('background-color: #001f3f; color: white;')

        layout = QVBoxLayout(chart_dialog)

        # Size chart content
        chart_text = QLabel('Size Chart:\n\n'
                           'Male:\n'
                           'S: Chest < 90cm, Waist < 80cm\n'
                           'M: Chest < 100cm, Waist < 90cm\n'
                           'L: Chest < 110cm, Waist < 100cm\n'
                           'XL: Chest >= 110cm, Waist >= 100cm\n\n'
                           'Female:\n'
                           'S: Chest < 85cm, Waist < 70cm\n'
                           'M: Chest < 95cm, Waist < 80cm\n'
                           'L: Chest < 105cm, Waist < 90cm\n'
                           'XL: Chest >= 105cm, Waist >= 90cm')
        chart_text.setStyleSheet('font-size: 16px;')
        layout.addWidget(chart_text)

        # Close button
        close_button = QPushButton('Close')
        close_button.setStyleSheet('''
            QPushButton {
                background-color: #001f3f;
                color: white;
                border: none;
                padding: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        ''')
        close_button.clicked.connect(chart_dialog.close)
        layout.addWidget(close_button)

        chart_dialog.exec_()

    def create_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Table view for history
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(['Timestamp', 'Expression', 'Result', 'Type'])
        self.history_table.setStyleSheet('''
            QTableWidget {
                background-color: #001a33;
                color: white;
                border: 1px solid #003366;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-family: 'Montserrat', 'Poppins', sans-serif;
            }
            QHeaderView::section {
                background-color: #001f3f;
                color: white;
                border: 1px solid #003366;
                padding: 5px;
            }
        ''')
        layout.addWidget(self.history_table)

        # Load history data
        self.load_history()

        return page

    def load_history(self):
        conn = sqlite3.connect('calculator_history.db')
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, expression, result, type FROM history ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        self.history_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.history_table.setItem(i, j, QTableWidgetItem(str(value)))
        conn.close()

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def toggle_theme(self, state):
        if state == Qt.Checked:
            self.setStyleSheet('''
                QMainWindow {
                    background-color: #121212;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #121212;
                    color: #f0f0f0;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 18px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #1e1e1e;
                }
                QLineEdit {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 18px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QComboBox {
                    background-color: #121212;
                    color: #f0f0f0;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 16px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLabel {
                    color: #f0f0f0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            ''')
        else:
            self.setStyleSheet('''
                QMainWindow {
                    background-color: #001f3f;
                    color: white;
                }
                QPushButton {
                    background-color: #001f3f;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 18px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #003366;
                }
                QLineEdit {
                    background-color: #001a33;
                    color: white;
                    border: 1px solid #003366;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 18px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QComboBox {
                    background-color: #001f3f;
                    color: white;
                    border: 1px solid #003366;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 16px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLabel {
                    color: white;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            ''')

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        calculator = Calculator()
        calculator.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        sys.exit(1)