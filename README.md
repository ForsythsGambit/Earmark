## Earmark

Earmark is a tool intended to aid reading while switching between an ebook and audiobook, somewhat akin to Amazon's whispersync. 
This is accomplished by transcribing the first few seconds of each file in an audiobook and indentifying where the file picks up in the ebook via an absolute location per the kindle calculation [method](https://wiki.mobileread.com/wiki/Page_numbers#Implementation). Support is currently only planned for audibooks broken up into mp3 segments, although support for 
.m4b would be nice down the line.

Please note this requires you to have a copy of both: the .mobi file of your ebook and the mp3 files of your audiobook.

### Installation
1. Install the dependencies via `pip install -r requirements.txt`
2. Install ffmpeg and either place the executable in the same directory or ensure it is on your path
3. Setup google cloud as explained in the section below 
4. profit?

#### Google Cloud
This project uses google cloud via [sound_recognition](https://pypi.org/project/SpeechRecognition/) for transcription of audio snippets, refer to this [guide](https://cloud.google.com/speech-to-text/docs/transcribe-api) on how to setup an account. The *absolute* path to your API key must be specified in a `.env` file as described below:
```
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-cloud-key.json"
```

Alternatively you can edit the `transcribe` function in `audio.py` and replace `recognize_google_cloud` with your prefered API/local model. Refer to [sound_recognition](https://pypi.org/project/SpeechRecognition/) for setup instructions.


### Usage
The procssing is split between two files, `audio.py` and `search.py` per their respective tasks.
Each function *can* be called individually should you so desire, but wrappers have been written to
streamline usage as much as possible.
An example is shown below:
```
import audio
import search
import json

transcriptions = audio.processAudiobook("/path/to/folder/of/mp3s")
#todo, do this in wrapper ->
text= [transcript["text"] for transcript in transcriptions] 
dump = search.parseMobi(mobiPath="/path/to/your/ebook.mobi")
matches = search.searchEbook(mobiDump=dump, searchText=text)
locations = search.searchLocations(matches)
```
In this example `locations` will be a list of dictionaries, I recommend converting it to json for ease of use
```
with open("output.json", "w") as out:
	out.write(str(locations))
print(jsonData)
```


### Roadmap
- core functionality is roughly finished
- optimization of `compareText()` is needed
- properly package as module
- see `todo.md`