# Personal Git Bash

A custom command-line interface built with Python and PyQt6. This project replicates the core functionality of a regular Git Bash terminal while introducing powerful quality-of-life enhancements tailored for a more efficient workflow.

## Key Features

- **Core Git Bash Functionality:** Operates just like your standard Git Bash terminal, handling typical commands seamlessly.
- **Quick Directory Insertion (`Ctrl+F`):** Press `Ctrl+F` to open a native file explorer dialog. Once you select a folder, its path is instantly appended to your current command prompt. (e.g., type `cd `, press `Ctrl+F`, choose your folder, and it instantly becomes `cd C:\\Users\\...`).
- **GitHub Repository Fetcher (`Ctrl+I`):** Press `Ctrl+I` to open GitHub in your default web browser. This allows you to quickly locate a repository and insert its `.git` URL directly into your command line.
- **Selectable & Copyable Text:** Easily highlight, select, and copy both your command inputs and the terminal outputs—improving upon the rigid text handling of many traditional terminals.

## Installation & Setup

1. Clone or download this repository.
2. Install all required dependencies using the `requirements.txt` file:

## For The Executable

1. Install `pip install pyinstaller`
2. Run this command with the right adjustments:
> `pyinstaller --noconsole --icon="Icon\\personal-git.ico" --distpath <Your-Path-Location> personal-git.py`