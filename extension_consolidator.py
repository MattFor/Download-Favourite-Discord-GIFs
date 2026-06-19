import re

from pathlib import Path

GIF_DIR = Path("gifs")

if not GIF_DIR.exists():
	print("gifs directory not found")
	raise SystemExit(1)

count = 0

for path in GIF_DIR.rglob("*"):
	if not path.is_file():
		continue

	new_name = re.sub(r'(\.gif)+$', '.gif', path.name, flags=re.IGNORECASE)

	if new_name != path.name:
		new_path = path.with_name(new_name)

		if new_path.exists():
			print(f"Skipping (target exists): {path} -> {new_path}")
			continue

		path.rename(new_path)
		count += 1
		print(f"Renamed: {path.name} -> {new_name}")

print(f"\nFixed {count} file(s).")
