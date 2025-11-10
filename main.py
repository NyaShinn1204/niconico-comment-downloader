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

total_comment = 0
total_comment_json = []
total_tv = []

total_filter = []

channle_list = api_tool.get_channel_list(search_info)
for single_channel in channle_list:
    
    filter_data, thread_key = api_tool.get_channel_info(single_channel["contentId"])
    single_json = {
        "filter_data": filter_data,
        "thread_key": thread_key
    }
    total_filter.append(single_json)
processed_list = api_tool.process_filter(total_filter)
for i, single_channel in enumerate(channle_list):
    channle_response = api_tool.get_content_channel(processed_list[i])
    for i in channle_response["data"]["globalComments"]:
        total_comment = total_comment + i["count"]
    for i in channle_response["data"]["threads"]:
        for i in i["comments"]:
            total_comment_json.append(i)
    if single_channel["tags"].__contains__("dアニメストア"):
        total_tv.append("dアニメ")
    else:
        total_tv.append("公式")

print(f" + Hit Channel: {', '.join(total_tv)}")
print(f" + Total Comment: {str(total_comment)}")

tree = api_tool.generate_xml(total_comment_json)
saved_filename = api_tool.save_xml_to_file(tree)