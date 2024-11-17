rm -rf build
rm -rf dist
pyinstaller -F -w --onefile  main.py
cp 420ab.js dist/
cp config.json dist/
