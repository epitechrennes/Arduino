# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# File tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called file, but risk of masking with the class file.

"""File Tools"""
print( "importing abcdk.filetools" );

import os
import time
import datetime
import shutil

import debug


def isFileExists( strPathFilename ):
#  strPathFilename = strPathFilename.replace( "/", getDirectorySeparator() );
#  strPathFilename = strPathFilename.replace( "\\", getDirectorySeparator() );
#  strPathFilename = strPathFilename.replace( getDirectorySeparator() + getDirectorySeparator(), getDirectorySeparator() );
#  print( "isFileExists( '%s' ) =>" % strPathFilename );
  try:
    file = open( strPathFilename, 'r' );
#    print( "file: " + str( file ) );
    if( file ):
#      print( "true" );
      file.close();
      return True;
  except (IOError, os.error), err:
#    print( "err: " + str( err ) );
    pass
#  print( "false" );
  return False;
# isFileExists - end


def copyFile( strPathFilenameSrc, strPathFilenameDst ):
    "copy one file to another one"
    "return true if ok"
    print( "INF: copyFile: %s => %s" % ( strPathFilenameSrc, strPathFilenameDst ) );
    bError = False;
    try:
        file = open( strPathFilenameSrc, "rb" );
    except BaseException, err:
        print( "ERR: filetools.copyFile failed: %s" % err );
        return False;
        
    try:
        strBuf = file.read();
    except BaseException, err:
        print( "ERR: filetools.copyFile failed: %s" % err );
        bError = True;
    file.close();        
    if( bError ):
        return False;

    try:
        file = open( strPathFilenameDst, "wb" );
        file.write( strBuf );
    except (IOError, os.error), err:
        print( "ERR: filetools.copyFile failed: %s" % err );
        bError = True;
    file.close();
    return not bError;
# copyFile - end

def copyDirectory( strPathSrc, strPathDst, strExcludeSkul = None ):
    "copy an entire directory to another place"
    "strExcludeSkul: if a file or directory contain this string, it will be excluded"
    "return true if ok"
    print( "INF: copyDirectory: %s => %s" % ( strPathSrc, strPathDst ) );
    bOk = True;
    bAtLeastOneFile = False;
    try:
        os.makedirs( strPathDst );
    except BaseException, err:
        print( "WRN: filetools.copyDirectory: while creating destination: " + str( err ) );
    if( not os.path.exists( strPathSrc ) ):
        return False;
    for elem in os.listdir( strPathSrc ):
        bAtLeastOneFile = True;
        sFullPath = os.path.join( strPathSrc, elem );
        if( strExcludeSkul != None and strExcludeSkul in elem ):
            continue;
        if os.path.isdir(sFullPath) and not os.path.islink(sFullPath):
            bOk &= copyDirectory( sFullPath, strPathDst + '/' + elem, strExcludeSkul );
        else:
            bOk &= copyFile( sFullPath, strPathDst + '/' + elem );
    return bOk and bAtLeastOneFile;
# copyDirectory - end


def getFileContents( szFilename ):
    "read a file and return it's contents, or '' if not found, empty, ..."
    aBuf = "";
    try:
        file = open( szFilename );
    except BaseException, err:
        debug.debug( "ERR: filetools.getFileContents open failure: %s" % err );
        return "";
        
    try:
        aBuf = file.read();
    except BaseException, err:
        debug.debug( "ERR: filetools.getFileContents read failure: %s" % err );
        file.close();
        return "";
        
    try:
        file.close();
    except BaseException, err:
        debug.debug( "ERR: filetools.getFileContents close failure: %s" % err );
        pass
    return aBuf;
# getFileContents - end


def getLine( strText, nNumLine ):
    "extract a specific line in a multiline text, return '' if line not found, text empty or ..."
    "parameter nNumLine should be in [0,nbrline-1]"
    # trim EOL and ...
    if( len( strText ) < 1 or nNumLine < 0 ):
        return "";


    aByLine = strText.split( '\n' );

    if( nNumLine >= len( aByLine ) ):
        return "";
    return aByLine[nNumLine];
 # getLine - end

def getFileFirstLine( szFilename ):
  "read a file and return it's first line, or '' if not found, empty, ..."
  strBufferRead = getFileContents( szFilename );
  return getLine( strBufferRead, 0 );
# getFileFirstLine - end



def getFilenameFromTime():
  "get a string usable as a filename relative to the current datetime stamp"
  strTimeStamp = str( datetime.datetime.now() );
  strTimeStamp = strTimeStamp.replace( " ", "_" );
  strTimeStamp = strTimeStamp.replace( ".", "_" );
  strTimeStamp = strTimeStamp.replace( ":", "m" );  
  return strTimeStamp;
# getFilenameFromTime - end

def getFileTime( strFilename ):
    "return the date/time of the last modify date of a file"
    try:
        nTime = os.path.getmtime( strFilename );
    except os.error, err:
        nTime = 0;
#    print( "getFileTime( '%s' ): %d" % ( strFile, nTime ) );
    return nTime;
# getFileTime - end
    

def getAgeOfFile( strFilename ):
    "return the number of seconds between timestamp of file and now"
    nTime = time.time() - getFileTime( strFilename );
    return nTime;
# getAgeOfFile - end



def makedirsQuiet( strPath, bPrintError = False ):
    try:
        os.makedirs( strPath );
    except BaseException, err:
        if( bPrintError ):
            print( "WRN: filetools.makedirsQuiet: err: %s" + str( err ) );
        pass # quiet!
# makedirsQuiet - end


def removeDirsQuiet( strPath, bPrintError = False ):
    try:
        shutil.rmtree( strPath );
    except BaseException, err:
        if( bPrintError ):
            print( "WRN: filetools.removeDirsQuiet: err: %s" + str( err ) );
        pass # quiet!
# removeDirsQuiet - end

def addFolderToZip( zipFile, strFolderPath, strRootPath = None ):
    "add an entire path to a ZipFile object previously open"
    "strRootPath: 1) permits to know when call from outside (=None), 2) store the absolute path of the archive root directory"
    "return the number of file added"
    print( "INF: filetools.addFolderToZip( '%s', '%s' )" % ( strFolderPath, strRootPath ) );
    nNbrFile = 0;
    for elem in os.listdir( strFolderPath ):
        sFullPath = os.path.join( strFolderPath, elem );
        if os.path.isdir(sFullPath) and not os.path.islink(sFullPath):
            if( strRootPath == None ):
                strRootPathChild = strFolderPath;
            else:
                strRootPathChild = strRootPath;
            nNbrFile += addFolderToZip( zipFile, sFullPath, strRootPath = strRootPathChild );
        else:
            strOrigFile = sFullPath;
            strArcFile = sFullPath[len(strRootPath):];
            # print( "%s => %s" % ( strOrigFile, strArcFile ) );
            zipFile.write( strOrigFile, strArcFile );
            nNbrFile += 1;
    if( strRootPath == None ):
        print( "INF: filetools.addFolderToZip: %d file(s) added to zip" % nNbrFile );
    return nNbrFile;
# addFolderToZip - end

def extractFolderFromZip( zipFile, aTableListPath ):
    "extract some folders from a zip file"
    "aTableListPath: a dictionnary with folder_in_archives => destination_on_disk"
    "eg: [ 'behaviors' ] = '/home/nao/Applications/autonomous/life2/'"
    "return number of extracted files"
    "WARNING: handle only first folder name"
    print( "filetools.extractFolderFromZip, table path:" );
    for k, v in aTableListPath.iteritems():
        print( "\t '%s' => '%s'" % ( k, v ) );
    listFile = zipFile.infolist();
    nNbrExtracted = 0;
    nCount = 0;
    for info in listFile:
        strFilename = info.filename;
        strFirstFolder = strFilename[:strFilename.find('/')];
#        print( "file: '%s' => first folder: '%s'\n" % ( strFilename, strFirstFolder ) );
        if( strFirstFolder in aTableListPath.keys() ):
            print( "%4d/%4d: '%s' exploded to '%s'" % ( nCount, len( listFile ), strFilename, aTableListPath[strFirstFolder] ) );
            try:
                zipFile.extract( strFilename, aTableListPath[strFirstFolder] );
                nNbrExtracted += 1;
            except BaseException, err:
                print( "ERR: life_data.installPackage: extract %s to %s, err: %s" % ( strFilename, aTableListPath[strFirstFolder], str( err ) ) );
                # on continue la ou pas ?            
        nCount += 1;
    print( "INF: filetools.extractFolderFromZip: %d file(s) extracted" % nNbrExtracted );
    return nNbrExtracted;
# extractFolderFromZip - end
    

def replaceInFile( strStringToFind, strStringNew, strFilenameSrc, strFilenameDst = None ):
    "replace the string <strStringToFind> by <strStringNew> in a file <strFilenameSrc>"
    "strFilenameDst: if unspecified, the source will be changed"
    "return True if ok"
    
    debug.debug( "INF: filetools.replaceInFile: file '%s' => '%s', replacing '%s' by '%s'\n" % (strFilenameSrc, strFilenameDst, strStringToFind, strStringNew )  );
    
    strContents = getFileContents( strFilenameSrc );
    
#    print( "strContents: " + strContents );

    strContents = strContents.replace( strStringToFind, strStringNew );
    if( strFilenameDst == None ):
        strFilenameDst = strFilenameSrc;
        
    try:
        file = open( strFilenameDst, "w" );
    except BaseException, err:
        debug.debug( "ERR: filetools.replaceInFile open failure: %s" % err );        
        return False;
        
    try:
        file.write( strContents );
    except BaseException, err:
        debug.debug( "ERR: filetools.replaceInFile write failure: %s" % err );
        file.close();
        return False;
        
    try:
        file.close();
    except BaseException, err:
        debug.debug( "ERR: filetools.replaceInFile close failure: %s" % err );
        return False;
        
    return True;
# replaceInFile - end

def autoTest():
    import config
    config.bDebugMode = True;
    print( "getAgeOfFile: %s"  % str( getAgeOfFile( "filetools.py" ) ) );
    #print( "replace in File:" + str( replaceInFile( "abcdk.", "toto.", "test.txt", "test2.txt" ) ) );

# autoTest();