from youtubesearchpython import VideosSearch


class Searcher:
    def __init__(self, keyword, number_of_videos=10):
        videoSearch = dict(VideosSearch(keyword, limit=number_of_videos).result())
        self.urls = []
        self.names = []
        self.thumbnailsurls = []
        for i in videoSearch['result']:
            self.urls.append(i['link'])
            self.names.append(i['title'])
            self.thumbnailsurls.append(i['thumbnails'][0]['url'])
