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

print("Ani : Importing Chatbot_Emotion!!", flush=True)
from transformers import AutoTokenizer, AutoModelWithLMHead

print("Ani : Loading model!!", flush=True)
tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-emotion")
model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-emotion", device_map="auto", load_in_8bit=True)





def get_emotion(text):
  input_ids = tokenizer(text + '</s>', return_tensors='pt').to("cuda")

  output = model.generate(**input_ids, max_length=2)
  
  dec = [tokenizer.decode(ids) for ids in output]
  label = dec[0]

  em_pred = {
	'sadness':0,
	'joy':0,
	'love':0,
	'anger':0,
	'fear':0,
	'surprise':0,
  }

  em_pred[label.split(" ")[1]] = 100

  print(label.split(" ")[1])

  return {'ANGER':str(em_pred['anger']), 
  'DISGUST':str(em_pred['anger']), 
  'FEAR':str(em_pred['fear']), 
  'JOY':str(em_pred['joy']), 
  'SADNESS':str(em_pred['sadness']), 
  'SURPRISE':str(em_pred['surprise'])}


return_queue = queue.Queue()
request_queue = queue.Queue()
def from_main_thread_blocking():
    while True:
        message = request_queue.get() #blocks until an item is available
        sentenceID = message[0]
        EmosStats = get_emotion(message[1])
        return_queue.put((sentenceID, EmosStats))

audioConvertor = threading.Thread(target=from_main_thread_blocking)
audioConvertor.start()
	
app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/EMOS', methods=['POST'])
def EMOS():
	sentenceID = uuid.uuid1()
	params = flask.request.get_json()
	sentence = params['sentence']
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return json.dumps({ "TYPE" : "EMOS" , "DATA": message[1]})


@app.route('/WEB/EMOS/<sentence>')
def WebEMOS(sentence):
	sentenceID = uuid.uuid1()
	data = (sentenceID, sentence)
	request_queue.put(data)
	message = return_queue.get()
	if message[0] == sentenceID :
		return "<h1>EMOS Output</h1><p>"+json.dumps(message[1])+"</p>"



@app.route('/', methods=['GET'])
def home():
    return flask.render_template('basic.html', WebAPI="EmoS WebAPI : use /WEB/EMOS/<sentence>",
	API = "EmoS API : use /EMOS/<sentence>")


if __name__ == "__main__":
    print("fmService : EmoS is ready . . .!!")
    app.run(host='0.0.0.0', port=3579)