## Earmark

Earmark is a tool intended to aid reading while switching between an ebook and audiobook, somewhat akin to Amazon's whispersync. 
This is accomplished by transcribing the first few seconds of each file in an audiobook and indentifying where the file picks up in the ebook via an absolute location per the kindle calculation [method](https://wiki.mobileread.com/wiki/Page_numbers#Implementation). Support is currently only planned for audibooks broken up into mp3 segments, although support for 
.m4b would be nice down the line.

Please note this requires you to have a copy of both: the .epub file of your ebook and the mp3 files of your audiobook.

### Roadmap

- Trimming, converting, and transcribing a snippet of an audiobook segment is finished.
- Searching the epub for the transcribed text and identifying its location (per the kindle calculation [method](https://wiki.mobileread.com/wiki/Page_numbers#Implementation)) is in development.

### Google Cloud
This project uses google cloud via [sound_recognition](https://pypi.org/project/SpeechRecognition/) for transcription of audio snippets, refer to this [guide](https://cloud.google.com/speech-to-text/docs/transcribe-api) on how to setup an account. The *absolute* path to your API key must be specified in a `.env` file as described below:
```
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-cloud-key.json"
```

Alternatively you can edit the `transcribe` function in `main.py` and replace `recognize_google_cloud` with your prefered API/local model. Refer to [sound_recognition](https://pypi.org/project/SpeechRecognition/) for setup instructions.
