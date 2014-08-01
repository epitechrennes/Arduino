# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Leds tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called file, but risk of masking with the class file.

"""Leds"""
print( "importing abcdk.leds" );

import time

import naoqitools


def rotateEyes( nColor, rTime, nNbrTurn ):
  # launch a leds animation using one color
  leds = naoqitools.myGetProxy( "ALLeds" );
  nNbrSegment = 8;
  for i in range( nNbrSegment*nNbrTurn ):
    leds.post.fadeRGB( "FaceLed%d" % (i%nNbrSegment) , nColor, rTime );
    leds.post.fadeRGB( "FaceLed%d" % (i%nNbrSegment) , 0x000000, rTime*1.25 );
    time.sleep( rTime*0.25 );
  time.sleep( rTime*0.5 ); # wait last time
# circleLedsEyes - end