#!/usr/bin/python3
import speech_recognition as sr
from thefuzz import fuzz 
import sys
import dotenv
import os
import logging
import subprocess
import json
"""Transcription Functions"""

def prepFile(inputFile, start = 0, outName=None, duration=15):
	"""takes inputed audio file, trims it keeping only the first {time} seconds and converts it to a .wav for transcription"""
	if outName == None:
		outputPath=f"{os.getcwd()}/temp/{os.path.basename(inputFile).split('.')[0]}.wav"
	else:
		outputPath=f"{os.getcwd()}/temp/{outName}.wav"
	logging.debug(f"Prepping file {inputFile}")
	subprocess.run(["ffmpeg","-ss",str(start),"-i",inputFile,"-t",str(duration),outputPath,"-loglevel","error"])
	
	return outputPath

def splitM4b (inputFile, time=15):
	#generate json file using ffprobe to identify chapters in an m4b
	logging.debug(f"Processing m4b file {inputFile}")
	subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_chapters","-i",inputFile,">","chapters.json"])
	with open("./test/chapters.json", "r") as file: #load json data
		jsonData = json.load(file)
	#loop over chapters and pass them to prepfile, and create of metadata
	chapters = {} 
	# {"index" :{"sourceFile":path,  start: start time (default None), sliceFile= path to sliced file, fileFormat: "m4b"}}
	for index, chapter in enumerate(jsonData["chapters"]):
		slicePath = prepFile(inputFile, start=chapter["start_time"],outName=chapter["tags"]["title"])
		chapters[str(index)]={"sourceFile": inputFile, "sliceFile": slicePath, "sourceFileFormat":"m4b", "startTime": chapter["start_time"]}
	return chapters

def transcribe(inputFile):
	dotenv.load_dotenv() #load google cloud API key from .env to its enviroment variable
	recogonizer=sr.Recognizer() #init speech_recognition
	#convert .wav file into an AudioFile instance
	audioFile = sr.AudioFile(inputFile)  
	with audioFile as source:
		recordedAudio = recogonizer.record(source)
	os.remove(inputFile) #remove .wav file
	return recogonizer.recognize_google_cloud(recordedAudio) #call google cloud api to transcribe audio
	

if __name__ == '__main__':
	pass
