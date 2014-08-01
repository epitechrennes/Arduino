#!/usr/bin/python
# -*- encoding: UTF-8 -*-
from optparse import OptionParser
from sys import argv, exit, stdin
from naoqi import ALProxy

#IP = "192.168.0.42"
IP = "169.254.0.42"
PORT = 9559

def say(tts, to_say):
  tts.say(to_say)

def main():
  parser = OptionParser(usage="Usage: %prog [options] [phrase1 [phrase2 ...]]")
  parser.add_option("-v", "--volume",
                    action="store", type="int", dest="volume",
                    help=u"définir le volume", metavar="VOL")
  (options, args) = parser.parse_args()
  
  if (options.volume):
    vol = ALProxy("ALAudioDevice", IP, PORT)
    vol.setOutputVolume(min(max(options.volume, 0), 100))

  tts = ALProxy("ALTextToSpeech", IP, PORT)
  tts.setLanguage('French')

  if len(args) == 0:
    line = 1
    while line:
      try:
        line = stdin.readline().strip('\n')
      except KeyboardInterrupt:
        break
      if line:
        say(tts, line)

  else:
    for arg in args:
      say(tts, arg)

if __name__ == "__main__":
  main()

