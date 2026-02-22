#!/bin/bash

# Test script for Alfred
# This demonstrates Alfred's capabilities step by step

set -e  # Exit on error

echo "===================================="
echo "🤵 Testing Alfred - Your File Butler"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ALFRED="./venv/bin/alfred"

# Step 1: Initialize
echo -e "${BLUE}Step 1: Initializing Alfred...${NC}"
$ALFRED init
echo ""

# Step 2: Learn from existing structure
echo -e "${BLUE}Step 2: Teaching Alfred your organization style...${NC}"
echo "Learning from test_env/Documents..."
$ALFRED learn test_env/Documents
echo ""

# Step 3: Show what we have to organize
echo -e "${BLUE}Step 3: Files waiting in Downloads:${NC}"
ls -1 test_env/Downloads/
echo ""

# Step 4: Dry run
echo -e "${BLUE}Step 4: Running dry-run to preview...${NC}"
$ALFRED organize test_env/Downloads --dry-run
echo ""

# Step 5: Ask user if they want to proceed
echo -e "${YELLOW}Ready to organize for real?${NC}"
echo "Press Enter to continue, or Ctrl+C to cancel..."
read

# Step 6: Organize for real
echo -e "${BLUE}Step 5: Organizing files...${NC}"
$ALFRED organize test_env/Downloads
echo ""

# Step 7: Show results
echo -e "${GREEN}✓ Done! Let's see where everything went:${NC}"
echo ""
echo "Finance folder:"
ls -1 test_env/Documents/Finance/ 2>/dev/null || echo "  (empty)"
echo ""
echo "Career folder:"
ls -1 test_env/Documents/Career/ 2>/dev/null || echo "  (empty)"
echo ""
echo "School folder:"
ls -1 test_env/Documents/School/ 2>/dev/null || echo "  (empty)"
echo ""
echo "Screenshots folder:"
ls -1 test_env/Pictures/Screenshots/ 2>/dev/null || echo "  (empty)"
echo ""
echo "Downloads folder (should be mostly empty):"
ls -1 test_env/Downloads/ 2>/dev/null || echo "  (empty)"
echo ""

echo -e "${GREEN}===================================="
echo "🎉 Alfred test complete!"
echo "====================================${NC}"
