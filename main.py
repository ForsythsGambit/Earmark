#!/usr/bin/python3
import speech_recognition as sr
import zipfile
from bs4 import BeautifulSoup
from thefuzz import fuzz 
import ffmpy
import sys
import dotenv
import os

"""Transcription Functions"""

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


""" Ebook search functions"""

def getContentFiles(inFile):
	"""Parses passed epub file and generates a list of xhtml/html files which contain the books text content"""
	#book=epub.read_epub(inFile)
	#thrawn alliances part 2 starts at loc 540
	with zipfile.ZipFile(inFile, "r") as epub:
		allFiles=epub.namelist()
		#creates list of all xhtml/html files, which will contain actual text content
		fileList = [file.split(".") for file in allFiles]
		fileList = [file for file in fileList if len(file)==2]
		fileList = [file[0]+".xhtml" for file in fileList if file[1]==("xhtml" or "html")]
		#print(*fileList, sep="\n")
		#location: part0011.xhtml, line 96
	return fileList

def findMatches(ebook, inFile, target, confidenceLevel=80):
	"""Parses the specified xhtml/html file within the specified ebook and searche ebook line which matches the transcripted text"""
	matches = [] #list of strings matching transcription *should* only be one match ideally but ynk. 
				 #Format: [(confidence level, matching line, path to file)] note: the unaltered line will be stored, not the adjusted one. 
	with zipfile.ZipFile(ebook, "r") as epub:
		selectedFile = epub.read(inFile)
		#with open(selectedFile, 'r', encoding="utf-8") as file:
		soup=BeautifulSoup(selectedFile, "html.parser") #init beautiful soup
		body=soup.find("body") #select only the body
		if body:
			for sLine in body.stripped_strings:
				line = sLine.lower() #the transcription will be all lowercase so this will improve accuracy

				#split strings by whitespace to count words
				tempTarg=target.split()
				tempLine=line.split()
				
				finLine = []
				#trim text from ebook to same length of transcription for better comparison
				if len(tempLine) > len(tempTarg):
					for word in tempLine:
						if len(finLine) < len(tempTarg):
							finLine.append(word)
				else:
					finLine=tempLine
				
				lineText = " ".join(finLine)
				confidence = fuzz.ratio(target, lineText) 
				if confidence  > confidenceLevel:
					"""
					print(f"Transcribed text:\n{target}")
					print(f"Matching text:\n{lineText}")
					print(f"Confidence: {confidence}")
					"""
					matches.append((confidence, sLine, inFile)) 
				else:
					pass
					#print(f"Confidence level of {fuzz.ratio(target, lineText)} too low")
		else:
			#no body found
			pass
	return matches

def searchEbook(ebook, target):
	"""wrapper for getContentFiles() and findMatches(), takes an ebook and a snippet of text and returns any matches"""
	matches=[]
	for file in getContentFiles(ebook):
		#print(f"parsing {file}")
		matches.extend(findMatches(ebook, file, target))
	if len(matches) > 1:
		#found multiple matches that exceed the confidence level
		#deal with this later, ask user to select most correct one?
		return matches
	else:
		return matches[0]

"""Wrapper"""

def run(audioFile, ebook):
	return searchEbook(ebook, transcribe(prepFile(audioFile)))

def display(data):
	"""Formats the data from run() to something user friendly"""
	print(f"Identified match with {data[0]}% confidence in file {data[2]}")

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
		run("test.mp3", "Alliances.epub")