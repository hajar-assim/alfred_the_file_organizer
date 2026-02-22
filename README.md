# Alfred

Your personal file butler. Automatically organizes files based on rules and learns from your existing folder structure.

## Features

- **Rule-based organization:** Define patterns to automatically sort files
- **AI learning:** Learns from your existing folder structure
- **Dry-run mode:** Preview changes before moving files
- **Watch mode:** Auto-organize files as they appear
- **Smart matching:** Only moves files when confident

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/alfred.git
cd alfred

# Install with pipx (recommended)
brew install pipx
pipx install .

# Or with pip in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

```bash
# Create config file
alfred init

# Teach Alfred your organization patterns (optional)
alfred learn ~/Documents

# Preview changes without moving files
alfred organize ~/Downloads --dry-run

# Organize files
alfred organize ~/Downloads

# Auto-organize new files as they appear
alfred watch ~/Downloads
```

## Configuration

Edit `~/.alfred/config.yaml`:

```yaml
rules:
  - pattern: "*.pdf"
    destination: "~/Documents/PDFs"

  - pattern: "Screenshot*.png"
    destination: "~/Pictures/Screenshots"
    rename: "{date}_screenshot.{ext}"

  - pattern: "*.{zip,tar,gz}"
    destination: "~/Downloads/Archives"

settings:
  use_ai: true
  ai_confidence_threshold: 0.7
  create_folders: true
```

**Rename placeholders:** `{name}`, `{ext}`, `{date}`, `{time}`

## How It Works

1. **Rules first:** Checks patterns in your config file
2. **AI fallback:** If no rule matches, uses learned patterns from `alfred learn`
3. **Confidence threshold:** Only moves files when confident (default 70%)
4. **No match:** Files that don't match stay untouched
