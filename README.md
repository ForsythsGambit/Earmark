# Earmark

## Overview
Earmark is a tool intended to aid reading while switching between an ebook and audiobook by providing functionality similair to amazon's whisperSync.
This is accomplished by transcribing the first 15 seconds of each file in an audiobook and indentifying the absolute kindle location where the text occurs via this [method](https://wiki.mobileread.com/wiki/Page_numbers#Implementation). There is currently only support for audiobooks which are a folder of parts (typically mp3 files, but ffmpeg should support others provided the necessary codecs). Support for m4b files and calculating locations based on time stamps is planned, but has not yet been implemented. 

**Please note** this requires you to have a copy of both: the .mobi file of your ebook and the audio files of your audiobook. If you have epub files I recommend using calibre to convert to mobi, this is my work flow. In addition this project currently and will only support unencrypted mobi files. Circumventing the drm of your purchased ebook is both potentially illegal and outside the purview of this project.

## Installation
1. Install the dependencies via `pip install -r requirements.txt`
2. Install ffmpeg and either place the executable in the same directory or ensure it is on your path
3. Setup google cloud as explained in the section below
4. profit?

### Google Cloud
This project uses google cloud via [sound_recognition](https://pypi.org/project/SpeechRecognition/) for the transcription of audio snippets, refer to this [guide](https://cloud.google.com/speech-to-text/docs/transcribe-api) on how to setup an account. The path to your API key must be specified in a `.env` file as described below:
```
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-cloud-key.json"
```
If you receive an error claiming your key was not found try alternating from a absolute path to a relative one or vice versa. 

I selected Google Cloud for the following: New users recieve a 300$ credit for the first 90 days as well free transcription of 60 minutes of audio free a month. In addition the costs of transcription should you somehow surpass this amount is negligible.


Alternatively however,  you can edit the `transcribe` function in `audio.py` and replace `recognize_google_cloud` with your prefered API/local model should you so desire. Refer to [sound_recognition](https://pypi.org/project/SpeechRecognition/) for setup instructions on how to configure your selected transcriber.


## Usage
The Earmark class provides an object oriented wrapper around the functions of `audio.py` and `search.py` for your convenience. Ensure you have edited `config.toml` with the appropriate paths and values (or passed them appropriately as keyword arguments). 

Earmark can be used in two ways, either as a command line interface or as python module.

### Module
To use as a module see the code below
```
import earmark
em = earmark.Earmark(configPath="config.toml")
em.run()
```

### CLI
Thanks to the wonderful [fire](https://github.com/google/python-fire) Earmark now has a CLI! Simply execute it as follows:
```
$ python3 earmark.py --cfg=config.toml run
```
or, assuming your python installation matches the shebang:
```
./earmark.py --cfg=config.toml run
```
Bam! And thats it!

---
It will now transcribe segments of your audiobook and identify the respective kindle locations (nearly) automatically! Be advised user input may be needed to select correctly matching text if it cannot be detemined automatically.

The output will be printed into a json file, `output.json` in the same directory by default.

The transcribed text will be stored to a local json file (as specified in the config file) and by default on successive runs will be used rather than retranscribing. Please be sure to disable this when using Earmark with a new book.


## Roadmap
- optimization of `compareText()` is needed
- properly package as module
- see `todo.md` for more

## Attribution
This project would have been impossible without the fine work of the devs who wrote [kindle-unpack](https://github.com/kevinhendricks/KindleUnpack). A copy of the files neccessary for the CLI are included under kindle-unpack/ and are licensed under the GPL v3. See the `COPYING` file in that directory for more information or refer to the link above to the view the source code beyond what is used in this project. 

## Distribution
Per the license of kindle-unpack, this project too is licensed under the GPL v3. Refer to `LICENSE` with any questions or concerns. 

