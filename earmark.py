import audio
import search
import logging
import toml
import os
import json
from datetime import datetime
import fire
from tqdm import tqdm
import time


class Earmark():
	"""Class which houses wrappers for audio&search, provides an oo more user friendly front to interact with Earmark"""
	def __init__(self,configPath=None, **kwargs):
		"""Two methods of initialization, via key word args. *or* a config file
		if a vaild config file is found any other kwargs will be ignored."""
		
		
		#dictionary mapping strings to corresponding log level so theres no evaluation of strings!
		logLevelDictionary = {"debug" : logging.DEBUG, "info" : logging.INFO, "warning" : logging.WARNING, "error" : logging.ERROR, "critical" : logging.CRITICAL}
		initializationArguments={}
		if configPath != None:
			#init Earmark by config file
			with open(configPath, "r") as tomlFile:
				initializationArguments = toml.load(tomlFile)
		elif "cfg" in kwargs:
			with open(kwargs["cfg"], "r") as tomlFile:
				initializationArguments = toml.load(tomlFile)
		else:
			#explicitly told to ignore config file
			initializationArguments = kwargs
				
		#will use same code to load initArgs into instance atrributes
		#paths
		self.mobiPath = initializationArguments["mobiFilePath"]
		self.audiobookDirectory = initializationArguments["audiobookDirectoryPath"]
		#values
		self.confidenceLevel=initializationArguments["transcriptionConfidenceThreshold"]
		self.poorMatchMargin = initializationArguments["poorMatchConfidenceMargin"]
		#logging
		initializationArguments["loggingLevel"]=initializationArguments["loggingLevel"].lower()
		if initializationArguments["loggingLevel"] not in logLevelDictionary:
			initializationArguments["loggingLevel"]="info"
		logging.basicConfig(filename=initializationArguments["loggingOutput"],level=logLevelDictionary[initializationArguments["loggingLevel"]] ,encoding="utf-8")
		with open(initializationArguments["loggingOutput"], "a") as log:
			log.write("="*100)
			log.write("\n")
			log.write(f"{str(datetime.now())}\n")
		#output files
		self.apiCache=initializationArguments["apiCache"]

	def run(self):
		transcriptions = self.processAudiobook()
		for transcript in transcriptions:
			logging.info(f"{transcript['file']} : {transcript['text']}")
		#cache transcriptions for inspection in a json file, if enabled in config
		if self.apiCache != None:
			try:
				os.remove("apiCache.json")
			except FileNotFoundError:
				pass
			with open(self.apiCache, "w") as cache:
				apiCache = json.dumps(transcriptions)
				cache.write(apiCache)
		
		text= [transcript["text"] for transcript in transcriptions]
		dump = self.parseMobi()
		matches = self.searchEbook(mobiDump=dump, searchText=text)
		locations = self.searchLocations(matches)
		jsonData = json.dumps(locations, indent=4)
		with open("output.json", "w") as out:
			out.write(str(locations))
		#print(jsonData)
		print("Results output to output.json")
	def processAudiobook(self):
		preppedAudioFiles=[]
		transcriptions = []
		workingDirectory = os.getcwd()
		files=os.listdir(self.audiobookDirectory)
		if "temp" not in os.listdir(workingDirectory):
			os.mkdir("temp")
			logging.debug("Making temp folder for audio files")
		print("Prepping audio files...")

		mp3Files = [file for file in files if file.endswith(".mp3")] #create list of all mp3 files in dir
		m4bFile = [file for file in files if file.endswith(".m4b")] #create list of all m4b files in dir
		if mp3Files and m4bFile: #if both mp3 and m4b files
			logging.critical("mp3 and m4b files present in directory, unsupported")
			raise ValueError
		elif mp3Files: 
			#transcribe mp3 files
			logging.debug(f"found {len(mp3Files)} mp3 files to process")
			for mp3 in tqdm(mp3Files):
				logging.debug(f"Found file for processing: {mp3}")
				preppedAudioFiles.append(audio.prepFile(f"{self.audiobookDirectory}/{mp3}"))
		elif m4bFile and len(m4bFile)<2:
			logging.debug(f"Found m4b audiobook file {self.audiobookDirectory}{m4bFile[0]}")
			chapters=audio.splitM4b(f"{self.audiobookDirectory}{m4bFile[0]}")
			#logging.debug(f"Split m4b file metadata: \n{json.dumps(chapters, indent=4,sort_keys=True)}")
			for chapter in tqdm(chapters):
				logging.debug(chapters[chapter])
				preppedAudioFiles.append((chapters[chapter]["sliceFile"]))
		elif len(m4bFile) > 1:
			logging.critical(f"Found more than one m4b file!")
		print(preppedAudioFiles, sep="\n")
		logging.info(f"Processed {len(preppedAudioFiles)} file(s): {*preppedAudioFiles,}")
		print("Transcribing audio files...")
		"""
		for file in tqdm(preppedAudioFiles):
			dict={}
			dict["file"]=file
			dict["text"]=audio.transcribe(file)
			transcriptions.append(dict)
		logging.info(f"Transcribed {len(transcriptions)} files")
		"""
		os.rmdir("./temp")
		return transcriptions
		
	def parseMobi(self):
		dumpFolder = search.dumpMobi(self.mobiPath)
		contentFile = search.getContentFile(dumpFolder)
		return contentFile #returns html file

	def searchEbook(self, mobiDump, searchText):
		"""wrapper for findMatch(), loops over list of strings (or a single one) and finds matches in specified mobi dump"""
		matches=[]
		if not isinstance(searchText, list):
			#searchEbook accepts a list of strings to search, if provided a single string add it to a list
			logging.info("searchEbook expected list of search strings but got single string insted. String converted to single element list.")
			text=searchText
			searchText = []
			searchText.append(text)
		print("Searching dumped mobi file for matching strings...")
		for searchString in tqdm(searchText):
			matches.append(search.findMatch(inputFile=mobiDump, searchText=searchString))

		return matches #A list of dictionaries in format: [{"confidenceLevel" : int, "text" : matching text, "file" : path to html file, "location" : int}]

	def searchLocations(self, excerpts):
		"""takes list of dictionaries and finds their kindle locations"""
		locations = [] #list of dictionaries 
		#progress bar uneccessary here
		for excerpt in excerpts:
			if excerpt == None:
				continue
			position=search.findBytes(file=excerpt["file"],searchText=excerpt["text"])
			location=search.calculateLocation(position)
			excerpt["location"]=location
			locations.append(excerpt)
		return locations #list of dictionaries in format: [{"confidenceLevel" : int, "text" : matching text, "file" : path to html file, "location" : int}]

if __name__ == "__main__":
	fire.Fire(Earmark)