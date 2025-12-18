import os
from pathlib import Path

import sys

# Project Base Directory
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Running from source
    BASE_DIR = Path(__file__).resolve().parent.parent

# Files
API_KEYS_FILE = BASE_DIR / "api_keys.json"

# Defaults
DEFAULT_KEYWORDS = ["CAT", "CUTE"]
DEFAULT_DAYS = 30
DEFAULT_MAX_PAGES = 5
DEFAULT_LIMIT_PER_KEYWORD = 50
DEFAULT_MIN_VIEWS = 100000
DEFAULT_MAX_DURATION = 60  # Seconds

# UI Settings
WINDOW_TITLE = "YouTube Shorts 爆款搜索神器"
WINDOW_SIZE = (1200, 800)
SPLIT_RATIO = [300, 900]  # Width ratio 3:7 approx

APP_VERSION = "20251218v.1"

# Support URLs
DONATE_URL = "https://ko-fi.com/guanda_ai_studio"
CHANNEL_URL = "https://www.youtube.com/@GuanDaAIStudio"
