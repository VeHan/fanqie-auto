@echo off

RMDIR /S "build"
RMDIR /S "dist"
pyinstaller "-F" "-w" "--onefile" "main.py"
COPY  "420ab.js" "dist/"
COPY  "config.json" "dist/"