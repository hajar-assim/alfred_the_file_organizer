"""File organization logic for Alfred."""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import fnmatch
import re
from colorama import Fore

from alfred.config import Config
from alfred.learner import FolderLearner


class FileOrganizer:
    """Handles file organization based on rules and AI predictions."""

    def __init__(self, config: Config, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.learner = FolderLearner()
        self.settings = config.get_settings()

    def organize_file(self, file_path: Path) -> bool:
        """Organize a single file based on rules or AI prediction.

        Returns True if file was organized, False otherwise.
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        # First try rule-based organization
        destination = self._match_rules(file_path)

        # If no rule matches and AI is enabled, try AI prediction
        if not destination and self.settings.get('use_ai', True):
            prediction = self.learner.predict_destination(file_path)
            if prediction:
                confidence = prediction.get('confidence', 0)
                threshold = self.settings.get('ai_confidence_threshold', 0.7)

                if confidence >= threshold:
                    destination = prediction.get('destination')
                    print(f"{Fore.CYAN}  [AI] Confidence: {confidence:.0%}")

        if not destination:
            print(f"{Fore.YELLOW}  ⊘ No rule or prediction for: {file_path.name}")
            return False

        # Move the file
        return self._move_file(file_path, destination)

    def _match_rules(self, file_path: Path) -> Optional[Dict]:
        """Match file against configured rules.

        Returns destination info if match found, None otherwise.
        """
        rules = self.config.get_rules()

        # Handle empty or None rules
        if not rules:
            return None

        for rule in rules:
            pattern = rule.get('pattern')
            if not pattern:
                continue

            # Handle patterns like "*.{zip,tar,gz}"
            if self._matches_pattern(file_path.name, pattern):
                destination = Path(rule.get('destination')).expanduser()
                rename_pattern = rule.get('rename')

                return {
                    'folder': destination,
                    'rename': rename_pattern,
                    'rule': rule.get('description', pattern)
                }

        return None

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern (supports glob and brace expansion)."""
        # Handle brace expansion like "*.{zip,tar,gz}"
        if '{' in pattern and '}' in pattern:
            # Extract extensions from pattern
            match = re.search(r'\{([^}]+)\}', pattern)
            if match:
                extensions = match.group(1).split(',')
                base_pattern = pattern[:pattern.index('{')]

                for ext in extensions:
                    expanded_pattern = base_pattern + ext.strip()
                    if fnmatch.fnmatch(filename, expanded_pattern):
                        return True
                return False

        # Regular glob matching
        return fnmatch.fnmatch(filename, pattern)

    def _move_file(self, file_path: Path, destination: Dict) -> bool:
        """Move file to destination folder.

        Args:
            file_path: Source file path
            destination: Dict with 'folder', optional 'rename', optional 'rule'

        Returns:
            True if moved successfully, False otherwise
        """
        dest_folder = destination.get('folder')
        rename_pattern = destination.get('rename')
        rule_name = destination.get('rule', 'AI prediction')

        # Create destination folder if needed
        if self.settings.get('create_folders', True):
            if not self.dry_run:
                dest_folder.mkdir(parents=True, exist_ok=True)

        # Determine final filename
        if rename_pattern:
            new_name = self._apply_rename_pattern(file_path, rename_pattern)
        else:
            new_name = file_path.name

        dest_path = dest_folder / new_name

        # Handle duplicates
        if dest_path.exists():
            dest_path = self._get_unique_path(dest_path)

        # Move the file
        action = "Would move" if self.dry_run else "Moving"
        print(f"{Fore.GREEN}  ✓ {action}: {file_path.name}")
        print(f"{Fore.CYAN}    → {dest_path}")
        print(f"{Fore.YELLOW}    Rule: {rule_name}")

        if not self.dry_run:
            try:
                shutil.move(str(file_path), str(dest_path))
                return True
            except Exception as e:
                print(f"{Fore.RED}    ✗ Error: {e}")
                return False

        return True

    def _apply_rename_pattern(self, file_path: Path, pattern: str) -> str:
        """Apply rename pattern to filename.

        Supported placeholders:
        - {name}: original filename without extension
        - {ext}: file extension
        - {date}: current date (YYYY-MM-DD)
        - {time}: current time (HH-MM-SS)
        """
        now = datetime.now()

        replacements = {
            '{name}': file_path.stem,
            '{ext}': file_path.suffix.lstrip('.'),
            '{date}': now.strftime('%Y-%m-%d'),
            '{time}': now.strftime('%H-%M-%S'),
        }

        result = pattern
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        return result

    def _get_unique_path(self, path: Path) -> Path:
        """Generate unique path if file already exists."""
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
