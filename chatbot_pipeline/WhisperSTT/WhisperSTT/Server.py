import socket
import sys
import binascii
try:
    import threading
except ImportError:
    import dummy_threading as threading

from WhisperS import *
import json
import enum
import time
from threading import Timer
from _thread import start_new_thread, allocate_lock

#Current STT Request type
Request_Type = "NA"

#Storage for recieved audio data
audio_buffer = []
audio_buffer_access_lock = allocate_lock()

#Keep running audio processing thread thread
WaitForData = False
WaitForData_access_lock = allocate_lock()

#nn network is being used
ISNetworkBusy = False

def WaitForDatat_timeout():
    global WaitForData_access_lock, WaitForData
    WaitForData_access_lock.acquire()
    WaitForData = False
    WaitForData_access_lock.release()


#Audio recieve timer timout
t = Timer(0, WaitForDatat_timeout)



class STT_STATES(enum.Enum):
    INITIALIZE_STREAM = 1
    PROCESS_STREAM = 2
    FINISH_STT = 3
    NA = 0


Session_State = STT_STATES.NA


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
port = 3582
connection = None
address = None


try:
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((host, port))
except socket.error as e:
	print(str(e))

s.listen(5)

Load_Model()


print("Ani : Speech to Text Server ready . . .!!")



def ProcessAudio(conn):
    global WaitForData, Request_Type, ISNetworkBusy, audio_buffer_access_lock, audio_buffer, t
    ISNetworkBusy = True
    try:
        while WaitForData:
            if Request_Type == 'PROCESS_STREAM':
                print("processing")
                if len(audio_buffer) > 0:
                    audio_strData = audio_buffer[0]
                    audio_data = binascii.a2b_base64(audio_strData)
                    Process_Stream(audio_data)
                    audio_buffer_access_lock.acquire()
                    del audio_buffer[0]
                    audio_buffer_access_lock.release()
            elif Request_Type == 'FINISH_STT':
                t.cancel()
                while len(audio_buffer) > 0:
                    audio_strData = audio_buffer[0]
                    audio_data = binascii.a2b_base64(audio_strData)
                    Process_Stream(audio_data)
                    audio_buffer_access_lock.acquire()
                    del audio_buffer[0]
                    audio_buffer_access_lock.release()
                print("finishing")
                sentence = Finish_STT()
                print("STT : "+sentence)
                conn.sendall(json.dumps({'RESULT':sentence}).encode())
                print("finished")
                break
            time.sleep(0.001)
    except Exception as e: print("Error in proce4ssing"+str(e))
    ISNetworkBusy = False
    return



def threaded_client(conn):
    global Session_State, WaitForData, WaitForData_access_lock, Request_Type, ISNetworkBusy, audio_buffer_access_lock, audio_buffer, t
    while True:
        
        data = conn.recv(122880)
        try:
            strmessage = data.decode('utf-8')
            print("recieved : "+strmessage)
            if strmessage != '':
                jsnmessage = json.loads(strmessage)
                Request_Type = jsnmessage['STATE']

                
                if Request_Type == 'INITIALIZE_STREAM':
                    Session_State = STT_STATES.INITIALIZE_STREAM
                    print("DeepSpeech Connection : INITIALIZE_STREAM")
                    Initialize_Stream()
                    Session_State = STT_STATES.PROCESS_STREAM

                    print("1. Waitign for thread lock")
                    WaitForData_access_lock.acquire()
                    WaitForData = False
                    WaitForData_access_lock.release()
                    print("2. thread lock aquired")

                    print("3. IS network busy")
                    #Wait untill network is released by previous request
                    while ISNetworkBusy:
                        continue

                    print("4. Waitign for Thread lock")
                    WaitForData_access_lock.acquire()
                    WaitForData = True
                    WaitForData_access_lock.release()
                    print("5. Thread lock aquired")

                    # duration is in seconds
                    t = Timer(5, WaitForDatat_timeout)
                    t.start()
                    
                    print("6. Started Thread")
                    start_new_thread(ProcessAudio,(conn,))
                    conn.sendall(json.dumps({'STATUS' : 'OK'}).encode())


                elif Request_Type == 'PROCESS_STREAM':
                    if Session_State == STT_STATES.PROCESS_STREAM:
                        t.cancel()

                        print("DeepSpeech Connection : PROCESS_STREAM")
                        audio_buffer_access_lock.acquire()
                        audio_buffer.append(jsnmessage['Message'])
                        audio_buffer_access_lock.release()
                        conn.sendall(json.dumps({'STATUS' : 'OK'}).encode())
                        # duration is in seconds
                        t = Timer(5, WaitForDatat_timeout)
                        t.start()

                elif Request_Type == 'FINISH_STT':
                    Session_State = STT_STATES.NA
            else:
                conn, address = s.accept()
                print("connected to :"+address[0]+" port: "+str(address[1])+"\n")

        except Exception as e: print("Error in recieve : "+str(e))
    conn.close()

		


while True:
	connection, address = s.accept()
	print("connected to :"+address[0]+" port: "+str(address[1])+"\n")
	# start_new_thread(threaded_client,(connection,))
	threaded_client(connection)
			
