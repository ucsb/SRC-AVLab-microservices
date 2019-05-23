#!/usr/bin/env python
'''
Make Derivatives for Web

walk the "repo" directory, select a source .WAV file preferring the "Broadcast" .WAV if available,
and create a audio level normalized MP3 file for any recording that doesn't already have an MP3 file.

'''
import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, help="The directory under which will be found .WAV files wich will be converted to MP3s")
parser.add_argument("--destination", help="The directory where the new MP3 files will be created.  If not specified the MP3 will be placed in the same directory as the source .WAV")
parser.add_argument("--normalizationScheme", help="The normalizaton scheme to be used.  Either 'ebu' or 'rms'. EBU is the default scheme. ")
args = parser.parse_args()

rootDir = args.source

# these functions also exist in inventory.py
def ismp3(path):
    if path.endswith('.mp3'):
        return True
    else:
        return False


def mp3sInFileList(fileList):
    mp3files = []
    for fname in fileList:
        if(ismp3(fname)):
            mp3files.append(fname)
    return mp3files
# end overlap with inventory.py


def isNonMasterWav(path):
    if path.endswith('.wav') and not path.endswith('m.wav'):
        return True
    else:
        return False


def isBroadcastWav(fileList):
    broadcastWavExists = False
    for fname in fileList:
        if(fname.endswith('b.wav')): # there may be some false positives with this test
            broadcastWavExists = True
            broadcastWav = fname
    if(broadcastWavExists):
        return broadcastWav
    else:
        return False


def isNotEdison(dirName):
    # 2018-10-10 for filtering out non-edison recordings
    # logic is a bit convoluted but...  this function returns True for most dirnames
    # but returns False for the Edison dirnames
    if dirName.startswith('cusb_ed_'):
        return False
    else:
        return True


def pickSourceWav(fileList):
    for fname in fileList:
        if(fname.endswith('.wav') and not fname.endswith('m.wav')):
            return fname


def makeMp3(dirName, sourceBroadcastWav):
    global args
    if dirName == rootDir:
        return
    destinationFileName, wav = os.path.splitext(sourceBroadcastWav)
    print("\ncreating a normalized MP3 file for: " + dirLastPart + "/")

    # defalut normalization scheme is ebu but you can specify one on the command line if you like
    if(args.normalizationScheme != None):
        print("using normalization scheme from command line")
        normalizationScheme = args.normalizationScheme
    else:
        print("using default ebu normalization scheme")
        normalizationScheme = "ebu"


## example command invocation:    python ffmpeg-normalize -o ~/Downloads/temp.mp3 --audio-codec libmp3lame  -nt ebu -v --target-level -16
    # here we call 'ffmpeg-normalize' with various flags so it will create the normalized MP3 file. LUFS -16
    # 05.02.2019, added "--dual-mono" at the end of the below call to attempt to fix pecularities, SE
    subprocess.call(["python", "/usr/local/bin/ffmpeg-normalize", dirName + "/" + sourceBroadcastWav, "-o", dirName + "/" + destinationFileName + 'd.mp3', "-nt", normalizationScheme, "--target-level", "-16", "--audio-codec", "libmp3lame", "--output-format", "mp3", "--audio-bitrate", "320k", "--true-peak", "-0.1", "--dual-mono"])


def main():
    '''
    main() function runs if this script is called directly by the python interpreter rather than being imported into some other Python script
    '''
    global conf
    global dirLastPart
    for dirName, subdirList, fileList in os.walk(rootDir):
        theTuple = os.path.split(dirName)
        dirLastPart = theTuple[1]
        if(any(ismp3(n) for n in fileList)):
            print("skipping " + dirLastPart + "/ as it already has an MP3 " + "\n")
            mp3sInDir = mp3sInFileList(fileList)
        # elif(isNotEdison(dirLastPart)):
        #     print("skipping " + dirLastPart + "/ as it is Not an edison" )
        else:
            # print(dirName + " NEEDS an MP3 added")
            if(any(isBroadcastWav(n) for n in fileList)):
                broadcastWav = pickBroadcastWav(fileList)
                makeMp3(dirName, broadcastWav)
            elif(any(isNonMasterWav(n) for n in fileList)):
                ## no broadcast wav in dir to serve as source so we search for plain .wav
                sourceWav = pickSourceWav(fileList)
                makeMp3(dirName, sourceWav)
            else:
                print("skipping " + dirName + "/ as no .WAV  was found in this directory to use as a source." + "\n")

    print("\n")

if __name__ == '__main__':
    main()
