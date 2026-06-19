# Discord Favorite GIF Downloader

A small Python script that downloads exported Discord favorite GIFs.

## What does it do?

* Reads the Discord favorites export JSON.
* Downloads each GIF or video source.
* Converts video sources to `.gif` when needed.
* Skips files that have already been downloaded.
* Reports dead links and their percentage of the total collection.
* Automatically runs `extension_consolidator.py` after downloading.
* Saves everything into a `gifs/` folder in the directory where the script is run.

## Requirements

* Python 3.10+
* `requests`
* `ffmpeg` for MP4-to-GIF conversion

Install the Python dependency:

```bash
pip install requests
```

## Getting the JSON export from Discord

Use the snippet from this gist:

https://gist.github.com/Davr1/af6a5806a3bf4b5b7dc18829029b42c2

1. Open Discord in a browser and log in.
2. Open Developer Tools with `Ctrl + Shift + I`.
3. Go to the **Console** tab.
4. Paste the export snippet.
5. If Discord blocks pasting, type `allow pasting` first, then paste again.
6. Run the snippet.

This will download a file named:

```text
discord-favorite-gifs.json
```

## Usage

Put the JSON file next to the downloader script, then run:

```bash
python download_gifs.py discord-favorite-gifs.json
```

The GIFs will automatically be downloaded into:

```text
gifs/
```

## Example Output

```text
Done.

Total entries:      1608
Eligible links:     1608
Downloaded:         1240
Skipped existing:   311
Dead links:         52 (3.23%)
Other failures:     5
```

## Notes

* The script keeps the original order using the `order` field.
* Re-running the script is safe, existing files are skipped automatically.
* Expired Discord CDN links are counted as dead links.
* If a download fails, the script skips that entry and continues.
* `extension_consolidator.py` is automatically executed after downloads complete.
