# TODO 

## Accuracy improvement
- [ ] use [inflext](https://pypi.org/project/inflect/) to convert arabic numbers to word numbers
## Features
- [ ] work on support audio format list
- [ ] add support for processing m4bs
- [ ] Implement binary search to find audio position from text
## Distribution
- [ ] properly format repository to push a build to pypi
- [ ] create a binary with [PyOxidizer](https://github.com/indygreg/PyOxidizer)
## Other
- [ ] clean up function to delete all intermediate folder
- [ ] Create method to save generated data and to ingest it rather than re-transcribing or re searching 

---

# Finished
- [x] add progress bar when converting/transcribing
- [x] use [fire](https://github.com/google/python-fire) for proper CLI calling than sys.args 