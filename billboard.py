import requests
from bs4 import BeautifulSoup
import datetime


def get_saturday_date():
    today = datetime.datetime.today()
    interval = 0
    weekday = today.weekday()
    if weekday == 5:
        interval = 0
    elif weekday == 6:
        interval = 6
    else:
        interval = 5 - weekday

    next_sat = today + datetime.timedelta(days=interval)
    prev_sat = next_sat - datetime.timedelta(days=7)
    date = f"{prev_sat.year}-{prev_sat.month}-{prev_sat.day}"
    return date


def get_billboard_hot_100():
    date = get_saturday_date()
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    song_tags = soup.find_all(
        "h3",
        class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")
    artist_tags = soup.find_all(
        "span",
        class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only")
    top_100 = []
    for index, tag in enumerate(song_tags):
        song_text = tag.get_text().strip()
        artist_text = artist_tags[index].get_text().strip()
        item = {"song": song_text, "title": artist_text}
        top_100.append(item)
    return top_100
