import billboard
import json

hot_100 = billboard.ChartData("hot-100")
chart_data = []
for song in hot_100:
  title = song.title
  artist = song.artist
  item = {"artist": song.title, "title": song.artist}
  chart_data.append(item)
print(json.dumps(chart_data, indent=4))
