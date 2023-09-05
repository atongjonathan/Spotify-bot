import requests
from bs4 import BeautifulSoup
from datetime import datetime



def try_data(link, no_of_songs):
    response = requests.get(link)
    data = response.text
    soup = BeautifulSoup(data, "html.parser")
    div_tags = soup.findAll(name="div",
                            class_="o-chart-results-list-row-container")

    h3 = [div.find("h3") for div in div_tags]
    span = [div.findAll("span") for div in div_tags]
    image_tags = [div.findAll("img") for div in div_tags]
    songs = []
    links = []
    images = []
    titles = []
    artists = []
    for image in image_tags:
        images.append(image[0].get("data-lazy-src"))
    for number in range(0, no_of_songs):
        title = h3[number].getText().strip()
        artist = span[number][1].getText().strip()
        image = image_tags[number]
        links.append(image)
        if "NEW" in artist:
            artist = span[number][3].getText().strip()
        songs.append(f"{number + 1}. {title} - {artist}\n")
        titles.append(title)
        artists.append(artist)

    return titles, artists

def get_data(no_of_songs):
    day = int(datetime.now().strftime("%d"))
    date = datetime.now().strftime(f"%Y-%m-{day}")
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    site_down = True
    while site_down:    
        try:
            titles,artists = try_data(url,no_of_songs)
            site_down = False
        except IndexError:
            day = day-1
            date = datetime.now().strftime(f"%Y-%m-{day}")
            url = f"https://www.billboard.com/charts/hot-100/{date}"
    return titles,artists

def get_dic_of_songs(no_of_songs,url):
    titles,artists = get_data(url, no_of_songs)
    dict_of_songs = []
    for number in range(0,no_of_songs):
        song = {
            "artist": artists[number],
            "track": titles[number]
        }
        dict_of_songs.append(song) 
    return dict_of_songs

# print(get_data(10))