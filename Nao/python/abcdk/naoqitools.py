# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Naoqi tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called naoqi, but risk of masking with the official naoqi.py from Naoqi.

"""Naoqi specific tools"""
print( "importing abcdk.naoqitools" );

import os
import sys
import time
import datetime

import cache
import config
import debug
import evaltools
import filetools
# import path # non on ne peut pas inclure path, car ca fait une boucle d'inclusion
# import system # de meme
import test


"we cut/paste this method here to not having to import the full module (cycle)"  
def isOnNao():
    """Are we on THE real Nao ?"""
    szCpuInfo = "/proc/cpuinfo";
#  if not isFileExists( szCpuInfo ): # already done by the getFileContents
#    return False;
    szAllFile =  filetools.getFileContents( szCpuInfo );
    if( szAllFile.find( "Geode" ) == -1 ):
        return False;
    return True;
# isOnNao - end

"we cut/paste this method here to not having to import the full module (cycle)"  
def getNaoqiPath():
    "get the naoqi path"
    "we cut/paste this method here to not having to import the full module (cycle)"
    s = os.environ.get( 'AL_DIR' );
    if( s == None ):
        if( isOnNao() ):
            s = '/opt/naoqi/';
        else:
            s = '';
    return s;
# getNaoqiPath - end


# import naoqi lib
strPath = getNaoqiPath();
home = `os.environ.get("HOME")`

if strPath == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  #alPath = strPath + "/extern/python/aldebaran"
  alPath = strPath + "\\lib\\"
  alPath = alPath.replace("~", home)
  alPath = alPath.replace("'", "")
  sys.path.append(alPath)
  import naoqi
  from naoqi import ALBroker
  from naoqi import ALModule
  from naoqi import ALProxy
#import inaoqi_d
#from naoqi_d import * # fait crasher sous windows, ca commence bien...

# import naoqi object - end



  
global_getNaoqiStartupTime = time.time();
def getNaoqiStartupTime():
    "return the time in seconds epoch of naoqi start (actually last altools loading)"
    global global_getNaoqiStartupTime;
    return global_getNaoqiStartupTime;
# getNaoqiStartupTime - end

global_getNaoqiStartupTimeStamp = str( datetime.datetime.now() );
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp[0:len(global_getNaoqiStartupTimeStamp)-3]; # enleve les micro secondes!
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp.replace( " ", "_" );
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp.replace( ":", "m" );
  
def getNaoqiStartupTimeStamp():
    "return the time stamp of naoqi start (actually last altools loading) - human readable, printable, usable as a filename"
    global global_getNaoqiStartupTimeStamp;
    return global_getNaoqiStartupTimeStamp;
# getNaoqiStartupTimeStamp - end


def myGetProxy( strProxyName, bUseAnotherProxy = False, strHostName = 'localhost' ):
  "redefinition of the basic getproxy, si it can work from choregraphe or from a python script"
  "bUseAnotherProxy: this proxy is used to unlock another proxy, with the same name"
  "strHostName: use another hostname, WRN: using this option will recreate a new proxy at each CALL => TODO"
  if( bUseAnotherProxy ):
      return myGetProxyNoAddr( strProxyName, True );
  if( strHostName != 'localhost' ):
      return myGetProxyWithAddr( strProxyName, strIP = strHostName );
  obj = cache.getInCache( strProxyName, ALProxy );
  if( obj != None ):
    return obj;
  obj = myGetProxyNoAddr( strProxyName );
  if( obj != None ):
    cache.storeInCache( strProxyName, obj );
  return obj;
# myGetProxy - end

def myGetProxyNoAddr( strProxyName, bUseAnotherProxy = False ):
    debug.debug( "MyGetProxyNoAddr: connecting to '%s'" % (strProxyName) );
    if( config.bInChoregraphe ):
        try:
            obj = ALProxy( strProxyName, bUseAnotherProxy );
            if( not obj or obj == None ):
                debug.debug( "ERR: MyGetProxyNoAddr: couldn't connect to '%s" % (strProxyName) );
                return None;
            obj.ping(); # to validate the right construction
            debug.debug( "INF: MyGetProxyNoAddr: connected to '%s'" % (strProxyName) );
            return obj;
        except RuntimeError, err:
            debug.debug(  "ERR: MyGetProxyNoAddr(%s): Exception catched: %s" % ( strProxyName, err ) );
            return None;
    else:
        # print  "MyGetProxyNoAddr: method disabled";
        # return None;
        return myGetProxyWithAddr( strProxyName );
# myGetProxyNoAddr - end

def myGetProxyWithAddr( strProxyName,  strIP = config.strDefaultIP, nPort = config.nDefaultPort ):
  debug.debug( "MyGetProxyWithAddr: connecting to '%s@%s:%d'" % (strProxyName,strIP,nPort) );
  try:
    obj = ALProxy( strProxyName, strIP, nPort );
    obj.ping(); # to validate the right construction
    if( not obj or obj == None ):
      debug.debug( "ERR: MyGetProxyWithAddr: couldn't connect to '%s@%s:%d' (1)" % (strProxyName,strIP,nPort) );
      return None;
    debug.debug( "INF: MyGetProxyWithAddr: connected to '%s@%s:%d' (1)" % (strProxyName,strIP,nPort) );
    return obj;
  except BaseException, err:
    debug.debug( "ERR: MyGetProxyWithAddr(%s): Exception catched: %s" % (strProxyName,err ) );
    return None;

# various tools

def launchCall( *listArgs ):
  "launch a naoqi call with a various list of argument"
  try:
    print "LaunchCall:", listArgs;
    args = listArgs[0];
    proxy = myGetProxy( args[0] );
    strFuncName = args[1];
    params = args[2];
    print( "LaunchCall: " + strFuncName + " params: " );
    print( params );
    proxy.callPython( strFuncName, *params );
    thread.exit(); # exit thread
  except BaseException, err:
    debug.debug( "MyPCall: Exception catched: %s" % err );
# launchCall - end

def myPCall( proxy, strFuncName, args ):
  try:
    listArgs = [ proxy, strFuncName, args ];
    thread.start_new_thread( LaunchCall, (listArgs,) );
    return;
  except BaseException, err:
    debug.debug( "MyPCall: Exception catched: %s" % err );
# myPCall - end

def postQueueOrders( aListOrder, nDelayBetweenOrderInSec = 0. ):
    """launch a list of naoqi command contiguously"""
    """eg: ["ALLeds = ALProxy( 'ALLeds')", "ALLeds.setIntensity( 'FaceLeds', 0.0 )","ALLeds.fadeRGB( 'FaceLeds', 0x0, 2.0 )" ] """
    def implode(strString,strElem):
        if( nDelayBetweenOrderInSec > 0. ):
            return "%s;time.sleep( %f ); %s " % ( strString, nDelayBetweenOrderInSec, strElem );
        return strString + ";" + strElem;
    strConstructedCommand = reduce( implode, aListOrder )
#    print( "strConstructedCommand: %s" % strConstructedCommand );
    evaltools.asyncEval( strConstructedCommand );
# postQueueOrders - end

class naoqiTask:
    "an interface to a naoqi task (created with pcall)"
    
    def __init__(self, id, strProxyName ):
        self.id = id;                                       # the naoqi ID
        self.strProxyName = strProxyName;       # the proxy that handle this task
    # __init__ - end
    
    def isFinished( self ):
        "is the process finished ?"
#        time.sleep( 0.05 ); # time for things to be resfreshed (join/poll or ...) # the time to create the proxy is sufficient
        proxy = myGetProxy( self.strProxyName );
        try:
            #~ proxy.wait( self.id, 1 ); # wait a minimal time
            #~ return True;
            return not proxy.isRunning( self.id );
        except:
            pass  # error => task finished
        return False;
    # isFinished - end
    
    def stop( self ):
        "stop the process"
        "return -1 if it hasn't been really stopped"
        proxy = myGetProxy( self.strProxyName );
        try:
            proxy.stop( self.id ); # wait a minimal time
            return isFinished();
        except:
            pass  # error => task finished or ...
        return True;
    # isFinished - end
    
# class naoqiTask - end


def getNaoqiVersion():
    "get the naoqi version"
    mem = myGetProxy( 'ALMemory' );
    return mem.version();
# getNaoqiPath - end



def autoTest():
    if( test.isAutoTest() ):
        test.activateAutoTestOption();
        postQueueOrders( ["import naoqitools", "ALLeds = naoqitools.myGetProxy( 'ALLeds')", "ALLeds.setIntensity( 'FaceLeds', 1.0 )","ALLeds.fadeRGB( 'FaceLeds', 0xFF, 2.0 )" ] );
# autoTest - end
    

autoTest();