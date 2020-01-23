import glob
import os
import sys
import argparse
import subprocess
import time
import pyodbc
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log

def main():   
	'''
	do the thing
	'''

	for audioFile in os.listdir('/Users/specpa7/Desktop/Jean_python/audio'):
		audioFileName, ext = os.path.splitext(audioFile)
		audioDir = os.path.join('/Users/specpa7/Desktop/Jean_python/audio',audioFile)
		
		for imgFile in os.listdir('/Users/specpa7/Desktop/Jean_python/img'):
			imgFileName, ext = os.path.splitext(imgFile)
			imgDir = os.path.join('/Users/specpa7/Desktop/Jean_python/img',imgFile)

			if audioFileName == imgFileName and audioFileName != '.DS_Store':
				# Define the directory of the output file
				outputDir = os.path.join('/Users/specpa7/Desktop/Jean_python/output',audioFile)

				# Embed the img and the audio	
				subprocess.call(['ffmpeg', '-i', audioDir, '-i', imgDir, '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"', outputDir])

				# delete the old files
				# os.remove(audioDir)
				# os.remove(imgDir)

			else: 
				print("No corresponding cover photo found!")

		


if __name__ == '__main__':
	main()
	log.log("complete")
