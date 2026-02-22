"""File system watcher for Alfred."""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from colorama import Fore

from alfred.organizer import FileOrganizer


class FileOrganizerHandler(FileSystemEventHandler):
    """Handles file system events and triggers organization."""

    def __init__(self, organizer: FileOrganizer):
        self.organizer = organizer

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Small delay to ensure file is fully written
        time.sleep(0.5)

        if file_path.exists():
            print(f"\n{Fore.MAGENTA}New file detected: {file_path.name}")
            self.organizer.organize_file(file_path)


class FileWatcher:
    """Watches a folder and organizes new files."""

    def __init__(self, watch_path: Path, organizer: FileOrganizer):
        self.watch_path = watch_path
        self.organizer = organizer
        self.observer = Observer()

    def start(self):
        """Start watching the folder."""
        event_handler = FileOrganizerHandler(self.organizer)
        self.observer.schedule(event_handler, str(self.watch_path), recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop watching the folder."""
        self.observer.stop()
        self.observer.join()
