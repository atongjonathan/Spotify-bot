import subprocess
from logging import getLogger

logger = getLogger(__name__)


def download(track_link):
  try:
    # download track
    print("start downloading: " + track_link)
    normal_download_command = ['spotdl', "--bitrate", "320k",
                               track_link]  # nomal download
    command = normal_download_command  # normal download
    result = subprocess.run(command,
                            cwd="output",
                            check=True,
                            text=True,
                            capture_output=True)
    logger.info(result.stdout)
    logger.info("end downloading: " + track_link)
    return True

  except subprocess.CalledProcessError as e:
    logger.error(f"Error executing process {e}")
    logger.error(f"Outputs {e.output}")
    # ffmpeg_command = ['spotdl', "--download-ffmpeg"]
    # subprocess.run(ffmpeg_command)
    # normal_download_command = ['spotdl', "--bitrate", "320k",
    #                            track_link]  # nomal download
    # command = normal_download_command  # normal download
    # subprocess.run(command, cwd="output")

    return False
