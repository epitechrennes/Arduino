# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# String tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with net, web, ftp, ping..."""

print( "importing abcdk.nettools" );

import time

import debug
import naoqitools
import pathtools
import filetools
import system

def getHostFolderAndFile( strWebAddress ):
    "separate host, directory and filename from a web address"
    "ie: 'http://mangedisque.com/Alma/index.html' => ['http://mangedisque.com', 'Alma', 'index.html'];"

    strHostname = "";
    strFoldersName = "";
    strFileName = "";
    
    strRemaining = strWebAddress;
    nIndex = strRemaining.find( '//' );
    if( nIndex != -1 ):
        strHostname = strRemaining[:nIndex+2];        
        strRemaining = strRemaining[nIndex+2:];
    else:
        strHostname = "http://";
        
    nIndex = strRemaining.find( '/' );
    if( nIndex != -1 ):
         strHostname += strRemaining[:nIndex];
         strRemaining = strRemaining[nIndex:];
    else:
        strHostname += strRemaining;
        strRemaining = "";

    nIndex = strRemaining.rfind( '/');
    if( nIndex != -1 ):
         strFoldersName = strRemaining[:nIndex+1];
         strFileName = strRemaining[nIndex+1:];
    else:
        strFileName = "index.php";
        
    if( strHostname[0] in ['"', "'"] ):
        strHostname = strHostname[1:];
        
    if( strFileName[-1] in ['"', "'"] ):
        strFileName = strFileName[:-1];
     
    return [ strHostname, strFoldersName, strFileName ];
# getHostFolderAndFile - end
#print( "%s" % getHostFolderAndFile( 'http://mangedisque.com/Alma/index.html' ) ); # pass
# print( "%s" % getHostFolderAndFile( 'http://google.com/index.html' ) ); # pass


def getHtmlPage( strHtmlAdress, bWaitAnswer = True, rTimeOutForAnswerInSec = 30.0, strSaveAs = None, bTryToUseCpp = True ):
    "return a web page, or "" on error (async or sync method, with optionnal timeout)"
    "Warning: don't put '&' in the html adress !"
    "rTimeOutForAnswerInSec: set to 0 for infinite"
    "strSaveAs: instead of returning a string, just save to a file and return True"
    # this method is ok but doesn't work on adress that doesn't finished with an extension (.ext)
#  req = urllib2.Request( strHtmlAdress );
#  print req.get_full_url();
# handle = urllib2.urlopen( req );
#  res = handle.read();
#  return res;

    # use cpp !
    if( bTryToUseCpp ):
        try:
            usage = naoqitools.myGetProxy( 'UsageTools' );
            # separate hostname and directories
            strHost, strFolder, strPageName = getHostFolderAndFile( strHtmlAdress );
    #        print( "altools.getHtmlPage: L'ADRESSE DU SITE: -%s-%s-%s-:" % (strHost, strFolder, strPageName) );
    #        strHost = strHost[len('http://'):]; # remove http: older version doesn't like it !
            if( strSaveAs != None ):
                if( bWaitAnswer ):
                    bRet = usage.getWebFile( strHost, strFolder + strPageName, strSaveAs, rTimeOutForAnswerInSec );
                    return bRet;
                else:
                    bRet = usage.post.getWebFile( strHost, strFolder + strPageName, strSaveAs, rTimeOutForAnswerInSec );
                    return "";
            strPageContents = usage.getWebPage( strHost, strFolder + strPageName, rTimeOutForAnswerInSec );
            if( strPageContents != "error" or ( rTimeOutForAnswerInSec > 0. and rTimeOutForAnswerInSec < 10.0 ) ): # if we put a short timeout, that's possible to have an empty response!
                return strPageContents; # else, we will use the normal method
            else:
                print( "WRN: getHtmlPage: CPP method error: return empty, trying other method" );
        except BaseException, err:
            print( "WRN: getHtmlPage: CPP method error: %s" % str( err ) );
            pass # use oldies version

    print( "WRN: nettools.getHtmlPage: using old one using fork and shell!" );

    # not very efficient: should store it in var/volatile (but less os independent)
    debug.debug( "getHtmlPage( %s, bWaitAnswer = %d, rTimeOutForAnswerInSec = %d )" % ( strHtmlAdress, bWaitAnswer, rTimeOutForAnswerInSec ) );
    strRandomFilename = pathtools.getVolatilePath() + "getHtmlPage_%s.html" % filetools.getFilenameFromTime();
    # sous windows wget peut geler, donc on va l'appeller avec un timeout (qui ne fonctionne pas, c'est drole...)
#    threadWGet = system.mySystemCall( "wget %s --output-document=%s --tries=16 --timeout=60 --cache=off -q" % ( strHtmlAdress, strRandomFilename ), False, True ); # commenter cette ligne pour avoir toujours le meme fichier
    # en fait plein d'options n'existe pas sur Nao, donc on ne laisse que celle ci:
    if( strSaveAs != None ):
        strRandomFilename = strSaveAs;
    threadWGet = system.mySystemCall( "wget \"%s\" --output-document=%s -q" % ( strHtmlAdress, strRandomFilename ), bWaitEnd = False, bStoppable = True ); # commenter cette ligne pour avoir toujours le meme fichier
    if( not bWaitAnswer ):
        debug.debug( "getHtmlPage( %s, %d ) - direct return" % ( strHtmlAdress, bWaitAnswer ) );
        return "";

    timeBegin = time.time();
    timeElapsed = 0.0;

    time.sleep( 1.0 ); # time for the process to be created !
    
    if( isinstance( threadWGet, int ) ):
        # on est ici dans un post d'un systemCall thréadé sur un UsageRemoteTools
        try:
            usage = naoqitools.myGetProxy( 'UsageRemoteTools', True );
            usage.wait( threadWGet, rTimeOutForAnswerInSec*1000 ); # On a très souvent cette erreur la: "'Function wait exists but parameters are wrong'" la tache est peut etre deja fini ?
        except BaseException, err:
            print( "WRN: getHtmlPage: wait for end failed, err: " + str( err ) );
        debug.debug( "getHtmlPage: at the end: thread is finished (naoqi id: %d)" % threadWGet );
    else:
        while( 1 ):
            debug.debug( "getHtmlPage: thread is finished: %d" % threadWGet.isFinished()  );
            if( threadWGet.isFinished() ):
                debug.debug( "getHtmlPage: isFinished !!!" );
                break;

            timeElapsed = time.time() - timeBegin;
            if( timeElapsed > rTimeOutForAnswerInSec ):
                debug.debug( "getHtmlPage: %f > %f => timeout" % (timeElapsed, rTimeOutForAnswerInSec) );
                threadWGet.stop();
                break;
            time.sleep( 0.2 );
        # while - end
        debug.debug( "getHtmlPage: at the end: thread is finished: %d" % threadWGet.isFinished()  );

#  bOnWindows = ( os.name != 'posix' );
#  if( bOnWindows ):
#      time.sleep( 8.0 ); # temps de l'appel car sur certaines plateformes (windows) le os.waitpid semble ne pas bien fonctionner ou alors c'est le wget...

    if( strSaveAs == None ):
        strBuf = "";

        file = False;
        try:
            file = open( strRandomFilename, 'r' );
            strBuf = file.read();
        except:
            print( "getHtmlPage: WRN: file '%s' is empty or not finished to be aquire... (timeElapsed: %f)" % ( strRandomFilename, timeElapsed ) );
        finally:
            if( file ):
                file.close();
            
        try:
            if( file ):
                os.unlink( strRandomFilename );
        except:
            print( "getHtmlPage: WRN: unlink of file '%s' failed..." % strRandomFilename );

    #    debug.debug( "getHtmlPage( %s, %d ) - return '%s'" % ( strHtmlAdress, bWaitAnswer, strBuf ) );
        debug.debug( "getHtmlPage( %s, %d ) - return a page of length: '%d'" % ( strHtmlAdress, bWaitAnswer, len( strBuf ) ) );
    else:
        debug.debug( "getHtmlPage( %s, %d ) - return, data saved to '%s'" % ( strHtmlAdress, bWaitAnswer, strSaveAs ) );
        strBuf = True; # a bit burk
    return strBuf;
# getHtmlPage - end

def autoTest():
    getHtmlPage( "http://www.google.fr/index.html" );
# autoTest  - end
    

# test zone
#autoTest();