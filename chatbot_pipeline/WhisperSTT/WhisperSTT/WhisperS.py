import io
import os
import time

import torch
import wave

import whisper

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
model = whisper.load_model("medium.en", download_root="/app/whisper/model")


# while True:
#     file = input("provide new file to transcribe :")

    # with open(file, 'rb') as pcmfile:
    #     pcmdata = pcmfile.read()
    # with wave.open(file+'.wav', 'wb') as wavfile:
    #     # wavfile.setparams((2, 2, 16000, 0, 'NONE', 'NONE'))
    #     wavfile.setnchannels(1)
    #     wavfile.setsampwidth(2)
    #     wavfile.setframerate(16000)
    #     wavfile.writeframes(pcmdata)

    # result = model.transcribe(file+'.wav')
    # print(result['text'])




STTPath = "/app/whisper/"
# STTPath = os.path.join(STTPath, 'data')

dtfilename = time.strftime("%Y%m%d-%H%M%S")

def GetdtFilePath():
    return os.path.join(STTPath, dtfilename+".pcm")

def Load_Model():
    print('Initializing Client...')

def Initialize_Stream():
    global  dtfilename
    dtfilename = time.strftime("%Y%m%d-%H%M%S")

    if os.path.exists(GetdtFilePath()):
        os.remove(GetdtFilePath())

def Process_Stream(bufferData):
    global dtfilename
    with open(GetdtFilePath(), "ab") as f:
        f.write(bufferData)
        f.close()

def Finish_STT():
    global client,dtfilename
    response = ""
    try:
        # The name of the audio file to transcribe
        file_name = GetdtFilePath()

        if os.path.exists(file_name):
            with open(file_name, 'rb') as pcmfile:
                pcmdata = pcmfile.read()
            with wave.open(file_name+'.wav', 'wb') as wavfile:
                # wavfile.setparams((2, 2, 16000, 0, 'NONE', 'NONE'))
                wavfile.setnchannels(1)
                wavfile.setsampwidth(2)
                wavfile.setframerate(16000)
                wavfile.writeframes(pcmdata)

            result = model.transcribe(file_name+'.wav')
            os.remove(file_name+'.wav')
            print(result['text'])

            response = result['text']

    except Exception as e: print("Error in recieve"+str(e))


    return response


