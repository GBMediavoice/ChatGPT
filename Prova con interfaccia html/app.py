from flask import Flask, render_template, request
import os, requests, sounddevice as sd, soundfile as sf, io, time
from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

def play_audio(message: str, voice: str):
  response = requests.post(
      "https://api.openai.com/v1/audio/speech",
      headers={
          "Authorization": f"Bearer { os.environ.get('OPENAI_API_KEY') }"
      },
      json={
          "model": "tts-1-1106",
          "input": message,
          "voice": voice,
          "response_format": "opus"
      }
  )
  with io.BytesIO(response.content) as audio_io:
      data, samplerate = sf.read(audio_io, dtype='float32')
      sd.play(data, samplerate)
      sd.wait()

@app.route("/", methods=["GET", "POST"])
def chat():
  query:str = ""
  while query != "end":
    if request.method == "POST":
        query = request.form["query"]
        play_audio(query, 'nova')
        if(query == "end"):
          break
        completion = client.chat.completions.create(
          model="gpt-4",
          temperature=1,
          messages=[
            {"role": "system", "content": query},
            {"role": "user", "content": "rispondi"}
          ]
        )
        answer = completion.choices[0].message.content
        print(answer)
        play_audio(answer, "onyx")
  return render_template("chat.html", query=query, completion=answer)

if __name__ == "__main__":
  app.run()