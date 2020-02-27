import glob
import os
import os.path
import sys
import argparse
import subprocess
import time
import pyodbc
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
from shutil import move

def main():   
	'''
	do the thing
	'''
	
	for file in os.listdir('/Users/specpa7/Desktop/Jean_python/TestFiles'):
		audioDir = '/Users/specpa7/Desktop/Jean_python/TestFiles/' + file + '/' + file + 'd' + '.mp3'
		imgDir = '/Users/specpa7/Desktop/Jean_python/TestFiles/' + file + '/' + file + '.jpg'
		outputDir = '/Users/specpa7/Desktop/Jean_python/TestFiles/' + file + '/' + file + 'd' + '_embedded' + '.mp3'
		
		# Check if the corresponding img exists
		isFile = os.path.isfile(imgDir)
		# Check if the mp3 is already updated
		isEmbedded = os.path.isfile(outputDir)

		if isFile and not isEmbedded:

			# Embed the img and the audio	
			subprocess.call(['ffmpeg', '-i', audioDir, '-i', imgDir, '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"', outputDir])
		
		else: 
			print("No corresponding cover photo found for ", file)

	for file in os.listdir('/Users/specpa7/Desktop/Jean_python/TestFiles'):
		audioDir = '/Users/specpa7/Desktop/Jean_python/TestFiles/' + file + '/' + file + 'd' + '.mp3'
		outputDir = '/Users/specpa7/Desktop/Jean_python/TestFiles/' + file + '/' + file + 'd' + '_embedded' + '.mp3'
		
		# Check if the corresponding img exists
		isFile = os.path.isfile(outputDir)

		if isFile:
			# Replace the files
			move(outputDir, audioDir)


	# for audioFile in os.listdir(audioDir):
	# 	audioFileName, ext = os.path.splitext(audioFile)
	# 	audioPath = os.path.join(audioDir,audioFile)
		
	# 	imgPath = imgDir + audioFileName + '.jpg'
	# 	isFile = os.path.isfile(imgPath)
		

	# 	if isFile: 	
	# 		# Define the directory of the output file
	# 		outputPath = os.path.join(outputDir,audioFile)

	# 		# Embed the img and the audio	
	# 		subprocess.call(['ffmpeg', '-i', audioPath, '-i', imgPath, '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"', outputPath])

	# 		# delete the old files
	# 		# os.remove(audioDir)
	# 		# os.remove(imgDir)

	# 	else: 
	# 		print("No corresponding cover photo found for ", audioFileName)

		


if __name__ == '__main__':
	main()
	log.log("complete")
