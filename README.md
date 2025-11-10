<div align="center">
    <strong>NCOverlay to python</strong>
</div>

<div id="top"></div>

## 

<p style="display: inline">
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
</p>

## Table of contents

- [About Repository](#What-this)
- [Requirement](#requirement)
- [How to use](#how-to-use)

## What this

This is a port of the NCOverlay Chrome extension to Python.
You can get almost the same comments 👍

## Requirement

- Content Info
- Python (3.12<=)
- Japan VPN

please check requirements.txt for Python requirements

## How to use

### How to use code?

1. Ensure Python is installed in your system [link](https://www.python.org/downloads/).

2. Download the zip file or run the following command:
   ```bash
   git clone https://github.com/NyaShinn1204/niconico-comment-downloader
   ```

3. Edit `search_info.json`
   Example here:
   ```json
    {
        "series_title": "最後にひとつだけお願いしてもよろしいでしょうか",
        "episode_title": "悪徳貴族（豚野郎達）を思う存分ボコボコにしてスカッとしてもよろしいでしょうか",
        "episode_name": "EPISODE 1",
        "episode_name_count": 1,
        "filter_json": {
            "duration": 1420,
            "targets": {
                "official": true, # include official vod comment
                "danime": true,   # include danime vod comment
                "chapter": true,  # include chapter vod comment
                "szbh": false     # include comment only vod comment
            }
        }
    }
   ```
   
5. Run command:
   ```bash
   python main.py
   ```
   
6. Enjoy comment 👍

## Have you found a problem?

discord: nyanyakko005
<br>
or
<br>
telegmra: skidnyarara

<p align="right">(<a href="#top">Jump Top</a>)</p>
