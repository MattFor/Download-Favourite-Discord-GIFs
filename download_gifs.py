from __future__ import annotations

import re
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests


def safe_name(text: str, max_len: int = 80) -> str:
	text = re.sub(r"[^\w.\-]+", "_", text.strip())
	return text[:max_len].strip("_") or "file"


def guess_ext(url: str, src: str, fmt: int | None) -> str:
	for candidate in (src, url):
		path = urlparse(candidate).path.lower()
		if path.endswith(".gif"):
			return ".gif"
		if path.endswith(".mp4"):
			return ".mp4"
		if path.endswith(".webm"):
			return ".webm"
		if path.endswith(".png"):
			return ".png"
		if path.endswith(".jpg") or path.endswith(".jpeg"):
			return ".jpg"

	if fmt == 1:
		return ".gif"
	if fmt == 2:
		return ".mp4"

	return ".bin"


def download_file(url: str, out_path: Path) -> None:
	headers = {
		"User-Agent": "Mozilla/5.0",
		"Referer": url,
	}

	with requests.get(url, headers=headers, stream=True, timeout=60) as r:
		r.raise_for_status()
		with open(out_path, "wb") as f:
			for chunk in r.iter_content(chunk_size=1024 * 256):
				if chunk:
					f.write(chunk)


def mp4_to_gif(mp4_path: Path, gif_path: Path) -> None:
	if shutil.which("ffmpeg") is None:
		raise RuntimeError("ffmpeg is not installed, cannot convert MP4 to GIF.")

	palette = mp4_path.with_suffix(".palette.png")

	try:
		subprocess.run(
			[
				"ffmpeg",
				"-y",
				"-i",
				str(mp4_path),
				"-vf",
				"fps=15,scale=iw:-1:flags=lanczos,palettegen",
				str(palette),
			],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)

		subprocess.run(
			[
				"ffmpeg",
				"-y",
				"-i",
				str(mp4_path),
				"-i",
				str(palette),
				"-lavfi",
				"fps=15,scale=iw:-1:flags=lanczos[x];[x][1:v]paletteuse",
				str(gif_path),
			],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
	finally:
		if palette.exists():
			palette.unlink(missing_ok=True)


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Download Discord GIF favorites into ./gifs"
	)
	parser.add_argument("json_file", help="Path to the JSON file with GIF data")
	args = parser.parse_args()

	json_path = Path(args.json_file).expanduser().resolve()
	if not json_path.is_file():
		print(f"JSON file not found: {json_path}", file=sys.stderr)
		return 1

	out_dir = Path.cwd() / "gifs"
	out_dir.mkdir(parents=True, exist_ok=True)

	with open(json_path, "r", encoding="utf-8") as f:
		data = json.load(f)

	if not isinstance(data, dict):
		print("Expected the JSON root to be an object/dict.", file=sys.stderr)
		return 1

	downloaded = 0
	dead_links = 0
	failed_other = 0
	skipped_existing = 0
	eligible_entries = 0
	total_entries = len(data)

	for i, (page_url, meta) in enumerate(data.items(), start=1):
		if not isinstance(meta, dict):
			print(f"Skipping item {i}: invalid metadata", file=sys.stderr)
			continue

		src = meta.get("src")
		fmt = meta.get("format")
		order = meta.get("order", i)

		if not src:
			print(f"Skipping item {i}: missing src", file=sys.stderr)
			continue

		eligible_entries += 1

		ext = guess_ext(page_url, src, fmt)
		base = f"{int(order):06d}_{safe_name(urlparse(page_url).path.split('/')[-1] or 'gif')}"

		if ext == ".mp4":
			final_path = out_dir / f"{base}.gif"
			temp_path = out_dir / f"{base}.mp4"

			if final_path.exists():
				skipped_existing += 1
				print(f"Skipping existing: {final_path.name}")
				continue

			try:
				print(f"Downloading {i}/{total_entries}: {src}")
				download_file(src, temp_path)
				mp4_to_gif(temp_path, final_path)
				downloaded += 1
				print(f"Saved: {final_path.name}")
			except requests.RequestException as e:
				dead_links += 1
				print(f"Dead link: {src} ({e})", file=sys.stderr)
			except Exception as e:
				failed_other += 1
				print(f"Failed for {src}: {e}", file=sys.stderr)
			finally:
				if temp_path.exists():
					temp_path.unlink(missing_ok=True)

		else:
			final_path = out_dir / f"{base}{ext}"

			if final_path.exists():
				skipped_existing += 1
				print(f"Skipping existing: {final_path.name}")
				continue

			try:
				print(f"Downloading {i}/{total_entries}: {src}")
				download_file(src, final_path)
				downloaded += 1
				print(f"Saved: {final_path.name}")
			except requests.RequestException as e:
				dead_links += 1
				print(f"Dead link: {src} ({e})", file=sys.stderr)
			except Exception as e:
				failed_other += 1
				print(f"Failed for {src}: {e}", file=sys.stderr)

	print("\nDone.")

	consolidator = Path(__file__).parent / "extension_consolidator.py"

	if consolidator.exists():
		print("\nRunning consolidator...")
		result = subprocess.run([sys.executable, str(consolidator)])

		if result.returncode == 0:
			print("Consolidation completed successfully.")
		else:
			print(
				f"Consolidation exited with code {result.returncode}",
				file=sys.stderr,
			)
	else:
		print("extension_consolidator.py not found, skipping.")

	dead_percentage = (dead_links / eligible_entries * 100) if eligible_entries else 0.0

	print(f"Total entries:      {total_entries}")
	print(f"Eligible links:     {eligible_entries}")
	print(f"Downloaded:         {downloaded}")
	print(f"Skipped existing:    {skipped_existing}")
	print(f"Dead links:         {dead_links} ({dead_percentage:.3f}%)")
	if failed_other:
		print(f"Other failures:      {failed_other}")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
