"""Configuration management for Alfred."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


class Config:
    """Manages Alfred's configuration file."""

    DEFAULT_CONFIG = {
        'rules': [
            {
                'pattern': '*.pdf',
                'destination': '~/Documents/PDFs',
                'description': 'PDF documents'
            },
            {
                'pattern': 'Screenshot*.png',
                'destination': '~/Pictures/Screenshots',
                'rename': '{date}_screenshot.{ext}',
                'description': 'Screenshots'
            },
            {
                'pattern': '*.{zip,tar,gz,rar}',
                'destination': '~/Downloads/Archives',
                'description': 'Compressed files'
            },
            {
                'pattern': '*.{jpg,jpeg,png,gif,heic}',
                'destination': '~/Pictures/Unsorted',
                'description': 'Images'
            },
            {
                'pattern': '*.{mp4,mov,avi,mkv}',
                'destination': '~/Movies/Unsorted',
                'description': 'Videos'
            },
            {
                'pattern': '*.{doc,docx,txt,rtf}',
                'destination': '~/Documents/Text',
                'description': 'Text documents'
            },
        ],
        'settings': {
            'use_ai': True,
            'ai_confidence_threshold': 0.7,
            'create_folders': True,
            'log_actions': True,
        }
    }

    def __init__(self):
        self.config_dir = Path.home() / '.alfred'
        self.config_path = self.config_dir / 'config.yaml'
        self.data_dir = self.config_dir / 'data'
        self.config = None

    def config_exists(self) -> bool:
        """Check if config file exists."""
        return self.config_path.exists()

    def init_config(self) -> Path:
        """Initialize config directory and file with defaults."""
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        with open(self.config_path, 'w') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)

        return self.config_path

    def load(self) -> Dict:
        """Load configuration from file. Returns empty config if file doesn't exist."""
        if not self.config_exists():
            # Return minimal config with AI enabled
            self.config = {
                'rules': [],
                'settings': {
                    'use_ai': True,
                    'ai_confidence_threshold': 0.7,
                    'create_folders': True,
                    'log_actions': True,
                }
            }
            return self.config

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        return self.config

    def get_rules(self) -> List[Dict]:
        """Get organization rules."""
        if not self.config:
            self.load()
        rules = self.config.get('rules', [])
        # Handle None case (when YAML has "rules:" with no value)
        return rules if rules is not None else []

    def get_settings(self) -> Dict:
        """Get settings."""
        if not self.config:
            self.load()
        return self.config.get('settings', {})

    def get_data_dir(self) -> Path:
        """Get data directory path."""
        return self.data_dir
