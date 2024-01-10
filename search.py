import logging
import sys
import os
import subprocess
from bs4 import BeautifulSoup
from thefuzz import fuzz
import math

def dumpMobi(mobiPath, force=False):
	"""dumps mobi file to a folder via kindle unpack"""
	workingDirectory = os.getcwd()
	logging.info("starting dumpMobi")
	if "dump" not in os.listdir(workingDirectory):
		#make dump directory if not found
		logging.info(f"Making mobi dump directory")
		os.mkdir('dump')
	fileSplit = mobiPath.split(".")
	if len(fileSplit) != 2:
		#ensure valid filename
		logging.exception("Did not receive path to mobiPath with a valid filename")
		raise ValueError
		return None
	filename = os.path.basename(mobiPath)
	filename=filename.split(".")[0]
	
	if filename not in os.listdir(f"{workingDirectory}/dump/"):
		logging.debug(f"Creating subdirectory dump/{filename}")
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

def getContentFiles(inFolder):
	"""Parses passed dumped mobi folder and generates a list of xhtml/html files which contain the books text content"""
	"""With mobi *should* be only one file, the list is a holdover from epub parsing"""		
	#thrawn alliances part 2 starts at loc 540
	#creates list of all files in dumped mobi folder
	fileList=[]
	for root, dirs, files in os.walk(inFolder):
		for file in files:
			filename=os.path.join(root, file)
			split=file.split(".")
			if len(split) == 1:
				#no file extension
				continue
			elif ((split[1] == "html") or (split[1]=="xhtml")):
				fileList.append(filename)

	contentFile=fileList[0]
	if len(fileList) > 1:
		logging.debug(f"{len(fileList)} content files found, expected 1. Keeping first file {contentFile}")
	logging.debug(f"Content files from folder {inFolder}: {*fileList,}")
	#location: part0011.xhtml, line 96
	return contentFile

def findMatches(inFile, target, confidenceLevel=80):
	"""Parses the specified xhtml/html file within the specified ebook and searche ebook line which matches the transcripted text"""
	matches = [] #list of strings matching transcription *should* only be one match ideally but ynk. 
				 #Format: [(confidence level, matching string, path to file, tagged html)] note: the unaltered line will be stored, not the adjusted one. 
	with open(inFile, "r") as html:
		soup=BeautifulSoup(html, "xml", from_encoding="utf-8") #init beautiful soup
	logging.debug(f"Searching {inFile} for text: {target} with confidence level {confidenceLevel}")
	for tag in soup.body.find_all(True):
		result = compareText(transcribedText=target, ebookText=tag.text, confidenceLevel=confidenceLevel)
		if result != None:
			result["file"]=inFile
			matches.append(result)
			logging.info(f"Found matching string in {inFile} with {confidenceLevel}% accuracy:\n	{target}matches\n	{tag.text}")
		else:
			pass
	return matches

def compareText(transcribedText, ebookText, confidenceLevel=80):
	"""Makes two strings as similar as possible then uses fuzzy text matching to compare two strings"""
	sLine = ebookText
	target = transcribedText 
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
		return {"confidenceLevel" : confidence, "text" : sLine}
	else:
		return None

def findBytes(file, searchText):
	"""Calculates number of bytes preceeding each string found from findMatches"""
	"""it takes the output of findMatches as input"""
	with open(file,"rb") as file:
		position = file.read().find(searchText.encode("utf-8"))
	return position
		
def calculateLocation(numBytes):
	loc = math.floor((numBytes * 2) / 300 + 1)
	return loc

"""wrapper"""

def parseMobi(mobiPath):
	dumpFolder = dumpMobi(mobiPath=mobiPath)
	contentFiles = getContentFiles(inFolder=dumpFolder)
	return contentFiles

def searchEbook(mobiDump, searchText):
	"""wrapper for getContentFiles() and findMatches(), takes an ebook and a snippet of text and returns any matches"""
	matches=[]
	if not isinstance(searchText, list):
		#searchEbook accepts a list of strings to search, if provided a single string add it to a list
		logging.info("searchEbook expected list of search strings but got single string insted. String converted to single element list.")
		text=searchText
		searchText = []
		searchText.append(text)

	for searchString in searchText:
		matches.extend(findMatches(inFile=mobiDump, target=searchString))

	return matches

def searchLocations(excerpts):
	"""takes list of dictionaries and finds their kindle locations"""
	locations = [] #list of dictionaries 
	for excerpt in excerpts:
		loc=calculateLocation(findBytes(file=excerpt["file"],searchText=excerpt["text"]))
		excerpt["location"]=loc
		locations.append(excerpt)
	return locations



if __name__ == '__main__':
	# see comment in main.py
	args = sys.argv
	try:
		globals()[args[1]](*args[2:])
	except IndexError:
		pass

		