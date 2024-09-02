import sys
import base64
import re
import os
import flask
import threading, queue
import uuid 
from shutil import copyfile
import json

try:
    import threading
except ImportError:
    import dummy_threading as threading

print("Ani : Importing Chatbot!!", flush=True)
from transformers import pipeline, Conversation


print("Ani : Importing Chatbot model!!", flush=True)
converse = pipeline("conversational", device=0)




def get_response(text):
    return converse([Conversation(text)]).generated_responses[0]


return_queue = queue.Queue()
request_queue = queue.Queue()
def from_main_thread_blocking():
    while True:
        message = request_queue.get() #blocks until an item is available
        sentenceID = message[0]
        answer = get_response(message[1])
        return_queue.put((sentenceID, answer))

audioConvertor = threading.Thread(target=from_main_thread_blocking)
audioConvertor.start()
	
app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/CHAT', methods=['POST'])
def CHAT():
	sentenceID = uuid.uuid1()
	params = flask.request.get_json()
	sentence = params['sentence']
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return json.dumps({ "TYPE" : "CHAT" , "DATA": message[1]})


@app.route('/WEB/CHAT/<sentence>')
def WebCHAT(sentence):
	sentenceID = uuid.uuid1()
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return "<h1>CHAT Output</h1><p>"+message[1]+"</p>"



@app.route('/', methods=['GET'])
def home():
    return flask.render_template('basic.html', WebAPI="Chat WebAPI : use /WEB/CHAT/<sentence>",
	API = "Chat API : use /CHAT/<sentence>")


if __name__ == "__main__":
    print("fmService : Chat is ready . . .!!")
    app.run(host='0.0.0.0', port=3580)