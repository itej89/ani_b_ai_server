from channels import Group
from channels.sessions import channel_session
import logging
import sys
import json
import operator
import subprocess
import shlex
import datetime
import os
import base64

from  .EndPointManager import EndPointManager

def getClientName(client):
    """ Return the unique id for the client
    Args:
            client list<>: the client which send the message of the from [ip (str), port (int)]
    Return:
            str: the id associated with the client
    """
    return 'room-' + client[0] + '-' + str(client[1])

@channel_session
def ws_connect(message):
    if message['path'] == '/chat': 
        clientName = getClientName(message['client'])
        print('New client connected: {}'.format(clientName))
        Group(clientName).add(message.reply_channel)
        message.channel_session['ClientID'] = clientName
        message.reply_channel.send({'accept': True})


@channel_session
def ws_receive(message):
    if "ClientID" in message.channel_session:
        clientName = message.channel_session['ClientID']
        print('Message recieved : {}'.format(clientName))

        data = json.loads(message['text'])

        # Compute the prediction
        Request_Type = data['Type']
        question = data['Message']

        if Request_Type == 'STT':

            Session_State_Type = data['SES_STATE']
            if Session_State_Type == 'INITIALIZE_STREAM':
                Status = EndPointManager.initSTTStream()
                if Status != '':
                    Status = json.loads(Status)
                    Group(clientName).send({'text': json.dumps({'Type':'STT','INITIALIZE_STREAM': Status['STATUS']})})
                else:
                    Group(clientName).send({'text': json.dumps({'Type':'STT','INITIALIZE_STREAM': 'NOK'})})
        
            elif Session_State_Type == 'PROCESS_STREAM':
                audioBuffer = data['AUDBUF']
                Status = EndPointManager.processSTTStream(audioBuffer)
                if Status != '':
                    print("Process Status : "+str(Status))
                    Status = json.loads(Status)
                    Group(clientName).send({'text': json.dumps({'Type':'STT','PROCESS_STREAM': Status['STATUS']})})
                else:
                    Group(clientName).send({'text': json.dumps({'Type':'STT','PROCESS_STREAM': 'NOK'})})

            elif Session_State_Type == 'FINISH_STT':
                Status = json.loads(EndPointManager.finishSTTStream())
                
                Group(clientName).send({'text': json.dumps({'Type':'STT','FINISH_STT': Status['RESULT']})})

        # if request is only for synthesizing text to audio
        elif Request_Type == 'SYNTH':
            try:
                audio_wav_bytes = EndPointManager.BotSynthesis(question)['DATA']
            except:  # Catching all possible mistakes
                logger.error('{}: Error with this question {}'.format(
                    clientName, question))
                logger.error("Unexpected error:"+ sys.exc_info()[0])
                answer = 'Error: Internal problem'

        # Send the prediction back
            Group(clientName).send({'text': json.dumps({'message': question, 'synth': audio_wav_bytes.decode('utf-8')})})

        # if request is only for emotion, return emotion values for teh question
        elif Request_Type == 'EMO':
            try:
                emotion = ChatbotManager.BotEmotion(question)['DATA']
            except:  # Catching all possible mistakes
                logger.error('{}: Error with this question {}'.format(
                    clientName, question))
                logger.error("Unexpected error:"+sys.exc_info()[0])
                answer = 'Error: Internal problem'

        # Send the prediction back
            Group(clientName).send({'text': json.dumps({'message': question, 'anger': emotion['ANGER'], 'disgust': emotion[
                'DISGUST'], 'fear': emotion['FEAR'], 'joy': emotion['JOY'], 'sadness': emotion['SADNESS'], 'surprise': emotion['SURPRISE']})})

            # if request is for both response and emotion
        elif Request_Type == '3DPrintJob':
            with open ("/home/tej/Documents/Ani_Cloud/Printers/3D/Ender3_12345/jobs", "r") as jobsfile:
                jobnames=jobsfile.readline().rstrip()
                jobfilepath = os.path.join('/home/tej/Documents/Ani_Cloud/Printers/3D/Ender3_12345/Designs/', jobnames)
                if jobnames != "" and os.path.isfile(jobfilepath):
                    with open (jobfilepath, "r") as designfile:
                        filecontent=designfile.read()
                        Group(clientName).send({'text': json.dumps({'message': filecontent})})

            # if jobnames != "":
            #     with open("/home/tej/Documents/Ani_Cloud/Printers/3D/Ender3_12345/jobs", 'r') as fin:
            #         jobnames = fin.read().splitlines(True)
            #     with open("/home/tej/Documents/Ani_Cloud/Printers/3D/Ender3_12345/jobs", 'w') as fout:
            #         fout.writelines(jobnames[1:])



        elif Request_Type == 'QA':

            print('QA Started')

            print('Reading Emotion : {}'.format(question))
            QEmotion  = EndPointManager.BotEmotion(question)

            try:
                QHighestEmotion = 'JOY'  # Emotion value to be sent for CakeChat, Default is set to JOY
                QHighestEmotionValue = 0

                # Find emotion with highest predicted value for the question
                for key, val in QEmotion['DATA'].items():
                    EmoValue = float(val)
                    if(float(EmoValue) > QHighestEmotionValue):
                        QHighestEmotionValue = EmoValue
                        QHighestEmotion = key

                        # Convert EmoS to CakeChat Emotions {neutral', 'anger', 'joy', 'fear', 'sadness'}
                        if QHighestEmotion == 'JOY':
                            QHighestEmotion = 'joy'
                        elif QHighestEmotion == 'ANGER':
                            QHighestEmotion = 'anger'
                        elif QHighestEmotion == 'SADNESS':
                            QHighestEmotion = 'sadness'
                        elif QHighestEmotion == 'FEAR':
                            QHighestEmotion = 'fear'
                        elif QHighestEmotion == 'DISGUST':
                            QHighestEmotion = 'neutral'
                        elif QHighestEmotion == 'SURPRISE':
                            QHighestEmotion = 'neutral'

                print('Highest Emotion : {}'.format(QHighestEmotion))
                CackeChatBufferedRequests = []
                if question != "":
                    CackeChatBufferedRequests.append(question)

                    answer = EndPointManager.callBot(CackeChatBufferedRequests, QHighestEmotion)
                    print('ChatBot Response : {}'.format(answer['response']))

                    emotion = EndPointManager.BotEmotion(answer['response'])['DATA']

                    nlp_information = EndPointManager.BotFindIntent(question)['DATA']

                    print('NLP Confidence : {}'.format(nlp_information['CONFIDENCE']))

                    if nlp_information['CONFIDENCE'] > 0.71:
                        audio_wav_bytes = EndPointManager.BotSynthesis('okay')['DATA']
                    else:
                        audio_wav_bytes = EndPointManager.BotSynthesis(answer['response'])['DATA']
                        

                    Group(clientName).send({'text': json.dumps({'message': answer['response'], 'anger': emotion['ANGER'], 'disgust': emotion['DISGUST'], 'fear': emotion['FEAR'], 'joy': emotion['JOY'], 'sadness': emotion['SADNESS'], 'surprise': emotion['SURPRISE'], 'intent':nlp_information['INTENT'], 'intent_conf':nlp_information['CONFIDENCE'] ,'synth': audio_wav_bytes})})
                    
                    print('QA Finished')

                    return

            except:  # Catching all possible mistakes
                print('{}: Error with this question {}'.format(
                    clientName, question))
                print("Unexpected error:"+ sys.exc_info()[0])
                answer = 'Error: Internal problem'

            # Check eventual error
            if not answer:
                answer = 'Error: Try a shorter sentence'
                emotion = 'None'
            
            Group(clientName).send({'text': json.dumps({'message': 'Error on server', 'anger': '0', 'disgust': '0', 'fear': '0', 'joy': '0', 'sadness': '100', 'surprise': '0', 'intent':'', 'intent_conf':'0' ,'synth': ''})})


@channel_session
def ws_disconnect(message):
    if "ClientID" in message.channel_session:
        clientName = message.channel_session['ClientID']
        print('Client disconnected : {}'.format(clientName))
    else:
        print('Client disconnected. . .')
