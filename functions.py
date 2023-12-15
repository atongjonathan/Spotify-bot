import subprocess
import requests
import telebot
import os


def download(track_link):
    try:
        # download track
        print("start downloading: " + track_link)
        normal_download_command = ['spotdl', "--bitrate", "320k", track_link] # nomal download
        command = normal_download_command # normal download
        subprocess.run(command, cwd="./output", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("end downloading: " + track_link)
        return True

    except Exception as e:
        # more info: apparently they give "SongError: Track no longer exists"
        # I can handle them more properly later without passing them to this function in the first place
        # e.g. by using spotify a
        return False

