#!/usr/bin/python3
import ffmpy
import sys


def prepFile(inFile, time=15):
	ff = ffmpy.FFmpeg(
		inputs={
			inFile : None
		},
		outputs={
			inFile.split(".")[0]+".wav": f"-t {time} -loglevel error" #this splits inFile at the `.` , takes the first half and adds .wav as the file extension
		}
	)
	ff.run()

if __name__ == '__main__':
	# little bit of stackoverflow magic which should let me call functions from the command like so:
	#python3 main.py trimFle test.mp3 ttest.mp3
	args = sys.argv
	# args[0] = current file
	# args[1] = function name
	# args[2:] = function args : (*unpacked)
	try:
		globals()[args[1]](*args[2:])
	except IndexError:
		#script was called without any commandline arguments, otherwise it would error with IndexError
		pass
