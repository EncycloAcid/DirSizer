# 📁 DirSizer  (with Rich UI)

A Python command-line tool featuring a Rich-enhanced interface to calculate folder sizes, display them clearly, and optionally rename folders to include their size information.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This utility provides an interactive menu to help you analyze disk space usage by folders. It can:

*   Calculate the total size of folders recursively (including all nested content).
*   Display sizes in -readable format (KB, MB, GB, etc.).
*   Present information clearly using tables, progress bars, and styled text via the `rich` library.
*   Optionally rename folders (either individually or batch rename subfolders) to append their calculated size.

## Features

*   **✨ Rich Interface:** Enhanced command-line experience with progress bars, spinners, styled text, tables, and panels.
*   **💻 Interactive Menu:** Simple numerical menu to select actions.
*   **📊 Accurate Size Calculation:** Recursively scans folders for total size.
*   **📈 Readable Sizes:** Converts bytes to KB, MB, GB, etc.
*   **📑 Three Core Actions:**
    1.  **List Subfolder Sizes:** Select a parent directory → view sizes of its immediate subfolders.
    2.  **Rename Multiple Subfolders:** Select a parent directory → calculate subfolder sizes → confirm → rename subfolders to `FolderName [Size]`.
    3.  **Analyze & Rename Single Folder:** Select a *specific* folder → calculate its size → confirm → rename the folder itself to `FolderName [Size]`.
    *   **🪟 Graphical Folder Selection:** Uses built-in Tkinter for easy folder selection dialogs.
*   **🛡️ Safety Features:**
    *   **Confirmation Prompts:** Critical prompts before any potentially destructive renaming action.
    *   **Skip Existing:** Attempts to detect and skip renaming folders that already appear to have a size appended (`[Size Units]` format).
    *   **Path Length Check:** Prevents renaming if the resulting path might exceed common OS limits.
    *   **Target Exists Check:** Avoids overwriting if a folder with the proposed new name already exists.
*   **⚠️ Error Handling:** Basic handling for permission errors or inaccessible files/folders during scans.

## ⚠️ WARNING: Rename Hazard!

The renaming features (Options 2 and 3) **permanently modify folder names** on your filesystem. This action **cannot be easily undone automatically**.

*   **🛑 BACK UP YOUR DATA** before using the rename features on important directories.
*   **🧪 TEST** the script on non-critical folders first to understand its behavior.
*   **👀 REVIEW** the proposed renames carefully before confirming.


## Requirements

*   **Python 3.x** (Developed with Python 3.7+)
*   **Rich:** For the enhanced terminal UI. Install via pip:
    ```bash
    pip install rich
    ```
*   **Tkinter:** Required for the graphical folder selection dialogs.
    *   Usually included with standard Python installations on Windows and macOS.
    *   On some Linux distributions, you might need to install it separately (e.g., `sudo apt-get update && sudo apt-get install python3-tk` on Debian/Ubuntu).

## How to Use

1.  **Download/Clone:** Get the script file (e.g., `DirSizer.py`) onto your computer.
2.  **Open Terminal/Command Prompt:** Launch your terminal (macOS/Linux) or command prompt (Windows).
3.  **Navigate:** Use the `cd` command to go to the directory where you saved the script file.
    ```bash
    cd path/to/your/script/directory
    ```
4.  **Run Script:** Execute the script using Python 3.
    ```bash
    DirSizer.py
    ```
    *(You might need to use `python3` instead of `python` depending on your system setup)*
5.  **Use Menu:** The script will display the main menu in your terminal. Enter the number corresponding to the action you want (1, 2, 3, or 4 to exit).
6.  **Select Folder:** A graphical folder selection window will pop up when needed. Choose the appropriate directory based on the selected menu action.
7.  **Follow Prompts:** Read the output in the terminal. Size calculations might take time for large folders (progress bars will be shown).
8.  **Confirm Renames:** If using options 2 or 3, carefully review the proposed changes displayed in the terminal table, then **explicitly confirm** the action in the pop-up dialog box before any folders are renamed.
9.  **Return to Menu:** After completing an action, press Enter to return to the main menu.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Please feel free to open an issue or submit a pull request.
