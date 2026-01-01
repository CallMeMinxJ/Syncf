# File name: cli.py
# Author: Astor.Jiang
# Date created: 2026-01-01 16:05:31
# Date modified: 2026-01-01 16:07:38
# ------
# Copyright (c) 2025 Astor.Jiang
# GoerTek
# All rights reserved.
import argparse
from os.path import realpath
import pathlib
import sys
import os
from rich.jupyter import display
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from datetime import datetime
import inquirer
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
import tarfile

console = Console()
is_frozen = getattr(sys, 'frozen', False)

if is_frozen:
    exe_path = sys.executable
    real_path = os.path.realpath(exe_path)
    root_path = Path(real_path).resolve().parent.parent

else:
    root_path = Path(__file__).resolve().parent.parent

package_dir = Path(root_path / ".files").resolve()



def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0 or unit == 'GB':
            return f"{size_in_bytes:6.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} GB"

def format_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()

    if dt.date() == now.date():
        return dt.strftime("today %H:%M")
    elif dt.date() == now.replace(day=now.day-1).date():
        return dt.strftime("yestday %H:%M")
    elif dt.year == now.year:
        return dt.strftime("%m-%d %H:%M")
    else:
        return dt.strftime("%Y-%m-%d")

def tar_gz_files(files, name, verbose=False):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.tar.gz"

    if not package_dir.exists():
        console.print(f"[red]error: {package_dir} is not exists[/red]")
        package_dir.mkdir(exist_ok=True)
        console.print(f"[green]Created dir {package_dir}[/green]")

    out_file = package_dir / filename

    cwd = Path.cwd()

    # count information
    total_files = 0
    total_size = 0
    skipped_files = []

    try:
        console.print(
            f"[green]start pack [cyan]<{len(files)}> files[/cyan][/green]"
            f"[yellow] to {out_file}[/yellow]"
        )
        if verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Packing...", total=len(files))

                with tarfile.open(out_file, "w:gz") as tar:
                    for file_path in files:
                        full_path = cwd / file_path

                        if file_path.endswith('/'):
                            dir_path = file_path.rstrip('/')
                            full_dir_path = cwd / dir_path

                            if full_dir_path.exists() and full_dir_path.is_dir():
                                try:
                                    tarinfo = tar.gettarinfo(name=str(full_dir_path), arcname=dir_path)
                                    tarinfo.type = tarfile.DIRTYPE
                                    tar.addfile(tarinfo)

                                    if verbose:
                                        progress.console.print(f"  [orange1]Added directory: {dir_path}/[/orange1]")
                                except Exception as e:
                                    skipped_files.append((file_path, str(e)))
                        else:
                            if full_path.exists() and full_path.is_file():
                                try:
                                    tar.add(str(full_path), arcname=file_path, recursive=False)
                                    total_files += 1
                                    total_size += full_path.stat().st_size

                                    if verbose:
                                        size = full_path.stat().st_size
                                        size_str = format_size(size)
                                        progress.console.print(f"  [blue]Added: {file_path} ({size_str})[/blue]")
                                except Exception as e:
                                    skipped_files.append((file_path, str(e)))
                            else:
                                skipped_files.append((file_path, "File not found"))

                        progress.update(task, advance=1)
        else:
            with tarfile.open(out_file, "w:gz") as tar:
                for file_path in files:
                    full_path = cwd / file_path

                    if file_path.endswith('/'):
                        dir_path = file_path.rstrip('/')
                        full_dir_path = cwd / dir_path

                        if full_dir_path.exists() and full_dir_path.is_dir():
                            try:
                                tarinfo = tar.gettarinfo(name=str(full_dir_path), arcname=dir_path)
                                tarinfo.type = tarfile.DIRTYPE
                                tar.addfile(tarinfo)
                            except Exception as e:
                                skipped_files.append((file_path, str(e)))
                    else:
                        if full_path.exists() and full_path.is_file():
                            try:
                                tar.add(str(full_path), arcname=file_path, recursive=False)
                                total_files += 1
                                total_size += full_path.stat().st_size
                            except Exception as e:
                                skipped_files.append((file_path, str(e)))
                        else:
                            skipped_files.append((file_path, "File not found"))

        size_str = format_size(total_size)

        console.print(f"[green]✓ Package complete: {out_file}[/green]")
        console.print(f"[cyan]Packed {total_files} files, total size: {size_str}[/cyan]")

        if skipped_files:
            console.print(f"[yellow]Skipped {len(skipped_files)} items:[/yellow]")
            for file_path, reason in skipped_files[:5]:  # 只显示前5个
                console.print(f"  [orange1]{file_path}: {reason}[/orange1]")
            if len(skipped_files) > 5:
                console.print(f"  [orange1]... and {len(skipped_files) - 5} more[/orange1]")

        return True

    except Exception as e:
        console.print(f"[red]error: fail to package files [cyan]{e}[/cyan][/red]")
        return False


def package_files(filelist, name, verbose=False):

    result_files = []

    if not os.path.exists(filelist):
        console.print(f"[red]error: [cyan]< {filelist} >[/cyan] is not exists")
        return False

    with open(filelist, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    include_rules = []
    exclude_rules = []

    for line in lines:
        if not line or line.startswith("#"):
            continue

        if line.startswith('!'):
            exclude_rules.append(line[1:])
        else:
            include_rules.append(line)

    include_spec = PathSpec.from_lines(
        GitWildMatchPattern, include_rules
    ) if include_rules else None

    if include_spec == None:
        console.print(f"[red]error: include rules is empty")
        return False


    exclude_spec = PathSpec.from_lines(
        GitWildMatchPattern, exclude_rules
    ) if exclude_rules else None

    cwd = Path.cwd()

    all_items = []

    for root, dirs, files in os.walk(cwd):
        root_path = pathlib.Path(root)

        for file in files:
            file_path = root_path / file
            rel_path = file_path.relative_to(cwd)
            all_items.append(str(rel_path))

        for dir_name in dirs:
            dir_path = root_path / dir_name
            rel_path = dir_path.relative_to(cwd)
            all_items.append(str(rel_path) + '/')

    result = []

    for item in all_items:
        matched_include = include_spec.match_file(item)

        matched_exclude = False
        if exclude_spec:
            matched_exclude = exclude_spec.match_file(item)

        if matched_include and not matched_exclude:
            result.append(item)

    if result:
        tar_gz_files(result, name, verbose)
    else:
        console.print(f"[cyan]warnning: have no files matched rules")
        return False

    return True


def show_package_list():


    if not package_dir.exists():
        console.print(f"[red]error: {package_dir} is not exists[/red]")
        package_dir.mkdir(exist_ok=True)
        console.print(f"[green]Created dir {package_dir}[/green]")
        return False

    try:
        tar_files = list(package_dir.glob("*tar.gz"))

        files_count = len(tar_files)

        file_infos = []
        for file in tar_files:
            stat = file.stat()
            file_infos.append({
                'name': file.name,
                'path': str(file),
                'size': stat.st_size,
                'size_formatted': format_size(stat.st_size),
                'mtime': stat.st_mtime,
                'mtime_formatted': format_time(stat.st_mtime),
                'mtim_dt': datetime.fromtimestamp(stat.st_mtime)
            })
        # sort by time
        file_infos.sort(key = lambda x: x['mtime'], reverse = True)

        choices = []
        for index, info in enumerate(file_infos, 1):
            index_str = f"{index:3d}"
            display_text = (
                f"{index_str}. {info['name']} "
                f"({info['size_formatted'].strip()}, {info['mtime_formatted']})"
            )
            choices.append((display_text, info['name']))

        choices.append(("exit", None))

        question = [
            inquirer.List(
                'file',
                message = f"please select file, totol: {files_count}",
                choices = choices,
                carousel = True
            )
        ]

        answers = inquirer.prompt(
            question
        )

        if answers and answers['file'] is not None:
            selected_file = answers['file']
            console.print(f"[green]select package {selected_file}[/green]")
            return selected_file

        return False

    except Exception as e:
        console.print(f"[red]error:{e}")
        return False

def unpackage_files(verbose=False):

    package_name = show_package_list()

    if package_name is None or package_name is False:
        console.print(f"[yellow]you select no files[/yellow]")
        return True

    package_file = package_dir / package_name

    questions = [
        inquirer.Confirm('confirm',
                       message="are you sure unpack to this dir ?",
                       default=True),
    ]

    answers = inquirer.prompt(questions)

    if not answers or not answers['confirm']:
        console.print("[yellow]cancel unpack action[/yellow]")
        return False

    console.print(f"[yellow]Will unpackage the file: {package_file}[/yellow]")

    try:
        if verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                with tarfile.open(package_file, "r:gz") as tar:
                    file_count = len(tar.getmembers())
                    task = progress.add_task("unpacking...", total=file_count)

                    for member in tar:
                        if verbose:
                            if member.isfile():
                                progress.console.print(f"  [blue]unpack: {member.name}[/blue]")
                            else:
                                progress.console.print(f"  [orange1]create dir: {member.name}[/orange1]")

                        tar.extract(member, path=".", set_attrs=False)
                        progress.update(task, advance=1)
        else:
            with tarfile.open(package_file, "r:gz") as tar:
                tar.extractall(path=".")

        console.print(f"[green]✓ unpack finished: {package_file}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]unpack action is failed: {e}[/red]")
        return False

def clean_all_packages(verbose=False):
    if not package_dir.exists():
        console.print(f"[yellow]Package directory '{package_dir}' does not exist.[/yellow]")
        return True

    all_files = list(package_dir.glob("*.tar.gz"))

    if not all_files:
        console.print(
            f"[yellow]have no [/yellow] "
                "[blue].tar.gz[/blue] "
                "[yellow]files need clean.[/yellow]")
        return True

    total_size = sum(f.stat().st_size for f in all_files)
    size_str = format_size(total_size)

    console.print(f"[yellow]Found {len(all_files)} package files (total: {size_str})[/yellow]")

    try:
        if verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[blue]Deleting files...", total=len(all_files))
                deleted_count = 0
                for file_path in all_files:
                    try:
                        file_path.unlink()
                        console.print(f"  [orange1]Deleted: {file_path.name}[/orange1]")
                        deleted_count += 1
                    except Exception as e:
                        console.print(f"  [yellow]Failed to delete {file_path.name}: {e}[/yellow]")
                    progress.update(task, advance=1)
                console.print(f"[green]✓ Deleted {deleted_count} files.[/green]")
        else:
            deleted_count = 0
            for file_path in all_files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    if verbose:
                        console.print(f"[yellow]Failed to delete {file_path.name}: {e}[/yellow]")
            console.print(f"[green]✓ Deleted {deleted_count} files.[/green]")

        return True

    except Exception as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")
        return False

def print_banner():
    banner = """
         ::::::::::  ##::    ::## ##::   ::##  :::::::::: :::::::::::: 
        ::::::::::::  ##::  ::##  ###::  ::## :::::::::::: :::::::::::: 
        ::::::         ########   ####:: ::## ::::::       ::::::       
         ::::::::::     ######    ## ::####:: ::::::       ::::::::::   
             :::::::     ####     ##  ::###:: ::::::       ::::::::::   
        ::::::::::::     ####     ##   ::##:: :::::::::::: ::::::       
         ::::::::::      ####     ##    ::##   :::::::::: ::::::       

    """
    console.print(banner, style="bold cyan")
    return 0

def parse_args():
    parser = argparse.ArgumentParser(
        description = """
            syncf - elegent tool to package
        """,
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-z",
        nargs = 2, metavar = ("filelist", "name"),
        help = "package files by filelist"
    )

    parser.add_argument(
        "-u", action = "store_true",
        help = "unpackage files"
    )

    parser.add_argument(
        "-l", action = "store_true",
        help = "display the list of packages"
    )

    parser.add_argument(
        "-v", action = "store_true",
        help = "display the details of actions"
    )

    parser.add_argument(
        "-c", action = "store_true",
        help = "clean all the packages"
    )


    return parser.parse_args()

def main():

    # get the args
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) == 1:
        print_banner()

    args = parse_args()
    if args.z:
        filelist, name = args.z
        package_files(filelist, name, args.v)
    elif args.u:
        unpackage_files(args.v)
    elif args.l:
        show_package_list()
    elif args.c:
        clean_all_packages(args.v)
    else:
        console.print("use <syncf -h> show helper")

    return 0

if __name__ == "__main__":
    main()

