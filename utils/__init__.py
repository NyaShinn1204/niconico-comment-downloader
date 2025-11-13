import os
import copy
import time
import json
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

class Niconico_Search:
    def __init__(self, session):
        self.session = session
        self.logined_ac = False
    def setup_sesson(self):
        self.session.headers.update({
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cache-control": "no-cache",
            "cookie": "lang=ja-jp; area=JP",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "sec-fetch-storage-access": "active",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        })
    def setup_cookie(self, cookie_text):
        if cookie_text != "":
            self.logined_ac = True
    
            self.session.headers.update({
                "cookie": cookie_text
            })

    def convert_kanji(self, num: int):
        kanji_units = ['', '十', '百', '千']
        kanji_large_units = ['', '万', '億', '兆', '京']
        kanji_digits = '零一二三四五六七八九'
            
        if num == 0:
            return kanji_digits[0]
            
        result = ''
        str_num = str(num)
        length = len(str_num)
            
        for i, digit in enumerate(str_num):
            if digit != '0':
                result += kanji_digits[int(digit)] + kanji_units[(length - i - 1) % 4]
            if (length - i - 1) % 4 == 0:
                result += kanji_large_units[(length - i - 1) // 4]
            
        result = result.replace('一十', '十')  # 「一十」は「十」に置き換え、バグ対策
        return result

    def gen_episode_name_list(self, video_info):
        name_list = []
        episode_count = video_info["episode_name_count"]
        name_list.append(video_info["series_title"]+" "+str(episode_count)+"話")
        name_list.append(str(episode_count)+"話")
        name_list.append(self.convert_kanji(episode_count)+"話")
        name_list.append("第"+str(episode_count)+"話")
        name_list.append("エピソード"+str(episode_count))
        name_list.append("episode"+str(episode_count))
        name_list.append("episode"+str(episode_count).zfill(2))
        name_list.append("EPISODE "+str(episode_count))
        name_list.append("EPISODE "+str(episode_count).zfill(2))
        name_list.append("ep"+str(episode_count))
        name_list.append("ep"+str(episode_count).zfill(2))
        name_list.append("#"+str(episode_count))
        name_list.append("#"+str(episode_count).zfill(2))
        name_list.append('"'+video_info["episode_name"]+'"')
        name_list.append('"'+video_info["episode_title"]+'"')
        return " OR ".join(name_list)

    def Ys(self, e):
        duration = e.get("duration")
        targets = e.get("targets", {})

        if not (targets.get("official") or targets.get("danime")):
            return None

        filters = [{"type": "equal", "field": "genre.keyword", "value": "アニメ"}]
        if duration:
            filters.append({
                "type": "range",
                "field": "lengthSeconds",
                "from": duration - 15,
                "to": duration + 15,
                "include_lower": True,
                "include_upper": True
            })
        return {"type": "and", "filters": filters} if len(filters) > 1 else filters[0]
    def Qs(self, e):
        duration = e.get("duration")
        targets = e.get("targets", {})

        if not targets.get("szbh"):
            return None

        filters = [{
            "type": "or",
            "filters": [
                {"type": "equal", "field": "tagsExact", "value": "コメント専用動画"},
                {"type": "equal", "field": "tagsExact", "value": "SZBH方式"}
            ]
        }]
        if duration:
            filters.append({
                "type": "range",
                "field": "lengthSeconds",
                "from": duration - 5,
                "to": duration + 65,
                "include_lower": True,
                "include_upper": True
            })
        return {"type": "and", "filters": filters} if len(filters) > 1 else filters[0]
    def Ds(self, e):
        targets = e.get("targets", {})
        if not targets.get("chapter"):
            return None

        return {
            "type": "and",
            "filters": [
                {"type": "equal", "field": "genre.keyword", "value": "アニメ"},
                {"type": "equal", "field": "tagsExact", "value": "dアニメストア"}
            ]
        }
    def gen_filter_list(self, video_info):
        e = video_info["filter_json"]
        filters = [self.Ys(e), self.Qs(e), self.Ds(e)]

        filters = [f for f in filters if f is not None]

        if len(filters) > 1:
            return {"type": "or", "filters": filters}
        elif len(filters) == 1:
            return filters[0]
        else:
            return None
    def gen_filter_list_simple(self, video_info):
        def make_anime_length_filter(from_value, to_value):
            return {
                "type": "and",
                "filters": [
                    {
                        "type": "equal",
                        "field": "genre.keyword",
                        "value": "アニメ"
                    },
                    {
                        "type": "range",
                        "field": "lengthSeconds",
                        "from": from_value,
                        "to": to_value,
                        "include_lower": True,
                        "include_upper": True
                    }
                ]
            }
        duration = video_info["filter_json"]["duration"]
        margin = 15
        return make_anime_length_filter(duration - margin, duration + margin)

    def get_channel_list(self, video_info):
        _Q = self.gen_episode_name_list(video_info)

        _F = json.dumps(self.gen_filter_list(video_info), ensure_ascii=False, separators=(",", ":"))

        payload_b1 = {
            "q": _Q,
            "_sort": "-startTime",
            "_context": "Yoimi V2/NCOverlay_3.26.8",
            "targets": "title",
            "fields": "contentId,title,userId,channelId,viewCounter,lengthSeconds,thumbnailUrl,startTime,commentCounter,categoryTags,tags",
            "jsonFilter": _F,
            "_limit": 50
        }
        _PAYLOAD = urllib.parse.urlencode(payload_b1, quote_via=urllib.parse.quote, safe="")
        response = self.session.get("https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search?"+_PAYLOAD).json()
        if len(response["data"]) == 0:
            _Q = self.gen_episode_name_list(video_info)

            _F = json.dumps(self.gen_filter_list_simple(video_info), ensure_ascii=False, separators=(",", ":"))

            payload_b1 = {
                "q": _Q,
                "_sort": "-startTime",
                "_context": "Yoimi V2/NCOverlay_3.26.8",
                "targets": "title",
                "fields": "contentId,title,userId,channelId,viewCounter,lengthSeconds,thumbnailUrl,startTime,commentCounter,categoryTags,tags",
                "jsonFilter": _F,
                "_limit": 50
            }
            response = self.session.get("https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search?"+_PAYLOAD).json()
            return response["data"]
        else:
            return response["data"]
    def get_channel_info(self, channelid):
        response = self.session.get(f"https://www.nicovideo.jp/watch/{channelid}?responseType=json").json()
        filtered_data = [
            {"id": str(item["id"]), "fork": item["forkLabel"]}
            for item in response["data"]["response"]["comment"]["threads"] if item["label"] != "easy"
        ]
        thread_key = response["data"]["response"]["comment"]["nvComment"]["threadKey"]

        return filtered_data, thread_key
    def get_content_channel(self, channel_info, date_time=int(time.time())):
        filtered_data = channel_info["filter_data"]
        thread_key    = channel_info["thread_key"]
        payload = {
            "params": {
                "targets": filtered_data,
                "language": "ja-jp"
            },
            "threadKey": thread_key,
        }
        if self.logined_ac:
            payload["additionals"] = {
                "when": date_time,
                "res_from": -1000
            }
        headers = {
            "X-Frontend-Id": "6",
            "X-Frontend-Version": "0",
            "X-Client-Os-Type": "others",
            "Content-Type": "application/json"
        }
        response = self.session.post("https://public.nvcomment.nicovideo.jp/v1/threads", json=payload, headers=headers).json()
        return response
    
    def process_filter(self, channel_info):
        process_target = copy.deepcopy(channel_info)
        id_occurrences = {}
        for entry in process_target:
            for item in entry['filter_data']:
                id_occurrences.setdefault(item['id'], 0)
                id_occurrences[item['id']] += 1
        
        duplicate_ids = {id_ for id_, count in id_occurrences.items() if count > 1}
        
        for dup_id in duplicate_ids:
            process_target[0]['filter_data'] = [
                item for item in process_target[0]['filter_data'] if item['id'] != dup_id
            ]
        return process_target
        
    
    def generate_xml(self, json_data):
        print("Checking Duplicate comment")
        seen = set()
        unique_data = []
        for item in json_data:
            key = (item["userId"], item["postedAt"], item["body"])
            if key not in seen:
                seen.add(key)
                unique_data.append(item)

        removed_count = len(json_data) - len(unique_data)
        print(f" + Delete {removed_count} comment")

        root = ET.Element("packet", version="20061206")
        
        for item in unique_data:
            chat = ET.SubElement(root, "chat")
            chat.set("no", str(item["no"]))
            chat.set("vpos", str(item["vposMs"] // 10))
            timestamp = datetime.fromisoformat(item["postedAt"]).timestamp()
            chat.set("date", str(int(timestamp)))
            chat.set("date_usec", "0")
            chat.set("user_id", item["userId"])
            
            chat.set("mail", " ".join(item["commands"]))
            
            chat.set("premium", "1" if item["isPremium"] else "0")
            chat.set("anonymity", "0")
            chat.text = item["body"]
        
        return ET.ElementTree(root)
    def save_xml_to_file(self, tree, base_filename="output.xml"):
        directory = os.path.dirname(base_filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        filename = base_filename
        counter = 1
        while os.path.exists(filename):
            filename = f"{os.path.splitext(base_filename)[0]}_{counter}.xml"
            counter += 1
    
        ET.indent(tree, space="  ", level=0)
        
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        return filename
    
    def export_comment(self, search_info):
        total_comment = 0
        total_comment_json = []
        total_tv = []

        total_filter = []

        channle_list = self.get_channel_list(search_info)
        for single_channel in channle_list:
    
            filter_data, thread_key = self.get_channel_info(single_channel["contentId"])
            single_json = {
                "filter_data": filter_data,
                "thread_key": thread_key
            }
            total_filter.append(single_json)
        processed_list = self.process_filter(total_filter)
        for single_channel_count, single_channel in enumerate(channle_list):
            channle_response = self.get_content_channel(processed_list[single_channel_count])
            for i in channle_response["data"]["globalComments"]:
                total_comment = total_comment + i["count"]
            if self.logined_ac:
                for single_thread in channle_response["data"]["threads"]:
                    print("Checking Comment Count")
                    print(" + Channel Comment Count: ", str(single_thread["commentCount"]))
    
                    if single_thread["commentCount"] == len(single_thread["comments"]):
                        total_comment_json.extend(single_thread["comments"])
                        continue
    
                    temp_list = list(single_thread["comments"])
                    temp_count = len(temp_list)
    
                    dt = datetime.fromisoformat(single_thread["comments"][0]["postedAt"])
                    first_unixtime = int(dt.timestamp())
    
    
                    while temp_count < single_thread["commentCount"]:
                        search_target = {
                            "thread_key": processed_list[single_channel_count]["thread_key"],
                            "filter_data": [
                                {
                                    "id": single_thread["id"],
                                    "fork": single_thread["fork"],
                                }
                            ]
                        }
    
                        channel_response = self.get_content_channel(search_target, first_unixtime)
                        comments = channel_response["data"]["threads"][0]["comments"]
    
                        if not comments:
                            break
    
                        temp_list.extend(comments)
                        temp_count = len(temp_list)
    
                        dt = datetime.fromisoformat(comments[0]["postedAt"])
                        first_unixtime = int(dt.timestamp())
                    
                    print(" + Last Check List count: ", str(len(temp_list)))
                    total_comment_json.extend(temp_list)
            else:
                for i in channle_response["data"]["threads"]:
                    for i in i["comments"]:
                        total_comment_json.append(i)
                                
            if single_channel["tags"].__contains__("dアニメストア"):
                total_tv.append("dアニメ")
            else:
                total_tv.append("公式")

        return total_tv, total_comment, total_comment_json