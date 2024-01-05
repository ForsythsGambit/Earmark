#!/usr/bin/python3
import speech_recognition as sr
import ffmpy
import sys
import dotenv
import os

def prepFile(inFile, time=15):
	#takes inputed audio file, trims it keeping only the first {time} seconds and converts it to a .wav for transcription
	ff = ffmpy.FFmpeg(
		inputs={
			inFile : None
		},
		outputs={
			inFile.split(".")[0]+".wav": f"-t {time} -loglevel error" #this splits inFile at the `.` , takes the first half and adds .wav as the file extension
		}
	)
	ff.run()
	return inFile.split(".")[0]+".wav" # returns preped file name

def transcribe(inFile):
	dotenv.load_dotenv() #load google cloud API key from .env to its enviroment variable
	recogonizer=sr.Recognizer() #init speech_recognition
	#convert .wav file into an AudioFile instance
	audioFile = sr.AudioFile(inFile)  
	with audioFile as source:
		recordedAudio = recogonizer.record(source)
	os.remove(inFile) #remove .wav file
	return recogonizer.recognize_google_cloud(recordedAudio) #call google cloud api to transcribe audio

def run(inFile):
	print(transcribe(prepFile(inFile)))

if __name__ == '__main__':
	# little bit of stackoverflow magic which should let me call functions from the command like so:
	#python3 main.py trimFle test.mp3 ttest.mp3
	args = sys.argv
	# args[0] = current file
	# args[1] = function name
	# args[2:] = function args : (*unpacked)
	try:
		globals()[args[1]](*args[2:])
	except IndexError:
		#script was called without any commandline arguments, otherwise it would error with IndexError
		pass