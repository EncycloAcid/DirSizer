# 📁 Folder Size Utility

A Python command-line tool to calculate folder sizes, display them in a human-readable format, and optionally rename folders to include their size information.

## Features

*   **Interactive Menu:** Easy-to-use command-line interface to choose actions.
*   **Accurate Size Calculation:** Recursively calculates the total size of folders, including all nested files and subfolders.
*   **Human-Readable Output:** Displays sizes in familiar units (B, KB, MB, GB, TB, etc.).
*   **Three Main Actions:**
    1.  **List Subfolder Sizes:** Select a parent directory and view a list of its immediate subfolders along with their calculated sizes.
    2.  **Rename Multiple Subfolders:** Select a parent directory, calculate the size of its immediate subfolders, and (after confirmation) rename them to `FolderName [Size]`.
    3.  **Analyze & Rename Single Folder:** Select a *specific* folder, calculate its size, and (after confirmation) rename *that single folder* to `FolderName [Size]`.
*   **Graphical Dialogs:** Uses built-in Tkinter for user-friendly folder selection dialogs.
*   **Safety Features:**
    *   Includes clear confirmation prompts before any renaming action is performed.
    *   Attempts to detect and skip renaming folders that already appear to have a size appended (using the `[Size Units]` format).
    *   Checks for potential issues like resulting path length exceeding limits or target names already existing before renaming.
*   **Error Handling:** Basic handling for permission errors or inaccessible files/folders during size calculation.

> **⚠️ WARNING:** The renaming features (Options 2 and 3) modify your folder names directly on the filesystem. This operation **cannot be easily undone automatically**. Always **back up important data** or test the script on non-critical directories first before using the renaming features on valuable folders!

## Requirements

*   **Python 3.x:** The script is written for Python 3.
*   **Tkinter:** Required for the graphical folder selection dialogs. Tkinter is usually included with standard Python installations on Windows and macOS. On some Linux distributions, you might need to install it separately (e.g., `sudo apt-get update && sudo apt-get install python3-tk` on Debian/Ubuntu).

## How to Use

1.  **Download/Clone:** Get the script file (e.g., `folder_size_utility.py`) onto your computer.
2.  **Open Terminal:** Launch your command prompt (Windows) or terminal (macOS/Linux).
3.  **Navigate:** Use the `cd` command to go to the directory where you saved the script file.
    ```bash
    cd path/to/your/script/directory
    ```
4.  **Run Script:** Execute the script using Python.
    ```bash
    python folder_size_utility.py
    ```
5.  **Use Menu:** The script will display the main menu. Enter the number corresponding to the action you wish to perform (1, 2, 3, or 4 to exit).
6.  **Select Folder:** When prompted, a graphical folder selection window will appear. Choose the appropriate directory based on the action selected (either the parent directory or the specific folder).
7.  **Follow Prompts:** Read the output and any confirmation messages carefully. Calculation might take time for very large folders.
8.  **Confirm Renames:** If using options 2 or 3, you **must explicitly confirm** the renaming operation in a dialog box before any changes are made.

## License


Example:
This project is licensed under the MIT License - see the LICENSE.md file for details.
