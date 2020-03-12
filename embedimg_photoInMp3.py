#!/usr/bin/env python
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

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, help="The directory under which will be found .jpg files wich will be embbeded into MP3s")
parser.add_argument("--mode", required=True, choices=["single","batch"], help="Single to process photo for a single recording rather than a batch")
args = parser.parse_args()


rootDir = args.source


def main():   
	'''
	do the thing
	'''
	# Mode Single
	if args.mode == 'single':
		audioDir = rootDir + '/' + os.path.basename(rootDir) + 'd' + '.mp3'
		imgDir = rootDir + '/' + os.path.basename(rootDir) + '.jpg'
		outputDir = rootDir + '/' + os.path.basename(rootDir) + 'd' + '_embedded' + '.mp3'

		# Check if the corresponding img exists
		isFile = os.path.isfile(imgDir)
		# Check if the mp3 is already updated
		isEmbedded = os.path.isfile(outputDir)

		if isFile and not isEmbedded:

			# Embed the img and the audio	
			subprocess.call(['ffmpeg', '-i', audioDir, '-i', imgDir, '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"', outputDir])
		else: 
			print("No corresponding cover photo found for ", file)

		# Replace the files
		move(outputDir, audioDir)	

	# Mode Batch
	elif args.mode == 'batch':
		for file in os.listdir(rootDir):
			audioDir = rootDir + '/' + file + '/' + file + 'd' + '.mp3'
			imgDir = rootDir + '/' + file + '/' + file + '.jpg'
			outputDir = rootDir + '/' + file + '/' + file + 'd' + '_embedded' + '.mp3'
			
			# Check if the corresponding img exists
			isFile = os.path.isfile(imgDir)
			# Check if the mp3 is already updated
			isEmbedded = os.path.isfile(outputDir)

			if isFile and not isEmbedded:

				# Embed the img and the audio	
				subprocess.call(['ffmpeg', '-i', audioDir, '-i', imgDir, '-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"', outputDir])
			
			else: 
				print("No corresponding cover photo found for ", file)

		for file in os.listdir(rootDir):
			audioDir = rootDir + '/' + file + '/' + file + 'd' + '.mp3'
			outputDir = rootDir + '/' + file + '/' + file + 'd' + '_embedded' + '.mp3'
			
			# Check if the corresponding img exists
			isFile = os.path.isfile(outputDir)

			if isFile:
				# Replace the files
				move(outputDir, audioDir)		


if __name__ == '__main__':
	main()
	log.log("complete")
