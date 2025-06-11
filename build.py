import os
import subprocess

# Ensure PyInstaller is installed
subprocess.run(['pip', 'install', 'pyinstaller'])

# Run PyInstaller to create a standalone executable
# --onefile: Create a single executable file
# --add-data: Include the resources folder
# --name: Set the output executable name
subprocess.run([
    'pyinstaller',
    '--onefile',
    '--add-data', 'resources;resources',
    '--name', 'AllInOneCalculator',
    'main.py'
])

print('Build completed. Executable is available in the dist folder.')