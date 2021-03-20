import csv
import json
import time
import pytube
import requests
import re


class VideoInfo:
    filter_name = ''
    video_id = ''


zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')


#检验是否含有中文字符
def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


class CarVideoDownloader:

    def get_video_ids(self, filter_name):
        u = 'https://www.youtube.com/results?search_query=%s' % filter_name

        # soup解析不了，手动字符串匹配
        resp = requests.get(u)
        if resp.status_code != 200:
            return None, 'invalid status_code=%d' % resp.status_code

        videoInfos = []

        content = resp.text

        index = content.find('var ytInitialData = ')
        if index == -1:
            return None, 'resp is invalid'
        content = content[index:]

        last_index = content.find(';</script>')

        c = content[len('var ytInitialData = '):last_index]

        json_val = json.loads(c)

        items = json_val['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
            'contents'][0]['itemSectionRenderer']['contents']
        for item in items:
            if item.get('videoRenderer') is None:
                continue
            info = VideoInfo()
            info.filter_name = filter_name
            info.video_id = item['videoRenderer']['videoId']
            videoInfos.append(info)
        return videoInfos, None


    def download(self, video_info):
        u = 'https://www.youtube.com/watch?v=%s' % video_info.video_id
        yt = pytube.YouTube(u)
        # if is_contains_chinese(yt.title):
        #     print("[Info] title=%s contains_zh, skip" % yt.title)
        #     return
        print("[Debug] download %s start..." % yt.title)
        streams = yt.streams.filter(
            file_extension='mp4',
            progressive=True,
        )
        if len(streams) == 0:
            return

        max_res = 0
        max_index = 0
        i = 0
        for stream in streams:
            x = int(stream.resolution.strip('p'))
            if x > max_res:
                max_res = x
                max_index = i
            i += 1
        stream = streams[max_index]
        print("[Debug] stream=", stream)
        stream.download('./videos/%s/' % video_info.filter_name)
        print("[Debug] download success")

        # for stream in yt.streams:
        #     print("[Debug] stream=", stream)
        #     stream.download('./videos/%s/' % video_info.filter_name)
        #     print("[Debug] download success")
        #     time.sleep(5)

    def down_all_videos(self, filter_name):

        video_infos, err = self.get_video_ids(filter_name)
        if err is not None:
            print("[Error] get_video_ids failed, err=", err)
            return err
        print("[Info] get video ids success, len is ", len(video_infos))

        for i in range(min(5, len(video_infos))):
            self.download(video_infos[i])
            time.sleep(0.5)
        return None
            

def test():
    downloader = CarVideoDownloader()
    err = downloader.down_all_videos('audi rs7')
    if err is not None:
        print("[Error] down_all_videos failed, err=", err)


def test_download():
    downloader = CarVideoDownloader()
    video_info = VideoInfo()
    for x in ['SFgLXZ9sKUc']:
        video_info.video_id = x
        video_info.filter_name = 'Lamborghini'
        downloader.download(video_info)


def exchange_to_en(raw):
    return raw.replace('奥迪', 'audi')

def product():

    models = []
    with open('./data/car_info_奥迪.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile)

        i = 0
        s = {}
        for row in spamreader:
            i += 1
            if i == 1 or s.get(row[1]):
                continue

            s[row[1]] = True
            models.append(row[1])

    downloader = CarVideoDownloader()
    i = 0
    for model_name in models:
        i += 1
        if i > 5:
            break
        print("[Debug] start to download %s" % model_name)

        err = downloader.down_all_videos(exchange_to_en(model_name))
        if err is not None:
            print("[Error] down_all_videos failed, err=", err)


if __name__ == '__main__':
    # test()
    test_download()
    # product()


