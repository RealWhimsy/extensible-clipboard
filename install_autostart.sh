#!/bin/bash
#
# Description: This script will add a .desktop file to the autostart config of your x-compatible system.
#
# Note: THE SCRIPT HAS TO BE PLACED INSIDE THE FOLDER OF A BUILT PROJECT, ON THE SAME LEVEL AS THE EXECUTABLE!
#
target_file=~/.config/autostart/extensible_clipboard_autostart.desktop
executable="$(realpath .)"
desktop_contents="
[Desktop Entry]
Encoding=UTF-8
Version=0.9.4
Type=Application
Name=Startup Extensible Clipboard App
Comment=
Exec=sh %s
StartupNotify=false
Terminal=false
Hidden=false
"
printf "$desktop_contents" "$executable" > "$target_file"
chmod +x "$target_file"
