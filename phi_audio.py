'''
typically called by filemaker script in the EDVR database in response to user clicking the "capture" checkbox.

Calling filemaker script: indv_transferred
parameter passed:  item barcode
	example:
		ack_col_56346f_01_w206626_03
		ucsb_ed_51193_01_9050_0a

renames files in the archive
the barcode passed in as a param starts with 'ucsb_' but the filenames of recordings stored in the repo start with 'cusb_'

as a subprocess this script calls "makebroadcast.py" which runs a ffmpeg process
as a subprocess this script calls bwfmetaedit
as a subprocess this script calls hashmove.py
as a subprocess this script may call makesip.py

'''
import os
import sys
import getpass
import time
import subprocess
import argparse
import pyodbc
###UCSB modules###
import config as rawconfig
import util as ut
from logger import log
import mtd
import makestartobject as makeso

def wait_for_wavelab(kwargs):
	'''
	try to run ffprobe on the files
	if we can't it means it's still oopen in Wavelab
	'''
	###VERIFY WE CAN WORK ON THIS FILE###
	startTime = time.time()
	timeDiff = time.time() - startTime
	#try to rename it once every 2 seconds for 30 seconds
	#this basically waits for the user to close this file in Wavelab
	while timeDiff < 30:
		try:
			if os.path.exists(os.path.join(kwargs.archDir, kwargs._fname)) and 'ucsb_' in kwargs._fname:
				os.rename(os.path.join(kwargs.archDir, kwargs._fname), kwargs.archiveFP_pre) #changes filenames to cusb ??
			if os.path.exists(os.path.join(kwargs.broadDir, kwargs._fname))and 'ucsb_' in kwargs._fname:
				os.rename(os.path.join(kwargs.broadDir, kwargs._fname), kwargs.broadcastFP)
			elif not os.path.exists(kwargs.archiveFP_pre) or not os.path.exists(kwargs.broadcastFP):
				print "buddy, something went wrong"
				sys.exit()
			else:
				return
		except OSError,e:
			time.sleep(2)
			timeDiff = time.time() - startTime
	if timeDiff	>= 30.0:
		log(**{"message":"attempt to process " + kwargs.fname + " timed out because this file is open in another program","level":"warning","print":True})
		log(**{"message":"Please check that this file is closed in Wavelab","print":True})
		foo = raw_input("To re-try processing, uncheck and re-check the 'transferred' box on this matrix's FileMaker record")
		sys.exit()

def delete_bs(kwargs):
	###delete bs###
	with ut.cd(kwargs.archDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".mrk"):
					try:
						os.remove(f)
					except:
						pass
	with ut.cd(kwargs.broadDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"):
					try:
						os.remove(f)
					except:
						pass

def init():
	'''
	initialize VARS
	'''
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="processes disc transfer files during digitization")
	parser.add_argument("input",help="the barcode of the disc you'd like to process")
	args = parser.parse_args()
	kwargs = ut.dotdict({})
	kwargs.qcDir = conf.NationalJukebox.PreIngestQCDir
	kwargs.batchDir = conf.NationalJukebox.BatchDir
	kwargs.archDir = conf.NationalJukebox.AudioArchDir
	kwargs.broadDir = conf.NationalJukebox.AudioBroadDir
	kwargs.barcode = args.input #grab the lone argument that FM provides
	kwargs._fname = kwargs.barcode + ".wav"
	log(**{"message":"processing " + kwargs.barcode,"print":True})
	if not os.path.exists(os.path.join(kwargs.archDir, kwargs._fname)) or not os.path.exists(os.path.join(kwargs.broadDir, kwargs._fname)):
		log(**{"message":"file " + kwargs._fname + " missing from arch or broad dir, not processed","level":"error","print":True})
		#print "Please check that you saved the file to the right directory in Wavelab before indicating that it was transferred"
		foo = raw_input("Please check that the file was named correctly and saved to the correct directory")
		sys.exit()
	else:
		if 'ucsb_' in kwargs._fname:
			os.rename(os.path.join(kwargs.archDir, kwargs._fname),  os.path.join(kwargs.archDir,  kwargs._fname).replace("ucsb_","cusb_"))
			os.rename(os.path.join(kwargs.broadDir, kwargs._fname), os.path.join(kwargs.broadDir, kwargs._fname).replace("ucsb_","cusb_"))
		kwargs.barcode = kwargs.barcode.replace("ucsb","cusb") #stupid, stupid bug. The printed barcodes start with 'ucsb_' rather than using the sigla 'cusb_'
		kwargs.fname = kwargs.barcode + ".wav"
		kwargs.archive_fname = kwargs.barcode + "m.wav" #make the new filename
		kwargs.broadcast_fname = kwargs.barcode + ".wav"
		kwargs.archiveFP_pre = os.path.join(kwargs.archDir, kwargs.fname)
		kwargs.archiveFP_post = os.path.join(kwargs.archDir, kwargs.archive_fname)
		kwargs.broadcastFP = os.path.join(kwargs.broadDir, kwargs.fname)
	return args, kwargs

def mark_processed_FM(file):
	sqlstr = """update SONYLOCALDIG set audioProcessed='1' where filename='""" + file + """'"""
	mtd.insertFM(sqlstr, pyodbc.connect(conf.NationalJukebox.cnxn))

def main():
	'''
	do the thing
	'''
	log("started")
	args, kwargs = init()
	wait_for_wavelab(kwargs)
	###make broadcast master###
	output = subprocess.check_output([conf.python, os.path.join(conf.scriptRepo,'makebroadcast.py'), '-i', kwargs.broadcastFP,'-f','-nj']) #makebroadcast with fades, national jukebox project file naming
	log(output)
	#pop them into the qc dir in a subdir named after their filename
	#hashmove makes end dir if it doesnt exist already
	output = subprocess.check_output([conf.python, os.path.join(conf.scriptRepo,'hashmove.py'), kwargs.broadcastFP, os.path.join(kwargs.qcDir, kwargs.barcode)])
	log(output)
	###end make broadcast master###
	###make archive master###
	os.rename(kwargs.archiveFP_pre, kwargs.archiveFP_post)
	log("file " + kwargs.archiveFP_pre + "renamed " + kwargs.archiveFP_post)
	#embed an md5 hash in the md5 chunk
	subprocess.call(['bwfmetaedit','--in-core-remove', kwargs.archiveFP_post])
	subprocess.call(['bwfmetaedit','--MD5-Embed', kwargs.archiveFP_post])
	#move them to qc dir in subdir named after their canonical filename (actual file name has "m" at end)
	output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'), kwargs.archiveFP_post, os.path.join(kwargs.qcDir, kwargs.barcode)])
	log(output)
	#check the box in FM
	mark_processed_FM(args.input)
	#see if this is ready to qc
	subprocess.call([conf.python, os.path.join(conf.scriptRepo, "makesip.py"), "-m", "nj", "-i", kwargs.barcode.strip()])
	###end make archive master###
	delete_bs(kwargs)


if __name__ == '__main__':
	main()
	log("complete")
