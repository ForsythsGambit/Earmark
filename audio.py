#!/usr/bin/python3
import speech_recognition as sr
from thefuzz import fuzz 
import sys
import dotenv
import os
import logging
import subprocess
"""Transcription Functions"""

def prepFile(inputFile, time=15):
	"""takes inputed audio file, trims it keeping only the first {time} seconds and converts it to a .wav for transcription"""
	outputPath=f"{os.getcwd()}/temp/{os.path.basename(inputFile).split('.')[0]}.wav"
	logging.debug(f"Prepping file {inputFile}")
	subprocess.run(["ffmpeg","-i",inputFile,"-t",str(time),outPath,"-loglevel","error"])
	
	return outputPath

def transcribe(inputFile):
	dotenv.load_dotenv() #load google cloud API key from .env to its enviroment variable
	recogonizer=sr.Recognizer() #init speech_recognition
	#convert .wav file into an AudioFile instance
	audioFile = sr.AudioFile(inputFile)  
	with audioFile as source:
		recordedAudio = recogonizer.record(source)
	os.remove(inputFile) #remove .wav file
	return recogonizer.recognize_google_cloud(recordedAudio) #call google cloud api to transcribe audio

"""Wrapper"""

def processAudiobook(audiobookDirectory):
	supportedAudioFormats = ["mp3","wav", "ogg", "m4a", "flac"] #todo
	preppedAudioFiles=[]
	transcriptions = []
	workingDirectory = os.getcwd()
	files=os.listdir(audiobookDirectory)
	logging.debug(f"Found {len(files)} files in {audiobookDirectory}")
	if "temp" not in os.listdir(workingDirectory):
		os.mkdir("temp")
		logging.debug("Making temp folder for audio files")
	for file in files:
		#logging.debug(f"Checking file: {file}") #a little *too* verbose
		split=file.split(".")
		#logging.debug(f"Split file extension into {split}") # this one too
		if len(split) == 1:
			logging.debug(f"file: {file} has no extension!")
			continue
		if split[1] == "m4b":
			logging.error("m4b format audiobooks are unsupported, please split it into multiple mp3s")
			raise ValueError("Unsupported file format, please split it into multiple .mp3s!")
		if split[1] in supportedAudioFormats:
			logging.debug(f"Found file for processing: {file}")
			preppedAudioFiles.append(prepFile(f"{audiobookDirectory}/{file}"))
	logging.info(f"Processed {len(preppedAudioFiles)} files: {*preppedAudioFiles,}")
	for file in preppedAudioFiles:
		dict={}
		dict["file"]=file
		dict["text"]=transcribe(file)
		transcriptions.append(dict)
	logging.info(f"Transcribed {len(transcriptions)} files")
	os.rmdir("./temp")
	return transcriptions
	

if __name__ == '__main__':
	args = sys.argv # [current file, function name , *args]
	try:
		globals()[args[1]](*args[2:])
	except IndexError:
		#script was called without any commandline arguments, otherwise it would error with IndexError
		pass
