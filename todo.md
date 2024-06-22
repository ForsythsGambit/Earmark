# TODO 

## Accuracy improvement
- [ ] use [inflext](https://pypi.org/project/inflect/) to convert arabic numbers to word numbers
- [ ] remove raw unicode strings from ebook text, ie emdashes like this `\u2014`
- [ ] Check ebook text for novel words/names that aren't normal english and remove them from both strings for better matching
	- especially sanderson words, like allomancy, Kandra, Kolloss, Feruchimist etc which wont have been transcribed correctly.
- [ ] optimize searching of book, if the audio files are in order then we shouldn't need to check previous parts of it assuming that our match is good enough.
## Features
- [ ] work on support audio format list
- [ ] add support for processing m4bs
## Distribution
- [ ] properly format repository to push a build to pypi
- [ ] create a binary with [PyOxidizer](https://github.com/indygreg/PyOxidizer)
## Other
- [ ] **Create config option to use api cache instead of re transcribing**
- [ ] clean up function to delete all intermediate folder
- [ ] Use path objects rather than strings
- [ ] Create method to save generated data and to ingest it rather than re-transcribing or re searching 

---

# Finished
- [x] add progress bar when converting/transcribing
- [x] use [fire](https://github.com/google/python-fire) for proper CLI calling than sys.args 