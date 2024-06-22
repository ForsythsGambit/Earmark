#!/usr/bin/python3
import speech_recognition as sr
from thefuzz import fuzz 
import dotenv
import os
import logging
import subprocess
"""Transcription Functions"""

def prepFile(inputFile: str, time=15) -> str:
	"""takes inputed audio file, trims it keeping only the first {time} seconds and converts it to a .wav for transcription"""
	outputPath: str = f"{os.getcwd()}/temp/{os.path.basename(inputFile).split('.')[0]}.wav"
	logging.debug(f"Prepping file {inputFile}")
	subprocess.run(["ffmpeg","-i",inputFile,"-t",str(time),outputPath,"-loglevel","error"])
	
	return outputPath

def transcribe(inputFile) -> str:
	dotenv.load_dotenv() #load google cloud API key from .env to its enviroment variable
	recogonizer = sr.Recognizer() #init speech_recognition
	#convert .wav file into an AudioFile instance
	audioFile = sr.AudioFile(inputFile)  
	with audioFile as source:
		recordedAudio = recogonizer.record(source)
	os.remove(inputFile) #remove .wav file
	return recogonizer.recognize_google_cloud(recordedAudio) #call google cloud api to transcribe audio
	

if __name__ == '__main__':
	pass
