import logging
import sys
import os
import subprocess
from bs4 import BeautifulSoup
from thefuzz import fuzz
import math
from header import *

def dumpMobi(mobiPath, force=False) -> str:
	"""dumps mobi file to a folder via kindle unpack"""
	workingDirectory: str = os.getcwd()
	logging.info(f"Dumping mobi file to {os.getcwd()}/dump")

	if "dump" not in os.listdir(workingDirectory):
		logging.info(f"Making mobi dump directory")
		os.mkdir('dump')
	
	fileSplit:list[str]  = mobiPath.split(".")
	if fileSplit[0] == "":
		"""Relative paths previously broke file extension checking"""
		fileSplit.pop(0)
	if len(fileSplit) != 2:
		#ensure valid filename
		logging.exception(f"Did not receive path to mobiPath with a valid filename (no or multiple extensions), instead received \"{mobiPath}\"")
		raise ValueError
		
	filename: str = os.path.basename(mobiPath)
	filename: str = filename.split(".")[0]
	
	if filename not in os.listdir(f"{workingDirectory}/dump/"):
		logging.info(f"Creating subdirectory dump/{filename}, dumping.")
		subprocess.run(["python","kindle-unpack/kindleunpack.py", mobiPath, f"{workingDirectory}/dump/{filename}"])
	elif force == True:
		logging.info(f"Found pre-existing mobi dump, overwriting.")
		for toDelete in os.listdir(f"{os.getcwd()}/filename"):
			file_path = os.path.join(f"{os.getcwd()}/filename", toDelete)
			os.remove(file_path)
		subprocess.run(["python","kindle-unpack/kindleunpack.py", mobiPath, f"{workingDirectory}/dump/{filename}"])
	else:
		logging.info(f"Found pre-existing mobi dump, keeping it.")
	return f"{workingDirectory}/dump/{filename}"

def getContentFile(inFolder: str) -> str:
	"""Parses passed dumped mobi folder and generates a list of xhtml/html files which contain the books text content"""
	"""With mobi *should* be only one file, the list is a holdover from epub parsing"""		
	#thrawn alliances part 2 starts at loc 540
	#crea[{"confidenceLevel" : int, "text" : matching text, "file" : path to html file}]tes list of all files in dumped mobi folder
	logging.info("Getting content file")
	fileList: list[str] = []

	for root, dirs, files in os.walk(inFolder):
		for file in files:
			filename=os.path.join(root, file)
			split=file.split(".")
			if len(split) == 1:
				#no file extension
				continue
			elif ((split[1] == "html") or (split[1]=="xhtml")):
				fileList.append(filename)

	if len(fileList) == 0:
		logging.CRITICAL(f"No html file found in dump directory {inFolder}")
		raise FileNotFoundError
	elif len(fileList) > 1:
		logging.debug(f"{len(fileList)} content files found, expected 1. Keeping first file {contentFile}")
	else:
		#all good
		contentFile: str = fileList[0]	
	logging.info(f"Content file {contentFile} found in folder {inFolder}")
	return contentFile

def findMatch(inputFile: str, searchText: str, confidenceLevel: int = 80, poorMatchMargin:int = 10, promptPoorMatches: bool = True) -> Match:
	"""Parses the specified xhtml/html file within the specified ebook and searche ebook line which matches the transcripted text"""
	matches = [] #list of dictionaries of strings matching transcription *should* only be one match ideally but ynk. 
				 #Format: [{"confidenceLevel" : int, "text" : matching text, "file" : path to html file, "location" : int}] note: the unaltered line will be stored, not the adjusted one. 
	poorMatches: list[Match] = []

	with open(inputFile, "r") as html:
		soup=BeautifulSoup(html, "xml", from_encoding="utf-8") #init beautiful soup
	
	logging.debug(f"Searching {inputFile} for text: {searchText} with confidence level {confidenceLevel}")
	for tag in soup.body.find_all(True):
		result: Match = compareText(transcribedText=searchText, ebookText=tag.text, confidenceLevel=confidenceLevel-poorMatchMargin)
		if result != None:
			result.file=inputFile
			result.location=None
			if result.confidenceLevel >= confidenceLevel:
				matches.append(result)
			elif result.confidenceLevel >= (confidenceLevel-poorMatchMargin):
				#fall back list if no matches meet confidence level
				poorMatches.append(result)
			logging.info(f"Found matching string with {result.confidenceLevel}% accuracy in {inputFile}:\n	{searchText}matches\n	{tag.text}")
		else:
			pass
	if len(matches) > 1:
		result = max(matches, key=lambda x: x.confidenceLevel) #one liner to select highest confidence match
	else:
		try:
			result = matches[0]
		except IndexError:
			#list is empty because no matches were found, if searchUntilMatch is True will execute again with lower confidence
			logging.info(f"No matching text found for string {searchText}")
			print(f"No matches found for transcribed string:\n-{searchText}")
			if len(poorMatches) >= 1:
				if promptPoorMatches:
					print("="*90)
					print(f"However poorer match(es) were found with at least {confidenceLevel-poorMatchMargin} certainty")
					print(f"If one of the text(s) below is the correct match for the transcribed text [1] please enter its number, or 0 if none.")
					print(f"[0] : {searchText}")
					for index, match in enumerate(poorMatches):
						print(f"[{index+1}] : {match.text}")
					inp=input("Enter correct string number, or 0 to skip: ")
					if inp not in range(1,len(poorMatches)+1):
						result = None
					else:
						logging.info(f"User selected correct matching string")
						result=poorMatches[inp-1]
				else:
					result = max(poorMatches, key=lambda x: x.confidenceLevel) #one liner to select highest confidence match
			else:
				print(f"Nor any matches within {poorMatchMargin}% of {confidenceLevel}.")
	return result

def compareText(transcribedText, ebookText, confidenceLevel=80) -> Match: 
	"""Makes two strings as similar as possible then uses fuzzy text matching to compare two strings"""
	sLine = ebookText
	searchText = transcribedText 
	line = sLine.lower() #the transcription will be all lowercase so this will improve accuracy
	#split strings by whitespace to count words
	tempTarg=searchText.split()
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
	confidence = fuzz.ratio(searchText, lineText) 
	if confidence  > confidenceLevel:
		return Match(confidenceLevel = confidence, text = sLine, file = None, location = None) #{"confidenceLevel" : confidence, "text" : sLine}
	else:
		return None

def findBytes(file, searchText):
	"""Calculates number of bytes preceeding each string found from findMatch"""
	"""it takes the output of findMatch as input"""
	with open(file,"rb") as file:
		position = file.read().find(searchText.encode("utf-8"))
	logging.info(f"Found byte position: {position} of searchText {searchText}")
	return position
		
def calculateLocation(numBytes):
	loc = math.floor((numBytes * 2) / 300 + 1)
	logging.info(f"Found kindle location: {loc} for byte position: {numBytes}")
	return int(loc)


if __name__ == '__main__':
	pass

		