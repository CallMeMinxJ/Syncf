#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py - Syncf Installation Script
Setup symlink and configure environment variables
"""

import os
import sys
import argparse
from pathlib import Path
import stat
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

def get_current_dir() -> Path:
    """Get current working directory reliably"""
    # 如果是打包的可执行文件
    if getattr(sys, 'frozen', False):
        # 通过 sys.executable 获取可执行文件路径
        exe_path = Path(sys.executable).resolve()
        # 返回可执行文件所在的目录
        return exe_path.parent
    else:
        # 如果是源代码运行，返回脚本所在目录
        return Path(__file__).parent.resolve()

def get_binary_path() -> Path:
    """Get syncf binary file path"""
    current_dir = get_current_dir()
    binary_path = current_dir / "bin" / "syncf"
    
    if not binary_path.exists():
        console.print(f"[red]✗ Binary not found: {binary_path}[/red]")
        console.print("\n[yellow]Please ensure you have built syncf:[/yellow]")
        console.print("[cyan]  pyinstaller --onefile src/cli.py --name syncf -i NONE[/cyan]")
        console.print("[cyan]  mv dist/syncf bin/[/cyan]")
        sys.exit(1)
    
    return binary_path

def get_home_dir() -> Path:
    """Get user home directory"""
    return Path.home()

def get_shell_type() -> str:
    """Detect shell type"""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    elif "fish" in shell:
        return "fish"
    return "unknown"

def get_shell_config() -> Path:
    """Get shell configuration file path"""
    home = get_home_dir()
    shell = get_shell_type()
    
    config_map = {
        "bash": [".bashrc", ".bash_profile", ".profile"],
        "zsh": [".zshrc"],
        "fish": [".config/fish/config.fish"],
    }
    
    configs = config_map.get(shell, [".bashrc", ".zshrc"])
    for config in configs:
        config_path = home / config
        if config_path.exists():
            return config_path
    
    # Return default if none exist
    return home / configs[0]

def setup_directories() -> Path:
    """Create necessary directories"""
    shell_bin = get_home_dir() / ".shell.bin"
    
    if not shell_bin.exists():
        shell_bin.mkdir(parents=True, exist_ok=True)
        os.chmod(shell_bin, stat.S_IRWXU)
        console.print(f"[green]✓ Created directory: {shell_bin}[/green]")
    else:
        console.print(f"[cyan]✓ Directory exists: {shell_bin}[/cyan]")
    
    return shell_bin

def create_shell_conf() -> Path:
    """Create or update .shell.conf file"""
    shell_conf = get_home_dir() / ".shell.conf"
    
    if not shell_conf.exists():
        content = """#!/bin/bash
# User shell configuration
# Add custom binaries to PATH

export SHELL_BIN_DIR="$HOME/.shell.bin"
if [ -d "$SHELL_BIN_DIR" ]; then
    export PATH="$SHELL_BIN_DIR:$PATH"
fi

# Add your custom configurations below
"""
        shell_conf.write_text(content)
        shell_conf.chmod(0o755)
        console.print(f"[green]✓ Created config: {shell_conf}[/green]")
    else:
        console.print(f"[cyan]✓ Config exists: {shell_conf}[/cyan]")
    
    return shell_conf

def setup_symlink(binary_path: Path, target_dir: Path) -> bool:
    """Create symlink in target directory"""
    target = target_dir / "syncf"
    
    if target.exists():
        if target.is_symlink():
            if target.resolve() == binary_path:
                console.print(f"[cyan]✓ Symlink exists: {target} → {binary_path}[/cyan]")
                return True
            else:
                console.print(f"[yellow]⚠  Overwriting symlink: {target}[/yellow]")
                target.unlink()
        else:
            console.print(f"[yellow]⚠  File exists, overwriting: {target}[/yellow]")
            target.unlink()
    
    try:
        target.symlink_to(binary_path)
        console.print(f"[green]✓ Created symlink: {target} → {binary_path}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Failed to create symlink: {e}[/red]")
        return False

def check_path_inclusion(target_dir: Path) -> bool:
    """Check if target directory is in PATH"""
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    target_str = str(target_dir)
    return any(path_dir == target_str for path_dir in path_dirs)

def ensure_source_in_config(shell_conf: Path, shell_config: Path) -> bool:
    """Ensure shell.conf is sourced in shell config file"""
    source_line = f'\nsource "{shell_conf}"\n'
    
    if not shell_config.exists():
        shell_config.touch()
    
    content = shell_config.read_text()
    
    if source_line.strip() in content or f"source {shell_conf}" in content:
        console.print(f"[cyan]✓ Already sourced in {shell_config.name}[/cyan]")
        return False
    
    with open(shell_config, "a") as f:
        f.write(f"\n# Source user shell configuration\n{source_line}")
    
    console.print(f"[green]✓ Added to {shell_config.name}[/green]")
    return True

def print_instructions(shell_bin: Path, shell_conf: Path, shell_config: Path):
    """Print post-installation instructions"""
    shell = get_shell_type()
    
    table = Table(box=box.ROUNDED, show_header=False, title="🎯 Installation Summary")
    table.add_column("Item", style="cyan")
    table.add_column("Path", style="white")
    
    table.add_row("Binary Directory", str(shell_bin))
    table.add_row("Shell Config", str(shell_conf))
    table.add_row("Shell Profile", str(shell_config))
    
    console.print(table)
    
    if not check_path_inclusion(shell_bin):
        panel = Panel(
            f"""🔧 Manual Configuration Required:

1. Add this to your {shell_config.name}:
   [blue]if [ -d "$HOME/.shell.bin" ]; then[/blue]
   [blue]    export PATH="$HOME/.shell.bin:$PATH"[/blue]
   [blue]fi[/blue]

2. Reload your shell configuration:
   [green]source {shell_config}[/green]

3. Verify installation:
   [cyan]syncf --help[/cyan]""",
            title="⚠️  Setup Required",
            border_style="yellow"
        )
        console.print(panel)
    else:
        console.print("[green]🎉 Setup completed successfully![/green]")
        console.print(f"\n[cyan]▶ Try: syncf --help[/cyan]")

def uninstall(shell_bin: Path):
    """Remove symlink and clean up"""
    target = shell_bin / "syncf"
    
    if target.exists() and target.is_symlink():
        target.unlink()
        console.print(f"[green]✓ Removed symlink: {target}[/green]")
        
        # Check if directory is empty
        if not any(shell_bin.iterdir()):
            shell_bin.rmdir()
            console.print(f"[cyan]✓ Removed empty directory: {shell_bin}[/cyan]")
    else:
        console.print("[cyan]✓ Symlink not found[/cyan]")
    
    console.print("\n[green]🗑️  Uninstallation complete![/green]")
    console.print("[yellow]Note: You may need to remove PATH configuration manually[/yellow]")

def setup(uninstall_flag: bool = False):
    """Main setup function"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Setting up...", total=6)
        
        if not uninstall_flag:
            # Installation flow
            console.print("\n[blue]🚀 Starting Syncf Installation[/blue]")
            
            # 1. Find binary
            binary_path = get_binary_path()
            console.print(f"[green]✓ Found binary: {binary_path}[/green]")
            progress.update(task, advance=1)
            
            # 2. Setup directories
            shell_bin = setup_directories()
            progress.update(task, advance=1)
            
            # 3. Create shell config
            shell_conf = create_shell_conf()
            progress.update(task, advance=1)
            
            # 4. Create symlink
            if not setup_symlink(binary_path, shell_bin):
                sys.exit(1)
            progress.update(task, advance=1)
            
            # 5. Update shell config
            shell_config = get_shell_config()
            ensure_source_in_config(shell_conf, shell_config)
            progress.update(task, advance=1)
            
            # 6. Print instructions
            print_instructions(shell_bin, shell_conf, shell_config)
            progress.update(task, advance=1)
            
        else:
            # Uninstallation flow
            console.print("\n[blue]🗑️  Starting Syncf Uninstallation[/blue]")
            shell_bin = get_home_dir() / ".shell.bin"
            uninstall(shell_bin)
            progress.update(task, completed=6)

def main():
    parser = argparse.ArgumentParser(
        description="Syncf Installation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--uninstall", "-u",
        action="store_true",
        help="Uninstall Syncf"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information"
    )
    
    # Print banner
    banner = """
         ::::::::::  ##::    ::## ##::   ::##  :::::::::: :::::::::::: 
        ::::::::::::  ##::  ::##  ###::  ::## :::::::::::: :::::::::::: 
        ::::::         ########   ####:: ::## ::::::       ::::::       
         ::::::::::     ######    ## ::####:: ::::::       ::::::::::   
             :::::::     ####     ##  ::###:: ::::::       ::::::::::   
        ::::::::::::     ####     ##   ::##:: :::::::::::: ::::::       
         ::::::::::      ####     ##    ::##   :::::::::: ::::::       
    """
    
    console.print(Panel(banner, title="Syncf Setup", border_style="blue"))
    
    args = parser.parse_args()
    
    if args.version:
        console.print("[cyan]Syncf Setup v1.0.0[/cyan]")
        return
    
    try:
        setup(args.uninstall)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠  Installation cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Setup failed: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
