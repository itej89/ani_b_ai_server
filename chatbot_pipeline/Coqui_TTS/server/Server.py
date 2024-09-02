import sys
import base64
import re
import os
import flask
import threading, queue
import uuid 
from shutil import copyfile


try:
    import threading
except ImportError:
    import dummy_threading as threading


import soundfile
import librosa   
from TTS.api import TTS
import json


model_name = TTS.list_models()[2]

# Init TTS
# tts = TTS(model_name)

# tts = TTS("tts_models/en/ljspeech/fast_pitch")
# tts = TTS("vocoder_models/en/ljspeech/hifigan_v2")
tts = TTS("tts_models/en/vctk/vits", gpu = True)

wav_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "synth.wav")
	


def ConvertToAudio(message):
	global  wav_path, tts
	sentenceID = message[0]
	sentence = message[1]
	sentence = re.sub('[^ a-zA-Z]+', '', sentence)
	sentence = sentence.lower()
	if sentence.startswith("im"):
		sentence = sentence.replace("im ", "i'm ")
	
	sentence = sentence.replace(" im ", " i'm ")
    
	tts.tts_to_file(text=sentence, speaker = tts.speakers[0], file_path=wav_path)
	# data, samplerate = soundfile.read(wav_path, samplerate=16000)
	data, samplerate = librosa.load(wav_path, sr=16000)
	soundfile.write(wav_path, data, samplerate=16000, subtype='PCM_16')


	audio = open(wav_path, "rb")
	audio_read = audio.read()
	audio_encode = base64.encodebytes(audio_read)
	return audio_encode


return_queue = queue.Queue()
request_queue = queue.Queue()
def from_main_thread_blocking():
    while True:
        message = request_queue.get() #blocks until an item is available
        pcmBytes = ConvertToAudio(message)
        return_queue.put((message[0], pcmBytes))

audioConvertor = threading.Thread(target=from_main_thread_blocking)
audioConvertor.start()
	
app = flask.Flask(__name__)
app.config["DEBUG"] = False


@app.route('/TTS', methods=['POST'])
def TTS():
	sentenceID = uuid.uuid1()
	params = flask.request.get_json()
	sentence = params['sentence']
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return json.dumps({ "TYPE" : "TTS", "DATA" : message[1].decode('utf-8') })


@app.route('/WEB/TTS/<sentence>')
def WebTTS(sentence):
	sentenceID = uuid.uuid1()
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return "<h1>DUR TTS</h1><audio src=\""+"/TTSData/"+str(sentenceID)+".wav""\" type=\"audio/wav\" controls>No support!</audio>"


@app.route('/TTSData/<path:filename>')
def download_file(filename):
    global  wav_path
    return flask.send_from_directory(os.path.dirname(os.path.realpath(__file__)), "synth.wav")


@app.route('/', methods=['GET'])
def home():
    return flask.render_template('basic.html', title="Text to speech : use /WEB/TTS/<sentence>")


if __name__ == "__main__":
    print("fmService : TTS is ready . . .!!")
    app.run(host='0.0.0.0', port=3578)
