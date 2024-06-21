import os
import re
import asyncio
import requests

from aiohttp import ClientSession
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from yt_dlp import YoutubeDL


async def download_html(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception("failed to download html")

        return await response.text()


def extract_video_id_from_html(html):
    # all youtube ids are 11 chars long
    match = re.search(r"watch\?v=(\S{11})", html)

    if not match:
        raise Exception("no ids found in html")

    return match.group()[8:]  # len("watch?v=")


async def download_audio_by_youtube_id(id, track):
    ydl_opts = {
        format: "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",  # downloaded is webm
                "preferredquality": "320",
            }
        ],
        "outtmpl": f"{id}",  # with settings above saves as {id}.mp3
    }

    with YoutubeDL(ydl_opts) as ydl:
        await asyncio.to_thread(ydl.download, [f"https://www.youtube.com/watch?v={id}"])

    #set meta tags

    audio = MP3(f"{id}.mp3", ID3=EasyID3)
    audio["title"] = track.title
    audio["artist"] = track.artists
    audio["album"] = track.album
    audio["date"] = track.release_date
    audio["tracknumber"] = str(track.track_number)
    audio.save()

    audio = MP3(f"{id}.mp3", ID3=ID3)
    cover_data = requests.get(track.track_cover).content

    audio.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime="image/jpeg",  # image/jpeg or image/png
            type=3,  # 3 is for the cover(front) image
            desc="Cover",
            data=cover_data,
        )
    )
    audio.save()

    #rename

    dir = f'{track.artists} – {track.title}.mp3'
    os.rename(f'{id}.mp3', dir)

    return dir


async def download_song(session, track):
    search_query = f"https://www.youtube.com/results?search_query={track.artists} – {track.title}"
    try:
        id = extract_video_id_from_html(await download_html(session, search_query))
        return await download_audio_by_youtube_id(id, track)
    except Exception as e:
        print(f'Error while downloading {track.artists} – {track.title}: {e}')
        return None


async def download_tracks(tracks):
    async with ClientSession() as session:
        tasks = [download_song(session, track) for track in tracks]
        downloaded_files = await asyncio.gather(*tasks)
    return downloaded_files
