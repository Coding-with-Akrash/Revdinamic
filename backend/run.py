#!/usr/bin/env python3
"""RevDynamics Flask Backend Runner"""
import subprocess
import sys

def main():
    print("Starting RevDynamics Backend...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
    subprocess.run([sys.executable, 'app.py'])

if __name__ == '__main__':
    main()