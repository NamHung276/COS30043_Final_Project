import importlib
import os
from pathlib import Path

os.chdir(Path(r"c:\Users\hungt\Documents\GitHub\COS30043_Final_Project").resolve())
os.environ.pop('RAWG_API_KEY', None)
os.environ.pop('NEWS_API_KEY', None)
os.environ['VITE_RAWG_API_KEY'] = 'rawg-test-key'
os.environ['VITE_NEWS_API_KEY'] = 'news-test-key'

import backend.config as config
importlib.reload(config)
print('rawg from settings', config.settings.rawg_api_key)
print('news from settings', config.settings.news_api_key)
print('init values', config.Settings().rawg_api_key, config.Settings().news_api_key)
