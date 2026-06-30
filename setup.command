#!/bin/bash
# Double-click this file in Finder to set up Palette (you only do this once).
# It creates a private Python environment and installs what Palette needs.

cd "$(dirname "$0")" || exit 1

echo "Setting up Palette in:"
echo "  $(pwd)"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 is not installed."
  echo "   Install it (free) from https://www.python.org/downloads/ then run this again."
  echo
  echo "Press any key to close…"; read -n 1 -s; exit 1
fi

echo "• Creating a private Python environment (.venv)…"
python3 -m venv .venv || { echo "❌ Could not create the environment."; echo "Press any key…"; read -n 1 -s; exit 1; }

echo "• Installing what Palette needs (this can take a minute)…"
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet -r requirements.txt || {
  echo "❌ Install failed — check your internet connection and run this again."
  echo "Press any key…"; read -n 1 -s; exit 1; }

# Make sure the app launcher is runnable (ZIP downloads can drop this bit).
chmod +x "Palette.app/Contents/MacOS/Palette" 2>/dev/null

echo
echo "✅ All set!  Now double-click  Palette.app  to open Palette."
echo "   Tip: once it's open, right-click its Dock icon → Options → Keep in Dock."
echo
echo "You can close this window. Press any key…"; read -n 1 -s
