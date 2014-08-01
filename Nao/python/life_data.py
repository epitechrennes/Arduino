# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Autonomous Life
# Life package
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Handle life data package"""

print( "importing life_data.py" );

import os
import stat
import sys
import zipfile

# line to add when not launched from a Nao
sdkPath = os.path.abspath( os.path.dirname( __file__ ) ) + '/../../../appu_shared/sdk/';
if( not sdkPath in sys.path ):
    print( "for use on a computer: appending to the sys path: '%s'" % sdkPath );
    sys.path.append( sdkPath );

import abcdk.filetools as filetools
import abcdk.naoqitools as naoqitools
import abcdk.nettools as nettools
import abcdk.pathtools as pathtools
import abcdk.system as system
import abcdk.stringtools as stringtools

def getPath():
    "return the path of the module currently executing"
    return os.path.abspath( os.path.dirname( __file__ ) );
# getPath - end

class LifeData:
    def __init__(self):
        self.path = os.path.abspath( os.path.dirname( __file__ ) ) + pathtools.getDirectorySeparator();
        self.gitPath = self.path + ".." + pathtools.getDirectorySeparator() + ".." + pathtools.getDirectorySeparator() + ".." + pathtools.getDirectorySeparator();
        self.strDownloadedPath = '/home/nao/downloaded/life_data/';
        self.strServerPath = None; # will contents, after initialisation the nearest web server
        self.strLocalServerPath = "http://amazel-de.local/"; # internal path
        self.strExternalServerPath = "http://nao.mangedisque.com/"; # external path

    # __init__ - end
    
    def __del__(self):
        pass
    # __del__ - end
    
    def getVersion( self ):
        "Return the version number of the data, used to detect new version on remote server"
        "So it should reflect the version of the data"
        rLifeDataVersionNumber = 0.953; # don't modify this variable name because it's grepped from outside - don't forget to modify life_data__metadata.xml too !
        return rLifeDataVersionNumber;
    # getVersion - end
    
    
    def getPackVersion( self, strMetaDataFileContents ):
        "extract a version from a metadata file"
#        print( "INF: LifeData.getPackVersion: strMetaDataFileContents: " +strMetaDataFileContents );
        nPick = strMetaDataFileContents.find( "<version>" );
        if( nPick == -1 ):
            print( "INF: LifeData.getPackVersion: no version number found in data (data size: %d)" % ( len( strMetaDataFileContents ) ) );
            return 0.;
        rVersion = stringtools.findNumber( strMetaDataFileContents[nPick:] );
        return rVersion;
    # getPackVersion - end
    
    
    def getFileVersion( self, strFilePath ):
        "extract a version from a life_data file (yeah it's this file, but find it without loading it with python)"
        enclosedFileData = filetools.getFileContents( strFilePath );
        # print( "INF: LifeData.getFileVersion: '%s'" % enclosedFileData );
        nPick = enclosedFileData.find( "rLifeDataVersionNumber" );
        if( nPick == -1 ):
            print( "INF: LifeData.getFileVersion: no version number found in %s (file size: %d)" % ( strFilePath, len( enclosedFileData ) ) );
            return 0.;
        rVersion = stringtools.findNumber( enclosedFileData[nPick:] );
        return rVersion;
    # getFileVersion - end
    
    def getLocalServer( self ):
        "get local server, or None"
        strData = nettools.getHtmlPage( self.strLocalServerPath + "index.html" );
        if( len( strData ) > 60 ):
            return self.strLocalServerPath;
        return None;
    # getLocalServer - end
    
    def getRemotePath( self ):
        if( self.strServerPath == None ):
            # test the nearest one
            self.strServerPath = self.getLocalServer();
            if( self.strServerPath  == None ):
                self.strServerPath = self.strExternalServerPath;
            print( "INF: LifeData.getRemotePath(): web path used is: " + self.strServerPath );
        return self.strServerPath + "life_data/";
    # getRemotePath - end

            
    
    def generatePackage( self, strNaoqiVersion, bRegenerateTempFolder = True, bRegenerateZip = True, bForBehavior = False ):
        "generate the big archive containing all the life data"
        "return true if ok"
        "bForBehavior: to be used as ressources of a choregraphe project"
        print( "INF: LifeData.generatePackage( strNaoqiVersion = '%s' )" % strNaoqiVersion );
        if( system.isOnNao() ):
            print( "ERR: LifeData.generatePackage: must be executed on a computer within the git folder!" );
            return false;
        if( not bForBehavior ):
            strTempPath = self.path + 'temp_life_data/';
        else:
            strTempPath = self.path + 'temp_life_data_light/';
        if( bRegenerateTempFolder ):
            filetools.removeDirsQuiet( strTempPath );
            filetools.makedirsQuiet( strTempPath );
            
            # python script
            strObjPath = strTempPath + "python/";
            filetools.makedirsQuiet( strObjPath );
            filetools.copyDirectory( self.gitPath + "appu_shared/sdk/abcdk/", strObjPath + 'abcdk/', '.pyc' );
            filetools.copyFile( self.gitPath + "appu_work/altools.py", strObjPath + 'altools.py' );
            filetools.copyFile( self.gitPath + "appu_work/naoconfig.py.sample", strObjPath + 'naoconfig.py' );
            filetools.copyFile( self.gitPath + "appu_work/naolibrary.py", strObjPath + 'naolibrary.py' );
            filetools.copyFile( self.gitPath + "appu_work/behaviordata.py", strObjPath + 'behaviordata.py' );
            filetools.copyFile( self.gitPath + "appu_work/autonomous_pose_default.py", strObjPath + 'autonomous_pose_default.py' );
            filetools.copyFile( self.path + "life_data.py", strObjPath + 'life_data.py' );
            # update version:
            if( bForBehavior ):
                strFilename = strObjPath + 'life_data.py';
                rVersion = self.getFileVersion( strFilename );
                rVersionLight = rVersion - 0.001;
                strSkul = "rLifeDataVersionNumber = %g;";
                filetools.replaceInFile( strSkul % rVersion, strSkul % rVersionLight, strFilename );

            # main behaviors (exported to xar)
            strExportScript = self.gitPath + "appu_shared/scripts/python/convert_crg_into_new_xars.py";
            print( "INF: LifeData.generatePackage: launching script '%s'" % strExportScript );
            
            os.system( "python " + strExportScript + " " + ".." + " " + "autonomous2" );
            strObjPath = strTempPath + "main_behaviors/autonomous2/";
            filetools.copyDirectory( self.path + "./exported/autonomous2/", strObjPath );

            os.system( "python " + strExportScript + " " + self.gitPath + "appu_applications/beta_menu" + " " + "beta_menu2" );
            strObjPath = strTempPath + "main_behaviors/beta_menu2/";
            filetools.copyDirectory( self.path + "./exported/beta_menu2/", strObjPath );
            filetools.removeDirsQuiet( self.path + "exported/" );

            # sub behaviors
            strObjPath = strTempPath + "behaviors/";
            filetools.copyDirectory( self.path + "../behaviors/", strObjPath );
            os.unlink( strObjPath + "standing/Pour regles de lancement des histoires, on met des heures afin de les ventiler dans le temps, le top serait selon les jours, mais comme mes demos sont souvent le lundi.txt" );

            # wait_anim
            strObjPath = strTempPath + "wait_anim/";
            strSrcPath = self.path + "../wait_anim/";
            # first export'em
            if( True ):
                strPathBackup = os.getcwd();
                os.chdir( strSrcPath );
                os.system( "convert_all_crg.py" );
                os.chdir( strPathBackup );
            filetools.copyDirectory( strSrcPath + 'exported/', strObjPath );
            
            # modules
            strObjPath = strTempPath + "modules";
            bRet = filetools.copyDirectory( self.gitPath + "appu_modules/buildcc/%s/" % strNaoqiVersion, strObjPath );
            if( not bRet ):
                print( "ERR: LifeData.generatePackage: compiled module not found for the version of naoqi: '%s'" % strNaoqiVersion );
                return False;
                
            # preferences
            filetools.copyFile( self.gitPath + "appu_modules/src/autonomous/ALLife_sample.xml", strObjPath + "/ALLife_sample.xml" );

            # naolibrary
            strObjPath = strTempPath + "naolibrary/";
            filetools.copyDirectory( self.gitPath + "appu_shared/library/naolibrary/", strObjPath );
            
            # scripts
            strObjPath = strTempPath + "scripts/";
            filetools.copyDirectory( self.path + "../scripts/", strObjPath );

            # bin
            strObjPath = strTempPath + "bin/";
            bRet = filetools.copyDirectory( self.gitPath + "appu_shared/scripts/cpp/buildcc/%s/lib" % strNaoqiVersion, strObjPath );
            if( not bRet ):
                print( "ERR: LifeData.generatePackage: compiled binary (watchdog or ...) not found for the version of naoqi: '%s'" % strNaoqiVersion );
                return False;

            # sounds
            if( not bForBehavior ):
                strObjPath = strTempPath + "wav/";
                filetools.copyDirectory( self.gitPath + "appu_data/sounds/", strObjPath );

        strReleasePath = self.path + '/release/';
        if( not bForBehavior ):
            filetools.removeDirsQuiet( strReleasePath ); # light suppose you want to keep a previous generated
        filetools.makedirsQuiet( strReleasePath );

        strZipName = "life_data.zip";
        if( bForBehavior ):
            strZipName = "life_data_light.zip";
        if( bRegenerateZip ):
            # Create the big zip
            zf = zipfile.ZipFile( strReleasePath + strZipName, 'w', zipfile.ZIP_DEFLATED );
            # zf.write( 'temp/behaviors/metadata_samples.xml', 'behaviors/metadata_samples.xml' );
            filetools.addFolderToZip( zf, strTempPath );
            zf.close();
        if( not self.testPackage( strReleasePath + strZipName ) ):
            print( "ERR: package '%s' is corrupted" % (strReleasePath + strZipName) );
            return False;
        
        # copy metadata
        bRet = filetools.copyFile( self.path + "life_data__metadata.xml", strReleasePath + "metadata.xml" );        
        # copy minimal file to the project ressource
        strProjectPath = self.path + "install_life_behavior/ressources/" ;
        filetools.makedirsQuiet( strProjectPath );
        bRet &= filetools.copyFile( strTempPath + "python/" + "life_data.py", strProjectPath + "life_data.py" ); # copy from temp, so that it has a patched version number (when light)
        bRet &= filetools.copyDirectory( strTempPath + "python/abcdk", strProjectPath + "abcdk/" );
        if( bForBehavior ):
            bRet &= filetools.copyFile( strReleasePath + strZipName, strProjectPath + strZipName );
        return bRet;
    # generatePackage - end
    
    def installPackage(self, strPackage ):
        "install the package at the good place on the robot"
        print( "INF: LifeData.installPackage( '%s' )" % strPackage );
        strTempFolder = "extracted_files";
        try:
            zf = zipfile.ZipFile( strPackage, 'r');
        except BaseException, err:
            print( "ERR: LifeData.installPackage: zip error: " + str( err ) );
            return False;
        # print( str( zf.infolist() ) );
        # zf.extractall( strTempFolder ); # extract all in a temp folder, but faster to install it directly at the good places !
        strHome = '/home/nao/';
        if( not system.isOnNao() ):
            strHome = 'c:/temp2/nao_simu_cle/'; # to test stuffs !
        aTableListPath = dict();
        aTableListPath[ 'behaviors' ] = strHome + 'Applications/autonomous/life2/';
        aTableListPath[ 'wait_anim' ] = strHome + 'Applications/autonomous/life2/';
        aTableListPath[ 'naolibrary' ] = strHome;
        aTableListPath[ 'python' ] = strHome +  'naoqi/lib/';
        aTableListPath[ 'wav' ] = strHome +  'Applications/shared/';
        aTableListPath[ 'modules' ] = strHome + 'Applications/autonomous/';
        aTableListPath[ 'main_behaviors' ] = strHome + 'Applications/autonomous/';
        aTableListPath[ 'scripts' ] = strHome;
        aTableListPath[ 'bin' ] = strHome;
        
        # close current usageremote running
        os.system( "killall usageremote" );
        
        bRet = filetools.extractFolderFromZip( zf, aTableListPath );
        zf.close();
        
        # install preferences
        strALLifeSrc = strHome + "Applications/autonomous/modules/ALLife_sample.xml";
        strALLifeDst = strHome + "naoqi/preferences/ALLife.xml";
        if( not filetools.isFileExists( strALLifeDst ) ):
            try:
                bRet &= filetools.copyFile( strALLifeSrc, strALLifeDst );
            except BaseException, err:
                print( "ERR: life_data.installPackage: copyfile %s => %s, err: %s" % ( strALLifeSrc, strALLifeDst, str( err ) ) );
                # on continue la ou pas ?
        # install patch for launch module from every path
        filetools.makedirsQuiet( strHome + "naoqi/lib/naoqi/lib/" );
        try:
            strFile = strHome + 'Applications/autonomous/modules/bin/usageremote';
            nCurrentMode =  os.stat(strFile)[stat.ST_MODE];
            nNewMode = nCurrentMode | stat.S_IXGRP | stat.S_IEXEC;
            os.chmod( strFile, nNewMode );
        except BaseException, err:
            print( "ERR: LifeData.installPackage: chmod error: " + str( err ) );
        return bRet;
    # installPackage - end
    
    def downloadPackage(self ):    
        if( not system.isOnNao() ):
            print( "ERR: LifeData.downloadPackage: must be executed on a real Nao!" );
            return false;        
        filetools.makedirsQuiet( self.strDownloadedPath );
        ut = naoqitools.myGetProxy( "UsageTools" );
        # ut.setDebugMode( True );
        nettools.getHtmlPage( self.getRemotePath() + "metadata.xml", bWaitAnswer = True, rTimeOutForAnswerInSec = 0, strSaveAs = self.strDownloadedPath + "metadata.xml" );            
        nettools.getHtmlPage( self.getRemotePath() + "life_data.zip", bWaitAnswer = True, rTimeOutForAnswerInSec = 0, strSaveAs = self.strDownloadedPath + "life_data.zip", bTryToUseCpp = False ); # notre bibliotheque cpp ne gere pas les si gros fichiers, pfff...    
    # downloadPackage - end

    def testPackage( self, strPackage ):
        "test a package"
        "return True if ok"
        try:
            zf = zipfile.ZipFile( strPackage, 'r');
        except BaseException, err:
            print( "ERR: LifeData.installPackage: zip error: " + str( err ) );
            return False;
        bRet = zf.testzip() == None;
        zf.close();
        if( not bRet ):
            print( "WRN: LifeData.testPackage: package '%s' is corrupted" % strPackage );
        return bRet;
    # testPackage - end
    
    def erasePackage( self, strPackage ):
        "erase a package and all linked file"
        try:
            os.unlink( strPackage );
        except BaseException, err:
            print( "ERR: LifeData.erasePackage: unlink(1) error: " + str( err ) );
        try:
            os.unlink( strPackage[:strPackage.rfind( '/' )+1] + "metadata.xml" );
        except BaseException, err:
            print( "ERR: LifeData.erasePackage: unlink(2) error: " + str( err ) );
    # erasePackage - end
    
    def getStatsAboutPackage( self, strPackage, bSortedBySize = True ):
        def __sortValues(elem1, elem2):
            "This private method is a tool for the sort algorithm."
            return elem1.compress_size - elem2.compress_size;
            
        strOut = "";
        try:
            zf = zipfile.ZipFile( strPackage, 'r');
            listInfo = zf.infolist();
            if( bSortedBySize ):
                listInfo.sort( __sortValues );
            for info in listInfo:
                strOut += "file: compress: %8d, size: %8d, file: '%s'\n" % ( info.compress_size, info.file_size, info.filename );
            zf.close();
        except BaseException, err:
            print( "ERR: LifeData.getStatsAboutPackage: zip error: " + str( err ) );
            return False;
        return strOut;
        
    
# class LifeData - end

lifeData = LifeData();

def autoTest():    
#    print( "getRemotePath:" + lifeData.getRemotePath() );
#    lifeData.generatePackage( "1.7.42", bRegenerateTempFolder = True, bForBehavior = True );
#    lifeData.installPackage( "release/life_data.zip" );
#    print( "Testing zip:" + str( lifeData.testPackage( "tptp.zip" ) ) );
    print( lifeData.getStatsAboutPackage( "release/life_data_light.zip" ) );
# autoTest - end

#autoTest();