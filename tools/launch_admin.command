#!/bin/bash
# Double-click this file on macOS to open the Admin Tool without using Terminal.
# If macOS asks "Are you sure?", click Open.

cd "$(dirname "$0")/.."
python3 tools/admin_gui.py
