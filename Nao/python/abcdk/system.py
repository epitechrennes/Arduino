# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# System tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Aldebaran Behavior Complementary Development Kit: A module for system tools."""
print( "importing abcdk.system" );

import os
import sys
import threading
import time

import config
import debug
import filetools
import naoqitools
import pathtools
import test

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

def isOnWin32():
    "Are we on a ms windows system?"
    # return not isOnNao() and os.name != 'posix';
    return os.name != 'posix';
# isOnWin32 - end

def getNaoIP():
  "get the nao ip address (eth>wifi)"
  if( not isOnNao() ):
    return "";

  try:    
      import socket # under windows, we doesn't have this module
      import fcntl
      import struct
  except:
      return "";
  def get_ip_address( strInterfaceName ):
    "get the ip associated to a linux network interface"
    try:
      sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
#      print( "sock: '%s'" % str( sock ) );
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      strInterfaceName = strInterfaceName[:15];
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      packedInterfaceName = struct.pack( '256s', strInterfaceName );
#      print( "packedInterfaceName: " + str( packedInterfaceName ) );
      ret = fcntl.ioctl(
          sock.fileno(),
          0x8915,  # SIOCGIFADDR
          packedInterfaceName
      );
#      print( "ret: '%s'" % ret );
      ret = ret[20:24];
#      print( "ret: '%s'" % ret );
      return socket.inet_ntoa( ret );
    except:
      return '';
  # get_ip_address - end

  debug.debug( "getNaoIP: getting ethernet" );
  strIP = get_ip_address( 'eth0' );
  if( strIP != '' ):
    return strIP;
  debug.debug( "getNaoIP: getting wifi" );
  return get_ip_address( 'wlan0' );
# getNaoIP - end

# print "getNaoIP(): '%s'" % str( getNaoIP() );

def getNaoIPs():
  "get the nao ips address: [eth,wifi]"
  if( not isOnNao() ):
    return [];

  try:    
      import socket # under windows, we doesn't have this module
      import fcntl
      import struct
  except:
      return "";
  def get_ip_address( strInterfaceName ):
    "get the ip associated to a linux network interface"
    try:
      sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
#      print( "sock: '%s'" % str( sock ) );
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      strInterfaceName = strInterfaceName[:15];
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      packedInterfaceName = struct.pack( '256s', strInterfaceName );
#      print( "packedInterfaceName: " + str( packedInterfaceName ) );
      ret = fcntl.ioctl(
          sock.fileno(),
          0x8915,  # SIOCGIFADDR
          packedInterfaceName
      );
#      print( "ret: '%s'" % ret );
      ret = ret[20:24];
#      print( "ret: '%s'" % ret );
      return socket.inet_ntoa( ret );
    except:
      return '';
  # get_ip_address - end

  return [get_ip_address( 'eth0' ), get_ip_address( 'wlan0' )];
# getNaoIPs - end

import subprocess


class ASyncSystemCallThread( threading.Thread ):
    def __init__(self, strCommandAndArgs, bStoppable = False ):
        threading.Thread.__init__( self );
        self.strCommandAndArgs = strCommandAndArgs;
        self.newProcess = False;
        self.bStoppable = bStoppable;
    # init - end

    def run ( self ):
        debug.debug( "system.asyncSystemCallThread calling '%s'" % self.strCommandAndArgs );
        # mySystemCall( self.strCommandAndArgs );
        if( self.bStoppable and isOnWin32() ):
            self.newProcess = subprocess.Popen( self.strCommandAndArgs );  # sous windows, il ne faut oas mettre shell a true si on veut pouvoir arreter une tache (genre lancer choregraphe)
        else:
            self.newProcess = subprocess.Popen( self.strCommandAndArgs, shell=True ); # , stdin=subprocess.PIPE
        try:
            sts = os.waitpid( self.newProcess.pid, 0 );
        except:
            pass # pid already finished or some erros occurs or under windows ?
        debug.debug( "system.asyncSystemCallThread calling '%s' - end" % self.strCommandAndArgs );
    # run - end

    def stop( self, rTimeOut = 2.0 ):
        "stop the process"
        "return -1 if it hasn't been really stopped"
        if( self.newProcess == False ):
            return -1; # the process hasn't been launch yet !

        if( not self.isFinished() ):
        #~ if(   os.name != 'posix' ):
            #~ # Kill the process using pywin32
            #~ import win32api # install from pywin32-214.win32-py2.6.exe
            #~ print dump( win32api );
            #~ win32api.TerminateProcess( int( self.newProcess._handle ), -1)
            #~ win32api.CloseHandle(self.newProcess._handle);
            #~ import ctypes
            #~ ctypes.windll.kernel32.TerminateProcess(int(self.newProcess._handle), -1)
        #~ else:
            try:
                self.newProcess.terminate(); # warning: require python2.6 or higher # fonctionne mais shell doit etre a true dans le Popen
            except:
                print( "WRN: testAll: ASyncSystemCallThread.stop: terminate failed" );
        self.join( rTimeOut ); #wait with a timeout of n sec
        if( not self.isFinished() ):
            time.sleep( rTimeOut / 4.0 ); # time for things to be resfreshed (join/poll or ...) (longer)
        if( not self.isFinished() ):
            return -1;
        return self.newProcess.returncode;
    # stop - end

    def isFinished( self ):
        "is the process finished ?"
        time.sleep( 0.05 ); # time for things to be resfreshed (join/poll or ...)
#       return self.isAlive();
        if( self.newProcess == False ):
            return False; # the process hasn't been launch yet !
        self.newProcess.poll();
        return ( self.newProcess.returncode != None );
    # isFinished - end

# ASyncSystemCallThread - end

def asyncSystemCall( strCommandAndArgs, bStoppable = False ):
  "launch a system call, without waiting the end of the system call"
  "return the thread object"
  async = ASyncSystemCallThread( strCommandAndArgs, bStoppable );
  async.start();
  return async;
# asyncSystemCall - end


def mySystemCall( strCommandAndArgs, bWaitEnd = True, bStoppable = False ):
    "make a system call, and choose to wait till the end or to thread"
    "return the process status or an object of type ASyncSystemCallThread, if it's an asynccall"
    debug.debug( "altools: mySystemCall( '%s', bWaitEnd=%d, bStoppable=%d)" % ( strCommandAndArgs, bWaitEnd, bStoppable ) );
    obj = False;
    if( config.bTryToReplacePopenByRemoteShellCall ):
        try:
            ur = naoqitools.myGetProxy( "UsageRemoteTools", True );
            naoqiTask = None;
            if( bWaitEnd ):
                ur.systemCall( strCommandAndArgs );
            else:
                id = ur.post.systemCall( strCommandAndArgs );
                naoqiTask = naoqitools.naoqiTask( id, "UsageRemoteTools" );
            debug.debug( "altools: mySystemCall( '%s', bWaitEnd=%d ) - remote call - end" % ( strCommandAndArgs, bWaitEnd ) );
            return naoqiTask;
        except BaseException, err:
            print( "WRN: mySystemCall: UsageRemoteTools error, doing a standard call - err: %s" %  err );
            pass # in case of bug, we will use normal call (next lines)
    
    # else cas normal
    if( bWaitEnd ):
        newProcess = subprocess.Popen( strCommandAndArgs, shell=True ); # not blocking !
        try:
            sts = os.waitpid( newProcess.pid, 0 );
            obj = sts[1]; # waitpid return (pid, exitstatus)
        except:
            pass # pid already finished or some erros occurs or under windows ?
    else:
        obj = asyncSystemCall( strCommandAndArgs, bStoppable );
    debug.debug( "altools: mySystemCall( '%s', bWaitEnd=%d) - end" % (strCommandAndArgs, bWaitEnd ) );
    return obj;
# mySystemCall - end


def getNaoChestName():
    "get the nao name as stored in the rom chest"
    stm = naoqitools.myGetProxy( "ALMemory" );
    strNum = stm.getData( "Device/DeviceList/ChestBoard/BodyNickName" );
    if( strNum == 'Nao336' and getNaoNickName() == 'Astroboy' ):
        strNum = 'Nao332';    
    return strNum;
# getNaoChestName - end

def getNaoNickName():
    "get the nao name as given by user"
    # return executeAndGrabOutput( "hostname", True );
    return filetools.getFileFirstLine( '/etc/hostname' );
# getNaoNickName - end

global_listNaoOwner = {
    '316': ['Valentin','Nanimator'],
    '327': ['Alex','NaoAlex'],
    '598': ['Alex','NaoAlex'],
    '425': ['Accueil','NaoLife'],
    '302': ['Flora','NaoFlop'],
    '471': ['Céline','Lestate'],
    '488': ['Jérome','NaoIntissar'],
    '492': ['Julien','Nao2Jams'],
    
    '340': ['JmPomies','Tifouite'],
    '337': ['Jerome Laplace',''],
    '329': ['Locki','Noah'],
    '340': ['Troopa',''],
    '351': ['Mlecyloj',''],
    '317': ['Scoobi','Nao'],
    '379': ['Ksan','Timmy'],
    '387': ['Richard Seltrecht','Isaac'],
    '341': ['Zelig','Sonny'],
    '339': ['Rodriguez','Andrew'],
    '305': ['Tibot','Zoé'],
    '314': ['Laurent','Nao'],
    '409': ['Drack','Igor'],
    '319': ['Oxman','R2'],
    '342': ['Jfiger',''],
    '321': ['Bothari','Tchoggi'],
    '307': ['Alexan','Cybot'],
    '407': ['Olleke','Domo'],
    '412': ['Hadrien',''],
    '312': ['Bilbo','Nao'],
    '334': ['Nameluas','Nao'],
    '338': ['DavidRPT','Nao'],
    '332': ['Clayde','AstroBoy'],  # 332 renamed in 336
    '336': ['Harkanork','Tao'],
    '330': ['Antoine','Naodadi'],
    '367': ['Mataweh','Junior'],
    '358': ['Lexa','Zirup'],
    '306': ['Gwjsan','Naomi'],
};

def getUserNameFromChestBody():
    "get the user name from the chest number"
    "WRN: valid only for appu, and beta30!"
    global global_listNaoOwner;
    strNum = getNaoChestName(); 
    strNum = strNum[3:];
    try:
        strName = global_listNaoOwner[strNum][0];
    except:
        strName = "unknown";
    return strName;
# getUserNameFromChestBody - end

def executeAndGrabOutput( strCommand, bLimitToFirstLine = False ):
  "execute a command in system shell and return grabbed output"
  "WARNING: it's a 'not efficient' function!"
  strTimeStamp = filetools.getFilenameFromTime();
  strOutputFilename = pathtools.getVolatilePath() + "grab_output_" + strTimeStamp+ ".tmp"; # generate a different file each call for multithreading capabilities
  mySystemCall( strCommand + " > " + strOutputFilename );
  if( bLimitToFirstLine ):
    strBufferRead = filetools.getFileFirstLine( strOutputFilename );
  else:
    strBufferRead = filetools.getFileContents( strOutputFilename );
  try:
    os.unlink( strOutputFilename );
  except:
    pass
  debug.debug( "executeAndGrabOutput: '%s'" % strBufferRead );
  return strBufferRead;
# executeAndGrabOutput - end


def autoTest():
    if( test.isAutoTest() ):
        test.activateAutoTestOption();
        print( "isOnNao(): '%s'" % str( isOnNao() ) );
        print( "isOnWin32(): '%s'" % str( isOnWin32() ) );
        print( "getNaoIP(): '%s'" % str( getNaoIP() ) );
        print( "getNaoIPs(): '%s'" % str( getNaoIPs() ) );
        backgroundTask = mySystemCall( "echo waiting 5s;sleep 5;echo end of waiting 5s", bWaitEnd = False );
        mySystemCall( "echo ; echo CECI EST UNE TRACE DE TEST; echo" );
        print( "backgroundTask_wait_5s isFinished: %s" % str( backgroundTask.isFinished() ) );
        time.sleep( 5 );
        print( "backgroundTask_wait_5s isFinished: %s" % str( backgroundTask.isFinished() ) );
        backgroundTask2 = mySystemCall( "echo waiting 5s (2);sleep 5;echo end of waiting 5s (2)", bWaitEnd = False );
        print( "killing task2 - before" );
        backgroundTask2.stop();
        print( "killing task2 - after" );
        time.sleep( 1 );
        print( "finished (after that, there should be no more trace...)" );
        
        
# autoTest - end
    
autoTest();