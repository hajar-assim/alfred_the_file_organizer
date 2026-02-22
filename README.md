# Is this you?
<img width="748" height="797" alt="image" src="https://github.com/user-attachments/assets/4a8085d6-54f7-4385-bc6d-b39b80441488" />
If you're like me you probably have an insanely messy file system with screenshots, random downloads, lecture notes etc. Well sure, this is fine at most times, but what about when you're trying to submit your assignment at 11:57 with a minute and 15 seconds on the clock to find your file and you are absolutely a mess of stress and CANNOT find the file you're supposed to submit? 11:59 hits and boom, you refresh. The file submission drop-box is locked, and you officially got a fat 0. Well yes, you could have better time management skills and do that boring ass assignment earlier, but why when you could just have a sexy file-system that makes it super easy to locate anything your looking for?

Don't you want your files to look beautiful like mine??
<img width="898" height="272" alt="image" src="https://github.com/user-attachments/assets/cf63164e-ef0e-43e9-b857-5f47cfcf3668" />


# Alfred

In comes your personal file butler, Alfred (yes I'm 22 and still watch Batman). Alfred automatically organizes files based on rules and learns from your existing folder structure, so no more sitting for hours dragging and dropping and organizing, only for you to stop the next day and have it turn into disarray in a couple months.

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
