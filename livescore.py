import requests
from bs4 import BeautifulSoup


def get_scores(sport):
    if sport == "football":
        link = "https://www.livescore.cz/?s=2"
    else:
        link = f"https://www.livescore.cz/{sport}/?s=2"
    response = requests.get(url=link)
    livescore = response.text
    site = BeautifulSoup(livescore, "html.parser")
    h4_tags = site.find_all(name="h4")
    titles = [tag.getText() for tag in h4_tags]

    score_data_div = site.find(name="div", id="score-data")
    spans = score_data_div.findAll(name="span")
    # text = score_data_div.findAll(name="text")
    anchor_tags = score_data_div.findAll(name="a", class_="live")
    times = [span.getText() for span in spans]
    scores = [score.getText() for score in anchor_tags]

    score_data = score_data_div.getText()

    updated_paragraph = score_data
    for time in times:
        updated_paragraph = updated_paragraph.replace(time, "/n")
    without_time = updated_paragraph

    updated_paragraph = without_time
    for score in scores:
        updated_paragraph = updated_paragraph.replace(score, "")
    without_score = updated_paragraph

    updated_paragraph = without_score
    for title in titles:
        updated_paragraph = updated_paragraph.replace(title, "")
    without = updated_paragraph

    fixtures = without.split("/n")
    fixtures.remove("")
    index = 0
    file = []
    try:
        for game in range(0, len(times)):
            file.append(f"{times[index]}  {fixtures[index]}\n                            {scores[index]}\n")
            index += 1
    except IndexError:
        file.append("Currently no live match found\n")
    return file
