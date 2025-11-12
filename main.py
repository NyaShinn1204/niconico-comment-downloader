import requests
from rich.console import Console
from utils import *

print("init s/d")
print(" + Niconico comment downloader")
print(" + Git: https://github.com/NyaShinn1204/niconico-comment-downloader")

print("! Note")
print(" This tool is not use account info. but if not use account info, niconico limited comment count")

console = Console()

web_session = requests.Session()
api_tool = Niconico_Search(web_session)

api_tool.setup_sesson(web_session)
# dev logic
api_tool.setup_cookie("")


with open('search_info.json', encoding="utf-8") as f:
    search_info = json.load(f)

try:
    print("Fetching Comment from json file")
    total_tv, total_comment, total_comment_json = api_tool.export_comment(search_info)
    
    print("COMMENT INFO: ")
    
    print(f" + Hit Channel: {', '.join(total_tv)}")
    print(f" + Total Comment from Niconico: {str(total_comment)}")
    print(f" + Total Comment from local   : {str(len(total_comment_json))}")
    
    tree = api_tool.generate_xml(total_comment_json)
    saved_filename = api_tool.save_xml_to_file(tree)
    print(f" + Exported locate: {saved_filename}")
except:
    console.print_exception(show_locals=True)