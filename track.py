class Track:

    def __init__(self, data):

        # metadata of mp3
        self.title = None
        self.album = None
        self.artists = None
        self.release_date = None
        self.track_number = None
        self.track_cover = None

        # youtube video id to match with filename
        self.video_id = None

        # json from spotify api
        self._data = data

        self.set_data()


    def set_data(self):

        # analyze json reply and set corresponding fields
        self.title = self._data['name']
        self.album = self._data['album']['name']
        self.artists = ', '.join(artist['name'] for artist in self._data['artists'])
        self.release_date = self._data['album']['release_date']
        self.track_number = self._data['track_number']
        self.track_cover = self._data['album']['images'][0]['url']
