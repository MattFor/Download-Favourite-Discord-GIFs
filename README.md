# Discord Favorite GIF Downloader

A small Python script that downloads exported Discord favorite GIFs.

## What it does

* Reads the Discord favorites export JSON.
* Downloads each GIF or video source.
* Converts video sources to `.gif` when needed.
* Saves everything into `/gifs` from the root where you run the script.

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

[https://gist.github.com/Davr1/af6a5806a3bf4b5b7dc18829029b42c2](https://gist.github.com/Davr1/af6a5806a3bf4b5b7dc18829029b42c2)

1. Open Discord in a browser and log in.
2. Open Developer Tools with `Ctrl + Shift + I`.
3. Go to the **Console** tab.
4. Paste the export snippet.
5. If Discord blocks pasting, type `allow pasting` first, then paste again.
6. Run the snippet.

This will download a file named `discord-favorite-gifs.json`.

## Usage

Put the JSON file next to the downloader script, then run:

```bash
python download_gifs.py discord-favorite-gifs.json
```

After that you the gifs will automatically start downloading to the created `/gifs` directiory.

## Notes

* The script keeps the original order using the `order` field.
* If a download fails, the script skips that entry and continues.
* 