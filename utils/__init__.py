import json
import urllib.parse

class Niconico_Search:
    def __init__(self, session):
        self.session = session
    def setup_sesson(self, session):
        session.headers.update({
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