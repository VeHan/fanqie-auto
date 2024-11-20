@echo off

RMDIR /S "build"
RMDIR /S "dist"
pyinstaller "-F" "-c" "--onefile" "main.py"
COPY  "420ab.js" "dist/"
COPY  "config.json" "dist/"