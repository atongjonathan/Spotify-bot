import subprocess
from logging import getLogger

logger = getLogger(__name__)


def download(track_link):
    try:
        # download track
        print("start downloading: " + track_link)
        normal_download_command = ['./spotdl', "--bitrate", "320k", track_link] # nomal download
        command = normal_download_command # normal download
        subprocess.run(command, cwd="output")
        print("end downloading: " + track_link)

    except Exception as e:
        logger.error(e)
        ffmpeg_command = ['spotdl', "--download-ffmpeg"]
        subprocess.run(ffmpeg_command)
        normal_download_command = ['spotdl', "--bitrate", "320k", track_link] # nomal download
        command = normal_download_command # normal download
        subprocess.run(command, cwd="output")

        # more info: apparently they give "SongError: Track no longer exists"
        # I can handle them more properly later without passing them to this function in the first place
        # e.g. by using spotify a
    return True

