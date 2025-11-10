import requests
from rich.console import Console
from utils import *

print("init s/d")
print(" + Niconico comment downloader")
print(" + Git: https://github.com/NyaShinn1204/niconico-comment-downloader")

console = Console()

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

try:
    total_tv, total_comment, total_comment_json = api_tool.export_comment(search_info)
    
    print(f" + Hit Channel: {', '.join(total_tv)}")
    print(f" + Total Comment: {str(total_comment)}")
    
    tree = api_tool.generate_xml(total_comment_json)
    saved_filename = api_tool.save_xml_to_file(tree)
except:
    console.print_exception(show_locals=True)