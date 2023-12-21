from flask import Flask, jsonify
from threading import Thread

app = Flask('name')


@app.route('/')
def index():
  data = {"message":"Alive", "reponse":200}
  return jsonify(data)


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()
