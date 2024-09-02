import sys
import socket
import requests
import json
import base64
import datetime

#Text to emotion endpoint
TTE_host = '127.0.0.1'
TTE_Port = 3579

#chatbot endpoint
Chatbot_host = '127.0.0.1'
Chatbot_Port = 3580

#Text to speech endpoint
TTS_host = '127.0.0.1'
TTS_Port = 3578

#Speech to text endpoint
STT_host = ''
STT_Port = 3582
STT_Socket = None

#Text to Intent recognition endpoint
TTI_host = '127.0.0.1'
TTI_Port = 3581

class EndPointManager():


	@staticmethod
	def initSTTStream():
		global STT_Socket, STT_Port, STT_host

		try:
			if STT_Socket is not None:
				STT_Socket.close()
		except socket.error as e:
				print(str(e))

		STT_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			STT_Socket.connect((STT_host, STT_Port))
			print("DeepSpeech__Socket Server Connection initialized : INITIALIZE_STREAM")
			STT_Socket.send(json.dumps({'STATE': 'INITIALIZE_STREAM'}).encode())
			Status = STT_Socket.recv(4096).decode('utf-8')
			print("DeepSpeech return : INITIALIZE_STREAM : "+Status)
			return Status
		except socket.error as e:
			print(str(e))

	@staticmethod
	def processSTTStream(bufData):
		global STT_Socket
		try:
			print("DeepSpeech__Socket Server Connection initialized : PROCESS_STREAM")
			STT_Socket.send(json.dumps({'STATE': 'PROCESS_STREAM', 'Message':bufData}).encode())
			Status = STT_Socket.recv(4096).decode('utf-8')
			return Status
		except socket.error as e:
			print(str(e))

	@staticmethod
	def finishSTTStream():
		global STT_Socket
		try:
			print("DeepSpeech__Socket Server Connection initialized : FINISH_STT")
			STT_Socket.send(json.dumps({'STATE': 'FINISH_STT'}).encode())
			Status = STT_Socket.recv(4096).decode('utf-8')
			return Status
		except socket.error as e:
			print(str(e))



	@staticmethod
	def BotEmotion(sentence):
		global TTE_host, TTE_Port
		
		try:
			url = f"http://{TTE_host}:{TTE_Port}/EMOS"
			body = {'sentence': sentence}
			response = requests.post(url, json=body)
			return response.json()
		except socket.error as e:
			print("Error : "+str(e))

		return "{'TYPE':'EMOS', 'DATA':''}"

	def BotChat(sentence, emotion):
		global Chatbot_host, Chatbot_Port
		
		try:
			url = f"http://{Chatbot_host}:{Chatbot_Port}/EMOCHAT"
			body = {'sentence': sentence, 'emotion' : emotion}
			response = requests.post(url, json=body)
			print(f"response.....{response}")
			return response.json()
		except socket.error as e:
			print("Error BotChat: "+str(e))

		return "{'TYPE':'EMOS', 'DATA':''}"
		
	@staticmethod
	def BotGetIntentList():
		global TTI_host, TTI_Port
		
		try:
			url = f"http://{TTI_host}:{TTI_Port}/INTENTS"
			response = requests.post(url, json=None)
			return response.json()
		except socket.error as e:
			print("Error : "+str(e))

		return "{'INTENTS': []}"

	@staticmethod
	def BotFindIntent(sentence):
		global TTI_host, TTI_Port
		
		try:
			url = f"http://{TTI_host}:{TTI_Port}/NLP"
			body = {'sentence': sentence}
			response = requests.post(url, json=body)
			return response.json()
		except socket.error as e:
			print("Error : "+str(e))

		return "{'INTENT':'', 'CONFIDENCE':''}"


	@staticmethod
	def callBot(context, emotion):
		global Chatbot_host, Chatbot_Port

		try:
			url = 'http://%s:%s/cakechat_api/v1/actions/get_response' % (Chatbot_host, Chatbot_Port)
			body = {'context': context, 'emotion': emotion}
			response = requests.post(url, json=body)
			return response.json()
		except socket.error as e:
			print(str(e))


	@staticmethod
	def BotSynthesis(sentence):
		global TTS_host, TTS_Port
		
		try:
			url = f"http://{TTS_host}:{TTS_Port}/TTS"
			body = {'sentence': sentence}
			response = requests.post(url, json=body)
			return response.json()
		except socket.error as e:
			print("Error : "+str(e))

		return "{'TYPE':'TTS', 'DATA':''}"
