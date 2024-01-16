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
		supportedAudioFormats = ["mp3","wav", "ogg", "m4a", "flac"] #todo
		preppedAudioFiles=[]
		transcriptions = []
		workingDirectory = os.getcwd()
		files=os.listdir(self.audiobookDirectory)
		logging.debug(f"Found {len(files)} files in {self.audiobookDirectory}")
		if "temp" not in os.listdir(workingDirectory):
			os.mkdir("temp")
			logging.debug("Making temp folder for audio files")
		#fileProcessBar = tqdm(files)
		print("Prepping audio files...")
		for file in tqdm(files):
			#fileProcessBar.set_description(f"Processing audio file: {file}")
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
				preppedAudioFiles.append(audio.prepFile(f"{self.audiobookDirectory}/{file}"))
		logging.info(f"Processed {len(preppedAudioFiles)} files: {*preppedAudioFiles,}")
		#transcriptionBar = tqdm(preppedAudioFiles)
		print("Transcribing audio files...")
		for file in tqdm(preppedAudioFiles):
			#transcriptionBar.set_description(f"Transcribing audio clip: {os.path.basename(file)}")
			dict={}
			dict["file"]=file
			dict["text"]=audio.transcribe(file)
			transcriptions.append(dict)
		logging.info(f"Transcribed {len(transcriptions)} files")
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