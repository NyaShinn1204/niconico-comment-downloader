def setup_sesson(sesson):
    sesson.headers.update({
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

def convert_kanji(num: int):
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

def gen_episode_name_list(video_info):
    name_list = []
    episode_count = video_info["episode_name_count"]
    name_list.append(video_info["series_title"]+" "+str(episode_count)+"話")
    name_list.append(str(episode_count)+"話")
    name_list.append(convert_kanji(episode_count)+"話")
    name_list.append("第"+str(episode_count)+"話")
    name_list.append("エピソード"+str(episode_count))
    name_list.append("episode"+str(episode_count))
    name_list.append("EPISODE "+str(episode_count))
    name_list.append("EPISODE "+str(episode_count).zfill(2))
    name_list.append("ep"+str(episode_count))
    name_list.append("#"+str(episode_count))
    name_list.append("#"+str(episode_count).zfill(2))
    name_list.append(video_info["episode_name"])
    name_list.append(video_info["episode_title"])
    return " OR ".join(name_list)

def get_channel_list(video_info):
    _Q = gen_episode_name_list(video_info)

    _PAYLOAD = {
        "q": _Q,
        "_sort": "-startTime",
        "_context": "Yoimi V2/NCOverlay_3.26.8",
        "targets": "title",
        "fields": "contentId,title,userId,channelId,viewCounter,lengthSeconds,thumbnailUrl,startTime,commentCounter,categoryTags,tags",
        "jsonFilter": "",
        "_limit": 50
    }