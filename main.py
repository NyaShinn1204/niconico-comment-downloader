import requests
from rich.console import Console
from utils import *

print("init s/d")

consle = Console()

web_session = requests.Session()
api_tool = Niconico_Search(web_session)

api_tool.setup_sesson(web_session)

search_info = {
    "series_title": "最後にひとつだけお願いしてもよろしいでしょうか",
    "episode_title": "悪徳貴族（豚野郎達）を思う存分ボコボコにしてスカッとしてもよろしいでしょうか",
    "episode_name": "EPISODE 1",
    "episode_name_count": 1,
    "filter_json": {
        "duration": 1420,
        "targets": {
            "official": True,
            "danime": True,
            "chapter": True,
            "szbh": False
        }
    }
}


channle_list = api_tool.get_channel_list(search_info)
print(channle_list)