import audio
import search
from header import *

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
	def __init__(self, configPath: str = None, **kwargs) -> None:
		"""Two methods of initialization, via key word args. *or* a config file
		if a vaild config file is found any other kwargs will be ignored."""
		
		
		#dictionary mapping strings to corresponding log level so theres no evaluation of strings!
		logLevelDictionary: dict[str, int] = {"debug" : logging.DEBUG, "info" : logging.INFO, "warning" : logging.WARNING, "error" : logging.ERROR, "critical" : logging.CRITICAL}
		initializationArguments: dict = {}

		if configPath != None: #User provided configPath as a command line argument
			with open(configPath, "r") as tomlFile:
				initializationArguments = toml.load(tomlFile)
		elif "cfg" in kwargs: #Alternatively user passed configPath as cfg instead
			with open(kwargs["cfg"], "r") as tomlFile:
				initializationArguments = toml.load(tomlFile)
		else: #configPath not provided, so initializing based on kwargs
			initializationArguments = kwargs
		
		#will use same code to load initArgs into instance atrributes
		#paths
		self.mobiPath: str = initializationArguments["mobiFilePath"]
		self.audiobookDirectory: str = initializationArguments["audiobookDirectoryPath"]
		#values
		self.confidenceLevel: int = initializationArguments["transcriptionConfidenceThreshold"]
		self.poorMatchMargin: int = initializationArguments["poorMatchConfidenceMargin"]
		self.tryApiCacheFirst: bool = initializationArguments["tryApiCacheFirst"]
		self.autoSelectHighest: bool = initializationArguments["autoSelectHighest"]
		"""Initialize logging"""
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
		transcriptions: list[Transcript] = []
		if self.tryApiCacheFirst and self.apiCache:
			logging.info("Using cached transcription data..")
			with open("./apiCache.json", 'r') as apiCache:
				json_data = json.load(apiCache)
			if json_data:
				for item in json_data:
					transcript = Transcript(file=item['file'], text=item['text'])
					transcriptions.append(transcript)
			else:
				logging.info("API Cache empty, reprocessing.")
				logging.info("Processing audiobook..")
				transcriptions = self.processAudiobook()
		else:
			logging.info("Processing audiobook..")
			transcriptions = self.processAudiobook()
		text: list[str] = [transcript.text for transcript in transcriptions]
		dumpedHtmlFile: str = self.parseMobi()
		matches: list[Match] = self.searchEbook(mobiDump=dumpedHtmlFile, searchText=text)
		locations: list[Match] = self.searchLocations(matches)
		dictionaryLocations: list[dict] = [asdict(location) for location in locations]
		jsonData = json.dumps(dictionaryLocations, indent=4)
		
		with open("output.json", "w") as out:
			out.write(str(jsonData))
		print("Results output to output.json")

	def processAudiobook(self) -> list[Transcript]:
		supportedAudioFormats: list[str] = ["mp3","wav", "ogg", "m4a", "flac"] #todo
		preppedAudioFiles: list = []
		transcriptions: list[Transcript] = []
		workingDirectory: str = os.getcwd()
		files: str = os.listdir(self.audiobookDirectory)

		logging.debug(f"Found {len(files)} files in {self.audiobookDirectory}")

		if "temp" not in os.listdir(workingDirectory):
			os.mkdir("temp")
			logging.debug("Making temp folder for audio files")

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
		
		print("Transcribing audio files...")

		for file in tqdm(preppedAudioFiles):
			transcriptions.append(Transcript(file,audio.transcribe(file)))
		
		#Output transcriptions to debug
		for transcript in transcriptions:
			logging.info(f"{transcript.file} : {transcript.text}")

		#cache transcriptions for inspection in a json file, if enabled in config
		if self.apiCache != None:
			try:
				os.remove("apiCache.json")
			except FileNotFoundError:
				pass
			with open(self.apiCache, "w") as cache:
				apiCache = json.dumps([asdict(transcript) for transcript in transcriptions])
				cache.write(apiCache)

		logging.info(f"Transcribed {len(transcriptions)} files")
		os.rmdir("./temp")
		return transcriptions

	def parseMobi(self) -> str:
		dumpFolder: str = search.dumpMobi(self.mobiPath)
		contentFile: str = search.getContentFile(dumpFolder)
		return contentFile #returns path to html file

	def searchEbook(self, mobiDump: str, searchText: list[str]) -> list[Match]:
		"""wrapper for findMatch(), loops over list of strings (or a single one) and finds matches in specified mobi dump"""
		matches: list[Match] = []
		#should only accept a list of strings, not make exceptions!
		""" 
		if not isinstance(searchText, list):
			#searchEbook accepts a list of strings to search, if provided a single string add it to a list
			logging.info("searchEbook expected list of search strings but got single string insted. String converted to single element list.")
			text=searchText
			searchText = []
			searchText.append(text)
		"""
		print("Searching dumped mobi file for matching strings...")
		logging.info("Searching dumped mobi file for matching strings...")
		for searchString in tqdm(searchText):
			matches.append(search.findMatch(inputFile=mobiDump, searchText=searchString, confidenceLevel=self.confidenceLevel, poorMatchMargin=self.poorMatchMargin, promptPoorMatches= not self.autoSelectHighest))

		return matches

	def searchLocations(self, excerpts: list[Match]) -> list[Match]:
		"""takes list of Match dataclases then finds their kindle locations and updates the Match"""
		locations: list[Match] = [] 
		#progress bar uneccessary here
		for excerpt in excerpts:
			if excerpt.file == None or excerpt.text == "" or excerpt.confidenceLevel == 0:
				continue
			position=search.findBytes(filePath=excerpt.file, searchText=excerpt.text)
			location=search.calculateLocation(position)
			excerpt.location=location
			locations.append(excerpt)
		return locations 

if __name__ == "__main__":
	fire.Fire(Earmark)