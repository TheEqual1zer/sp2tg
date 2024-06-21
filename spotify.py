import spotipy

from track import Track
from spotipy.oauth2 import SpotifyClientCredentials

from util import Type


class Spotify:

    def __init__(self, client_id, client_secret):
        self.auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.client = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_type_from_url(self, query):

        if 'track' in query:
            return Type.TRACK
        elif 'album' in query:
            return Type.ALBUM
        elif 'playlist' in query:
            return Type.PLAYLIST
        else:
            return None

    def get_tracks(self, query):

        match (self.get_type_from_url(query)):

            case Type.TRACK:
                tracks = [Track(self.client.track(query))]

            case Type.ALBUM:

                result = self.client.album(query)

                tracks = list()
                for track in result['tracks']['items']:
                    track_data = track
                    track_data['album'] = result
                    tracks.append(Track(track_data))

            case Type.PLAYLIST:

                result = self.client.playlist(query)

                tracks = list()
                for track in result['tracks']:
                    if track is not None:
                        track_data = track['track']
                        if track_data is not None:
                            track_data['playlist'] = f"{result['name']} - {result['owner']['display_name']}"
                            tracks.append(Track(track_data))

            case _:
                return None

        return tracks
