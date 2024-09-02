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


import json

print("fmService : NLP is loading model. . .")
from transformers import pipeline
model = pipeline(model="facebook/bart-large-mnli", device=0)
labels = ["lights off", "lights on", "stop listening", "start 3d printer", "reset 3d printer", "tag me to wav", "open nurse app", "start cleaning", "stop cleaning", "back-forth"]


LABEL_MAP = {
    "lights off" : "LIGHTOFF", 
    "lights on" : "LIGHTON", 
    "stop listening" : "LISTENOFF", 
    "start 3d printer" : "3DPRINTERSTART", 
    "stop 3d printer" : "3DPRINTERSTOP", 
    "reset 3d printer" : "3DPRINTERRESET", 
    "tag me to wav" : "TAGTOWAV", 
    "open nurse app" : "ZERODOC", 
    "start cleaning" : "DUSTERMYROOM", 
    "stop cleaning" : "DUSTERSTOP", 
    "back-forth" : "KITCHENLOOP"
}

def Predict_Action(sentence):
    result = model(sentence, candidate_labels=labels)
    scores = result["scores"]
    argmax = max(range(len(scores)), key=lambda x : scores[x])
    print(scores)
    return LABEL_MAP[ result["labels"][argmax] ]


return_queue = queue.Queue()
request_queue = queue.Queue()
def from_main_thread_blocking():
    while True:
        message = request_queue.get() #blocks until an item is available
        sentenceID = message[0]
        NLPIntent = Predict_Action(message[1])
        return_queue.put((sentenceID, NLPIntent))

audioConvertor = threading.Thread(target=from_main_thread_blocking)
audioConvertor.start()
	
app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/NLP', methods=['POST'])
def NLP():
	sentenceID = uuid.uuid1()
	params = flask.request.get_json()
	sentence = params['sentence']
	print(sentence) 
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return json.dumps({ "TYPE" : "NLP" , "DATA": message[1]})

@app.route('/INTENTS', methods=['POST'])
def INTENTS():
	jIntentList = open("./IntentList.json", 'r')
	Intents = jIntentList.read()
	jIntentList.close()
	return Intents;


@app.route('/WEB/NLP/<sentence>')
def WebTTS(sentence):
	sentenceID = uuid.uuid1()
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	print(message)
	if message[0] == sentenceID :
		return "<h1>NLP Output</h1><p>"+f"{message[1]}"+"</p>"



@app.route('/', methods=['GET'])
def home():
    return flask.render_template('basic.html', WebAPI="NLP Web : use /WEB/NLP/<sentence>", 
	API="NLP Api : use /NLP/<sentence>", 
	Intents="Intent List : use /INTENTS")


if __name__ == "__main__":
    print("fmService : NLP is ready . . .!!")
    app.run(host='0.0.0.0', port=3581)

