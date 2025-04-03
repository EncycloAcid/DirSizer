import os
import sys
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.rule import Rule
from rich.text import Text
from rich import print

console = Console()

def format_size(size_bytes):
    """Converts a size in bytes to a human-readable format (KB, MB, GB, etc.)."""
    if size_bytes < 0: size_bytes = 0
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    power = 1024
    while (size_bytes >= power - 1) and i < len(size_name) - 1:
        size_bytes /= power
        i += 1
    s = "{:.2f}".format(size_bytes)
    s = s.rstrip('0').rstrip('.') if '.' in s else s
    return f"{s} {size_name[i]}"

def check_if_already_renamed(folder_name):
    """Checks if a folder name likely already ends with a size indicator."""
    pattern = r"\s+\[\d+(\.\d+)?\s+(B|K[Bb]|M[Bb]|G[Bb]|T[Bb]|P[Bb]|E[Bb]|Z[Bb]|Y[Bb])\]$"
    return re.search(pattern, folder_name) is not None

def get_folder_size(folder_path: Path):
    """Calculates the total size of a folder including all its subfolders and files.
       Uses pathlib.Path. Returns (total_size, items_skipped).
    """
    total_size = 0
    items_skipped = 0
    try:
        for entry in os.scandir(folder_path):
            entry_path = Path(entry.path)
            try:
                if entry.is_dir(follow_symlinks=False):
                    sub_size, sub_skipped = get_folder_size(entry_path)
                    total_size += sub_size
                    items_skipped += sub_skipped
                elif entry.is_file(follow_symlinks=False):
                    try:
                        total_size += entry_path.stat(follow_symlinks=False).st_size
                    except OSError:
                         items_skipped += 1
                         continue
            except OSError:
                items_skipped += 1
                continue
    except OSError as e:
         console.print(f"\n[[bold yellow]Warning[/]]: Error accessing content within [cyan]'{folder_path.name}'[/]: {e}")
         return total_size, items_skipped + 1
    return total_size, items_skipped

def select_directory(title="Select Folder") -> str | None:
    """Opens a dialog to select a directory. Returns path as string or None."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    initial_dir = Path.home()
    try:
        folder_selected = filedialog.askdirectory(title=title, initialdir=str(initial_dir))
    except Exception:
         folder_selected = filedialog.askdirectory(title=title)
    root.destroy()
    return folder_selected

def list_folders_with_sizes():
    """Action 1: List subfolders with sizes using Rich."""
    console.print(Rule("[bold cyan]List Subfolder Sizes[/]"))
    target_directory_str = select_directory(title="Select Parent Folder to List Subfolder Sizes")

    if not target_directory_str:
        console.print("[yellow]No directory selected. Returning to menu.[/]")
        return

    target_directory = Path(target_directory_str).resolve()

    if not target_directory.is_dir():
        console.print(f"[bold red]Error:[/bold red] Selected path is not a valid directory: [cyan]{target_directory}[/]")
        return

    console.print(f"Scanning directory: [cyan]{target_directory}[/]\n")

    folders_to_scan = []
    total_skipped_in_scan = 0
    try:
        with console.status("[bold green]Finding subdirectories..."):
            for item in target_directory.iterdir():
                if item.is_dir():
                    folders_to_scan.append({"name": item.name, "path": item})

        if not folders_to_scan:
            console.print("[yellow]No subfolders found in this directory.[/]")
            return

        console.print(f"Found {len(folders_to_scan)} subfolders. Calculating sizes...")

        results_data = []

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=True
        ) as progress:
            scan_task = progress.add_task("[cyan]Calculating...", total=len(folders_to_scan))

            for folder_info in sorted(folders_to_scan, key=lambda x: x['name'].lower()):
                folder_name = folder_info['name']
                folder_path = folder_info['path']
                progress.update(scan_task, description=f"[cyan]Calculating: [yellow]{folder_name}[/]")

                current_folder_skipped = 0
                error_msg = None
                formatted_size = "[grey50]N/A[/]"

                try:
                    size_bytes, skipped = get_folder_size(folder_path)
                    current_folder_skipped = skipped
                    total_skipped_in_scan += current_folder_skipped
                    formatted_size = format_size(size_bytes)
                except Exception as e:
                    error_msg = str(e)
                    console.print(f"\n[[bold red]Error[/]] calculating size for [yellow]{folder_name}[/]: {e}")

                results_data.append({
                    "name": folder_name,
                    "path": folder_path,
                    "size_str": formatted_size,
                    "skipped": current_folder_skipped,
                    "error": error_msg
                })
                progress.update(scan_task, advance=1)

        console.print(Rule("[bold cyan]Results[/]"))
        table = Table(title=f"Subfolders in [cyan]{target_directory.name}[/]", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Folder Name", style="dim cyan", width=40, no_wrap=False)
        table.add_column("Calculated Size", justify="right", style="green")
        table.add_column("Status", justify="left")

        for item in results_data:
            status = ""
            if item['error']:
                status = f"[bold red]Error: {item['error']}[/]"
            elif item['skipped'] > 0:
                status = f"[yellow]{item['skipped']} item(s) skipped[/]"
            else:
                 status = "[grey50]OK[/]"

            folder_name_text = Text(item['name'], overflow="fold")

            table.add_row(folder_name_text, item['size_str'], status)

        console.print(table)

        if total_skipped_in_scan > 0:
            console.print(f"\n[yellow]Note:[/yellow] A total of {total_skipped_in_scan} item(s) could not be accessed across all folders (permissions?).")
        console.print("Listing complete.")

    except PermissionError:
        console.print(f"\n[bold red]Error:[/bold red] Permission denied to read directory: [cyan]{target_directory}[/]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred during listing:[/bold red] {e}")


def rename_folders_with_size():
    """Action 2: Rename multiple subfolders with size using Rich."""
    console.print(Rule("[bold orange_red1]Rename Multiple Subfolders with Size[/]"))
    console.print("[bold yellow]⚠️ WARNING:[/] This will rename subfolders in the selected directory.")
    console.print("         Ensure you have backups or test on unimportant data first!")

    target_directory_str = select_directory(title="Select Parent Folder Containing Subfolders to Rename")

    if not target_directory_str:
        console.print("[yellow]No directory selected. Returning to menu.[/]")
        return

    target_directory = Path(target_directory_str).resolve()

    if not target_directory.is_dir():
        console.print(f"[bold red]Error:[/bold red] Selected path is not a valid directory: [cyan]{target_directory}[/]")
        return

    console.print(f"Scanning directory for renaming: [cyan]{target_directory}[/]\n")

    folders_to_process = []
    folders_to_rename_info = []
    skipped_already_named = 0
    total_skipped_items_calc = 0

    try:
        with console.status("[bold green]Finding subdirectories..."):
            for item in target_directory.iterdir():
                if item.is_dir():
                    folders_to_process.append({"name": item.name, "path": item})

        if not folders_to_process:
            console.print("[yellow]No subfolders found to rename in this directory.[/]")
            return

        console.print(f"Found {len(folders_to_process)} subfolders. Calculating sizes for renaming...")

        with Progress(
            TextColumn("[progress.description]{task.description}"), BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(), console=console, transient=True
        ) as progress:
            calc_task = progress.add_task("[cyan]Calculating...", total=len(folders_to_process))

            for folder_info in sorted(folders_to_process, key=lambda x: x['name'].lower()):
                folder_name = folder_info['name']
                old_path = folder_info['path']
                progress.update(calc_task, description=f"[cyan]Calculating: [yellow]{folder_name}[/]")

                if check_if_already_renamed(folder_name):
                    console.print(f"   -> [yellow]Skipping:[/yellow] [cyan]'{folder_name}'[/] (looks already renamed)")
                    skipped_already_named += 1
                    progress.update(calc_task, advance=1)
                    continue

                formatted_size = "[grey50]N/A[/]"
                new_folder_name = None
                new_path = None
                current_skipped = 0
                error_msg = None

                try:
                    size_bytes, skipped = get_folder_size(old_path)
                    current_skipped = skipped
                    total_skipped_items_calc += skipped
                    formatted_size = format_size(size_bytes)
                    new_folder_name = f"{folder_name} [{formatted_size}]"
                    new_path = target_directory / new_folder_name

                    if len(str(new_path)) > 240:
                         error_msg = "Resulting path too long"
                         console.print(f"   -> [yellow]Skipping:[/yellow] [cyan]'{folder_name}'[/] ({error_msg})")
                         progress.update(calc_task, advance=1)
                         continue

                    folders_to_rename_info.append({
                        "old_name": folder_name, "old_path": old_path,
                        "new_name": new_folder_name, "new_path": new_path,
                        "size_str": formatted_size, "skipped": current_skipped
                    })
                    console.print(f"   -> [green]OK:[/green] [cyan]'{folder_name}'[/] -> Size: [bold green]{formatted_size}[/]" + (f" ([yellow]{current_skipped} skipped[/])" if current_skipped else ""))

                except Exception as e:
                    error_msg = str(e)
                    console.print(f"\n   -> [[bold red]Error[/]] calculating size for [yellow]{folder_name}[/]: {e}")

                progress.update(calc_task, advance=1)


        console.print(f"\nCalculation complete. {skipped_already_named} folder(s) skipped as potentially already renamed.")
        if total_skipped_items_calc > 0:
             console.print(f"[yellow]Note:[/yellow] {total_skipped_items_calc} item(s) could not be accessed during size calculation.")
        print("")

        if not folders_to_rename_info:
            console.print("[yellow]No folders eligible for renaming found.[/]")
            return

        console.print(Rule("[bold yellow]Proposed Renames[/]"))
        confirm_table = Table(title="Review Carefully!", show_header=True, header_style="bold magenta", expand=True)
        confirm_table.add_column("Current Name", style="dim cyan", no_wrap=False)
        confirm_table.add_column(" ", justify="center")
        confirm_table.add_column("Proposed New Name", style="green", no_wrap=False)

        for rename_info in folders_to_rename_info:
            confirm_table.add_row(rename_info['old_name'], "->", rename_info['new_name'])

        console.print(confirm_table)

        root_confirm = tk.Tk(); root_confirm.withdraw(); root_confirm.attributes('-topmost', True)
        confirm = messagebox.askyesno(
            "Confirm Rename",
            f"Proceed with renaming {len(folders_to_rename_info)} folder(s) in:\n"
            f"{target_directory}\n\n"
            f"Review the proposed names in the terminal.\nThis action CANNOT be easily undone.",
            icon='warning' )
        root_confirm.destroy()

        if not confirm:
            console.print("[yellow]Rename operation cancelled by user.[/]")
            return

        console.print(Rule("[bold orange_red1]Performing Renames[/]"))
        success_count = 0
        fail_count = 0
        for rename_info in folders_to_rename_info:
            old = rename_info['old_path']
            new = rename_info['new_path']
            old_display = rename_info['old_name']
            new_display = rename_info['new_name']

            if new.exists():
                 console.print(f"   -> [bold red]Error:[/bold red] Cannot rename '[cyan]{old_display}[/]'. Target '[cyan]{new_display}[/]' already exists. Skipping.")
                 fail_count += 1
                 continue

            try:
                old.rename(new)
                console.print(f"   -> [green]Renamed:[/green] '[cyan]{old_display}[/]' -> '[bold green]{new_display}[/]'")
                success_count += 1
            except OSError as e:
                console.print(f"   -> [bold red]Error[/] renaming '[cyan]{old_display}[/]' to '[cyan]{new_display}[/]': {e}")
                fail_count += 1
            except Exception as e:
                 console.print(f"   -> [bold red]Unexpected Error[/] renaming '[cyan]{old_display}[/]': {e}")
                 fail_count += 1

        console.print(Rule("[bold cyan]Rename Summary[/]"))
        summary_table = Table(show_header=False, box=None, padding=(0,1))
        summary_table.add_column()
        summary_table.add_column(justify="right")
        summary_table.add_row("[green]Successfully renamed:[/]", f"[bold green]{success_count}[/]")
        skipped_total = fail_count + skipped_already_named + len([f for f in folders_to_rename_info if len(str(f['new_path'])) > 240])
        summary_table.add_row("[yellow]Failed/Skipped:[/]", f"[bold yellow]{skipped_total}[/]")
        console.print(summary_table)
        console.print("Rename operation finished.")


    except PermissionError:
        console.print(f"\n[bold red]Error:[/bold red] Permission denied to read directory: [cyan]{target_directory}[/]")
    except FileNotFoundError:
         console.print(f"\n[bold red]Error:[/bold red] Directory not found during scan: [cyan]{target_directory}[/]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred during renaming process:[/bold red] {e}")


def analyze_and_rename_single_folder():
    """Action 3: Analyze & rename a single selected folder using Rich."""
    console.print(Rule("[bold blue]Analyze & Rename Single Folder[/]"))
    console.print("Select the specific folder you want to analyze and potentially rename.")
    console.print("[bold yellow]⚠️ WARNING:[/] This will rename the selected folder itself.")

    selected_folder_path_str = select_directory(title="Select Folder to Analyze and Rename")

    if not selected_folder_path_str:
        console.print("[yellow]No directory selected. Returning to menu.[/]")
        return

    selected_folder_path = Path(selected_folder_path_str).resolve()

    if not selected_folder_path.is_dir():
        console.print(f"[bold red]Error:[/bold red] Selected path is not a valid directory: [cyan]{selected_folder_path}[/]")
        return

    folder_name = selected_folder_path.name
    parent_dir = selected_folder_path.parent

    console.print(f"\nAnalyzing folder: [bold cyan]'{folder_name}'[/]")
    console.print(f"             in: [dim cyan]{parent_dir}[/]")

    if check_if_already_renamed(folder_name):
        console.print(f"\n[yellow]Folder '[cyan]{folder_name}[/]' appears to already have a size appended. Skipping rename proposal.[/]")
        try:
            with console.status("[bold green]Calculating size anyway..."):
                size_bytes, skipped = get_folder_size(selected_folder_path)
            formatted_size = format_size(size_bytes)
            console.print(f"\nCalculated size: [bold green]{formatted_size}[/]" + (f" ([yellow]{skipped} items skipped[/])" if skipped else ""))
        except Exception as e:
            console.print(f"\n[bold red]Error calculating size:[/bold red] {e}")
        return

    total_skipped_items = 0
    formatted_size = "[grey50]N/A[/]"
    new_folder_name = None
    new_full_path = None

    try:
        with console.status(f"[bold green]Calculating size for '{folder_name}'...", spinner="dots") as status:
            start_time = time.time()
            size_bytes, skipped = get_folder_size(selected_folder_path)
            total_skipped_items = skipped
            end_time = time.time()
            formatted_size = format_size(size_bytes)
            status.update(f"[bold green]Calculation complete for '{folder_name}'[/]")

        console.print(f"Calculation finished in {end_time - start_time:.2f} seconds.")
        console.print(f"\nFolder: '[bold cyan]{folder_name}[/]'")
        console.print(f"Size:    [bold green]{formatted_size}[/]")
        if total_skipped_items > 0:
             console.print(f"[yellow]Note:[/yellow]   {total_skipped_items} item(s) inside could not be accessed.")

        new_folder_name = f"{folder_name} [{formatted_size}]"
        new_full_path = parent_dir / new_folder_name

        if len(str(new_full_path)) > 240:
            console.print("\n[yellow]Resulting path would be too long. Cannot propose rename.[/]")
            return

        if new_full_path.exists():
            console.print(f"\n[yellow]Cannot rename:[/yellow] A file or folder named '[cyan]{new_folder_name}[/]' already exists in the parent directory.")
            return

        console.print(f"\n[yellow]Proposed rename:[/yellow] '[cyan]{folder_name}[/]' -> '[bold green]{new_folder_name}[/]'")

        root_confirm = tk.Tk(); root_confirm.withdraw(); root_confirm.attributes('-topmost', True)
        confirm = messagebox.askyesno(
            "Confirm Rename",
            f"Do you want to rename this folder?\n\n"
            f"From: '{folder_name}'\n"
            f"To:   '{new_folder_name}'\n\n"
            f"In directory: {parent_dir}",
            icon='question' )
        root_confirm.destroy()

        if not confirm:
            console.print("[yellow]Rename cancelled by user.[/]")
            return

        console.print("\nAttempting to rename...")
        try:
            selected_folder_path.rename(new_full_path)
            console.print(f"   -> [green]Successfully renamed to '[bold green]{new_folder_name}[/]'[/]")
        except OSError as e:
            console.print(f"   -> [bold red]Error renaming folder:[/bold red] {e}")
        except Exception as e:
            console.print(f"   -> [bold red]An unexpected error occurred during rename:[/bold red] {e}")


    except PermissionError:
        console.print(f"\n[bold red]Error:[/bold red] Permission denied to access the folder: [cyan]{selected_folder_path}[/]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred during analysis:[/bold red] {e}")


def display_menu():
    """Prints the main menu options using Rich Panel."""
    menu_text = (
        "[bold cyan]1.[/] List Sizes of Subfolders in a Directory\n"
        "[bold cyan]2.[/] Rename Multiple Subfolders with Size ([bold yellow]Use Caution![/])\n"
        "[bold cyan]3.[/] Analyze & Rename a Single Selected Folder\n"
        "[bold red]4.[/] Exit"
    )
    console.print(Panel(menu_text, title="[bold magenta]Folder Size Utility Menu[/]", border_style="blue", expand=False))


def main():
    """Runs the main menu loop."""
    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            list_folders_with_sizes()
        elif choice == '2':
            rename_folders_with_size()
        elif choice == '3':
            analyze_and_rename_single_folder()
        elif choice == '4':
            console.print("[bold blue]Exiting program.[/]")
            break
        else:
            console.print("[bold red]Invalid choice.[/] Please enter 1, 2, 3, or 4.")

        console.print("\n[dim]Press Enter to return to the menu...[/]")
        input()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user (Ctrl+C). Exiting.[/]")
    except Exception as e:
        console.print(f"\n[bold red]An critical error occurred:[/]")
        console.print_exception(show_locals=False)
