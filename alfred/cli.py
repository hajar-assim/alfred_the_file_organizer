"""Main CLI interface for Alfred."""

import click
import os
from pathlib import Path
from colorama import init, Fore, Style

from alfred.config import Config
from alfred.watcher import FileWatcher
from alfred.organizer import FileOrganizer
from alfred.learner import FolderLearner

init(autoreset=True)  # Initialize colorama


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Alfred - Your personal file butler.

    Automatically organizes files based on rules and learns from your existing structure.
    """
    pass


@main.command()
def init():
    """Initialize Alfred with a default config file."""
    config = Config()
    config_path = config.init_config()
    click.echo(f"{Fore.GREEN}✓ Alfred initialized!")
    click.echo(f"{Fore.CYAN}Config file created at: {config_path}")
    click.echo(f"\nEdit the config file to customize your organization rules.")
    click.echo(f"Then run: {Fore.YELLOW}alfred watch ~/Downloads")


@main.command()
@click.argument('folder', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Preview changes without moving files')
def watch(folder, dry_run):
    """Watch a folder and auto-organize new files.

    Example: alfred watch ~/Downloads
    """
    folder_path = Path(folder).expanduser().resolve()

    config = Config()
    if not config.config_exists():
        click.echo(f"{Fore.YELLOW}⚠ No config file found. Running in AI-only mode.")
        click.echo(f"{Fore.CYAN}Tip: Run 'alfred init' to create a config with rules.\n")

    organizer = FileOrganizer(config, dry_run=dry_run)
    watcher = FileWatcher(folder_path, organizer)

    mode = "DRY-RUN" if dry_run else "LIVE"
    click.echo(f"{Fore.GREEN}✓ Alfred is watching: {folder_path}")
    click.echo(f"{Fore.YELLOW}Mode: {mode}")
    click.echo(f"{Fore.CYAN}Press Ctrl+C to stop\n")

    try:
        watcher.start()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.GREEN}✓ Alfred stopped watching.")
        watcher.stop()


@main.command()
@click.argument('folder', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Preview changes without moving files')
def organize(folder, dry_run):
    """Organize existing files in a folder.

    Example: alfred organize ~/Downloads --dry-run
    """
    folder_path = Path(folder).expanduser().resolve()

    config = Config()
    if not config.config_exists():
        click.echo(f"{Fore.YELLOW}⚠ No config file found. Running in AI-only mode.")
        click.echo(f"{Fore.CYAN}Tip: Run 'alfred init' to create a config with rules.\n")

    organizer = FileOrganizer(config, dry_run=dry_run)

    mode = "DRY-RUN" if dry_run else "LIVE"
    click.echo(f"{Fore.GREEN}✓ Organizing: {folder_path}")
    click.echo(f"{Fore.YELLOW}Mode: {mode}\n")

    # Get all files in folder (not subdirectories)
    files = [f for f in folder_path.iterdir() if f.is_file()]

    if not files:
        click.echo(f"{Fore.YELLOW}No files to organize.")
        return

    organized_count = 0
    for file_path in files:
        result = organizer.organize_file(file_path)
        if result:
            organized_count += 1

    if dry_run:
        click.echo(f"\n{Fore.GREEN}✓ Would organize {organized_count}/{len(files)} files.")
    else:
        click.echo(f"\n{Fore.GREEN}✓ Organized {organized_count}/{len(files)} files.")


@main.command()
@click.argument('folder', type=click.Path(exists=True))
def learn(folder):
    """Analyze a folder structure to learn organization patterns.

    Example: alfred learn ~/Documents
    """
    folder_path = Path(folder).expanduser().resolve()

    click.echo(f"{Fore.GREEN}✓ Alfred is learning from: {folder_path}")
    click.echo(f"{Fore.CYAN}Analyzing folder structure...\n")

    learner = FolderLearner()
    stats = learner.learn_from_folder(folder_path)

    click.echo(f"{Fore.GREEN}✓ Learning complete!")
    click.echo(f"\n{Fore.CYAN}Statistics:")
    click.echo(f"  Files analyzed: {stats.get('files_analyzed', 0)}")
    click.echo(f"  Folders scanned: {stats.get('folders_scanned', 0)}")
    click.echo(f"  Patterns learned: {stats.get('patterns_learned', 0)}")
    click.echo(f"\n{Fore.YELLOW}Alfred will now use these patterns to organize new files!")


if __name__ == "__main__":
    main()
