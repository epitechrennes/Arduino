# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Speech tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Speech tools"
print( "importing abcdk.speech" );

import math

import config
import system
import debug
import constants
import naoqitools
import pathtools
import filetools

def getDefaultSpeakLanguage():
  "return the default speak language"
  #return constants.LANG_EN; # TODO: better things ! # CB : gets the real language
  if( not system.isOnNao() ):
    return 0;
  try:
    tts = naoqitools.myGetProxy("ALTextToSpeech");
  except:
    # no tts => anglais
    debug.debug( "WRN: speech.getDefaultSpeakLanguage: no tts found" );
    return constants.LANG_EN;
  if( tts == None ):
    return constants.LANG_EN;
  lang =  tts.getLanguage()
  if lang == "French":
    return constants.LANG_FR;
  else:
    return constants.LANG_EN;  
# getDefaultSpeakLanguage - end

def setSpeakLanguage( nNumLang = getDefaultSpeakLanguage(), proxyTts = False ):
    "change the tts speak language"
    print( "SetSpeakLanguage to: %d" % nNumLang );
    if( not proxyTts ):
        proxyTts = naoqitools.myGetProxy( "ALTextToSpeech" );
    if( not proxyTts ):
        debug( "ERR: setSpeakLanguage: can't connect to tts" );
        return;

    try:
        if( nNumLang == constants.LANG_FR ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceFrench" );
        elif ( nNumLang == constants.LANG_EN ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceEnglish" );
        elif ( nNumLang == constants.LANG_SP ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceSpanish" );
        elif ( nNumLang == constants.LANG_IT ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceItalian" );
        elif ( nNumLang == constants.LANG_GE ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceGerman" );
        elif ( nNumLang == constants.LANG_CH ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceChinese" );
        elif ( nNumLang == constants.LANG_PO ):
            proxyTts.loadVoicePreference( "NaoOfficialVoicePolish" );
        elif ( nNumLang == constants.LANG_KO ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceKorean" );            
        else:
            proxyTts.loadVoicePreference( "NaoOfficialVoiceEnglish" );
    except:
        print( "ERR: setSpeakLanguage: loadVoicePreference error" );
# setSpeakLanguage - end

def getSpeakLanguage():
  "return the current speak language of the synthesis"
  tts = naoqitools.myGetProxy( "ALTextToSpeech" );
  strLang = tts.getLanguage();
  if( strLang ==  "French" ):
    return constants.LANG_FR;
  elif ( strLang ==  "English" ):
    return constants.LANG_EN;
  elif ( strLang ==  "Spanish" ):
    return constants.LANG_SP;
  elif ( strLang ==  "Italian" ):
    return constants.LANG_IT;
  elif ( strLang ==  "German" ):
    return constants.LANG_GE;
  elif ( strLang ==  "Chinese" ):
    return constants.LANG_CH;
  elif ( strLang ==  "Polish" ):
    return constants.LANG_PO;
  elif ( strLang ==  "Korean" ):
    return constants.LANG_KO;    
  else:
    return constants.LANG_EN;
# getSpeakLanguage - end

def getSpeakAbbrev( nNumLang ):
    "return the lang abbreviation from a lang number"
    if( nNumLang == constants.LANG_FR ):
        return 'fr';
    if( nNumLang == constants.LANG_EN ):
        return 'en';
    if( nNumLang == constants.LANG_SP ):
        return 'sp';
    if( nNumLang == constants.LANG_IT ):
        return 'it';
    if( nNumLang == constants.LANG_GE ):
        return 'ge';
    if( nNumLang == constants.LANG_CH ):
        return 'ch';
    if( nNumLang == constants.LANG_PO ):
        return 'po';
    if( nNumLang == constants.LANG_KO ):
        return 'ko';
    return 'en'; # default ?
# getSpeakLanguage - end



def isLangFrench():
  return getSpeakLanguage() == constants.LANG_FR;

def isLangEnglish():
  return getSpeakLanguage() == constants.LANG_EN;

def isLangSpanish():
  return getSpeakLanguage() == constants.LANG_SP;

def isLangItalian():
  return getSpeakLanguage() == constants.LANG_IT;

def isLangGerman():
  return getSpeakLanguage() == constants.LANG_GE;

def isLangChinese():
  return getSpeakLanguage() == constants.LANG_CH;

def isLangPolish():
  return getSpeakLanguage() == constants.LANG_PO;

def isLangKorean():
  return getSpeakLanguage() == constants.LANG_KO;

def setLangFrench():
  setSpeakLanguage( constants.LANG_FR );

def setLangEnglish():
  setSpeakLanguage( constants.LANG_EN );

def setLangSpanish():
  setSpeakLanguage( constants.LANG_SP );

def setLangItalian():
  setSpeakLanguage( constants.LANG_IT );

def setLangGerman():
  setSpeakLanguage( constants.LANG_GE );

def setLangChinese():
  setSpeakLanguage( constants.LANG_CH );

def setLangPolish():
  setSpeakLanguage( constants.LANG_PO );
  
def setLangKorean():
  setSpeakLanguage( constants.LANG_KO );



def changeLang():
#  if( config.nNumLang == constants.LANG_FR ):
#    config.nNumLang = constants.LANG_EN;
#  else:
#    config.nNumLang = constants.LANG_FR;
    print( "speech.changeLang: TODO reecrire sans utiliser nNumLang" ); # TODO
# changeLang - end


def assumeTextHasDefaultSettings( strTextToSay, nUseLang = -1 ):
    "look if text has voice default params( RSPD, VCT, Vol...) if not, add it, and return it"
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    if( nUseLang == constants.LANG_CH ):
        return strTextToSay; # current bug => don't add modifiers to this speak languages!

    if( strTextToSay.find( "\\RSPD=" ) == -1 ):
        strTextToSay = "\\RSPD=" + str( config.nSpeakSpeed ) + "\\ " + strTextToSay;
    if( strTextToSay.find( "\\VCT=" ) == -1 ):
        strTextToSay = "\\VCT=" + str( config.nSpeakPitch ) + "\\ " + strTextToSay;
    if( strTextToSay.find( "\\VOL=" ) == -1 ):
        strTextToSay = "\\VOL=" + str( config.nSpeakVolume ) + "\\ " + strTextToSay;
    return strTextToSay;
# assumeTextHasDefaultSettings - end


def sayAndCache_getFilename( strTextToSay, nUseLang = -1 ):
    "return the filename linked to the sentence to say (using precomputed text)"
    "nUseLang: if different of -1: speak with a specific languages (useful, when text are already generated: doesn't need to swap languages for nothing!"

    # we will generate a string without some specific characters
    # specific characters are all but A-Za-z0-9

    #allchars = "";
    #for i in range( 1, 256):
    #  allchars += ord( i );
    #allcharsbutalphanum = allchars.translate(None, 'abcdefghi ...)

    #  szFilename = strTextToSay.replace( " ", "_" ); # this line cut the compatybility with ALDemo
    #  szFilename = strTextToSay.replace( "\n", "__" ); # this line cut the compatybility with ALDemo
    #  szFilename = szFilename.translate( string.maketrans("",""), ' ,;.?!/\\\'"-:><=' );

    szFilename = "";
    for i in range( len( strTextToSay ) ):
        ch = strTextToSay[i];
        if( ch.isalnum() ):
            szFilename += ch;
        elif( ch == ' ' ):
            szFilename += '_';
        else:
            szFilename += "%X" % ( ord( ch )%16 );

    szFilename = szFilename[:160]; # limit filename to 160 chars
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    szFilename = str( nUseLang ) + szFilename;
    return szFilename;
# sayAndCache_getFilename - end

def sayAndCache_InformPrepare():
    "inform user we will prepare a text, and that would take sometimes"
    aListTextWait = ["Wait a little I'm preparing what I would say", "Attend un peu, je réfléchis a ce que je vais dire" ];
    if( getSpeakLanguage() <= constants.LANG_FR ):
        listTextWait = aListTextWait[getSpeakLanguage()];
    else:
        listTextWait = aListTextWait[constants.LANG_EN];
    sayAndCache( listTextWait, bStoreToNonVolatilePath = True, bWaitEnd = False ) # c'est récursif, mais si le texte est plus court que la limite, alors c'est ok (renderé juste la premiere fois)
# sayAndCache_InformPrepare - end
    
def sayAndCache( strTextToSay, bJustPrepare = False, bStoreToNonVolatilePath = False, bDirectPlay = False, nUseLang = -1, bWaitEnd = True, bCalledFromSayAndCacheFromLight = False ):
  "generate a text in a file, then read it, next time it will be directly played from that file"
  "bJustPrepare: render the text to a file, but don't play it now"
  "bStoreToNonVolatilePath: copy the generated file to a non volatile path (/usr/generatedvoices)"
  "nUseLang: if different of -1: speak with a specific languages (useful, when text are already generated: doesn't need to swap languages for nothing!"
  "return the length of the text in seconds, or None if impossible"
  print( "sayAndCache( '%s', bJustPrepare: %s, bStoreToNonVolatilePath: %s, bDirectPlay: %s, nUseLang: %d, bWaitEnd: %s, bCalledFromSayAndCacheFromLight: %s )" % ( strTextToSay, str( bJustPrepare ), str( bStoreToNonVolatilePath ), str( bDirectPlay ), nUseLang, str( bWaitEnd ), str( bCalledFromSayAndCacheFromLight ) ) );
  if( not config.bPrecomputeText ):
      print( "sayAndCache: disabled by configuration: bPrecomputeText is false" );
      if( bJustPrepare ):
          return None; # do nothing
      tts = naoqitools.myGetProxy( "ALTextToSpeech" );
      tts.say( strTextToSay );
      return None;
  print( "sayAndCache: FORCING DIRECT_PLAY CAR SINON C'EST BUGGE DANS LA VERSION COURANTE!");  
  bDirectPlay = True;
  
  if( config.bRemoveDirectPlay ):
    print( "WRN: DISABLING DIRECT_PLAY SETTINGS for testing/temporary purpose" );
    bDirectPlay = False;  
  
  strTextToSay = assumeTextHasDefaultSettings( strTextToSay, nUseLang );
  szFilename = sayAndCache_getFilename( strTextToSay, nUseLang );
  
  szPathVolatile = pathtools.getVolatilePath();
  
#  if( not szFilename.isalnum() ): # the underscore is not an alphanumeric, but is valid there
#    debug( "WRN: sayAndCache: some chars are not alphanumeric in filename '%s'" % szFilename );
  szPathFilename = szPathVolatile + szFilename + ".raw";
  bGenerate = not filetools.isFileExists( szPathFilename );
  
  if( bGenerate ):
    szAlternatePathFilename = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw"; # look in a non volatile path
    
    if( filetools.isFileExists( szAlternatePathFilename ) ):
      debug( "sayAndCache: get static precomputed text for '%s'" % ( strTextToSay ) );
      copyFile( szAlternatePathFilename, szPathFilename );
      bGenerate = not filetools.isFileExists( szPathFilename );  #update this variable
    # if alternate
  # if bGenerate
  
  if( bGenerate ):
    # generate it!
    debug( "sayAndCache: generating '%s' to file '%s'" % ( strTextToSay, szPathFilename ) );
    sayAndCache_InformProcess();
    timeBegin = time.time();
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    
    if( nUseLang != -1 ):
        # change the language to the wanted one
        setSpeakLanguage( nUseLang );
    if( len( strTextToSay ) > 150 and ( not bJustPrepare or bCalledFromSayAndCacheFromLight ) ):
        # if it's a long text, we had a blabla to tell the user we will wait (if it's a just prepare from inner, we don't use it)
        sayAndCache_InformPrepare();
    
    print( "TTS TO FILE 1 - BEGIN" );
    tts.sayToFile( strTextToSay, szPathFilename );
    print( "TTS TO FILE 1 - END" );
    sayAndCache_InformProcess_end();
    
    debug( "sayAndCache: generating text to file - end (tts) - time: %fs" % ( time.time() - timeBegin ) );    
    timeBegin = time.time();
    
    removeBlankFromFile( szPathFilename );
    debug( "sayAndCache: generating text to file - end (post-process1) - time: %fs" % ( time.time() - timeBegin ) );
    timeBegin = time.time();

    if( bStoreToNonVolatilePath ):
      try:
        os.makedirs( pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator());
      except:
        pass
      szAlternatePathFilename = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw"; # a non volatile path
      copyFile( szPathFilename, szAlternatePathFilename );

    time.sleep( 0.1 ); # pour laisser la synthese souffler un peu (dans les scripts je mettais 300ms)
    debug( "sayAndCache: generating text to file - end (post-process2) - time: %fs" % ( time.time() - timeBegin ) );
    
  statinfo = os.stat( szPathFilename );
  rLength = statinfo.st_size / float(22050*1*2); # sizefile => secondes
    
  if( not bJustPrepare ):
#    debug( "speech::sayAndCache: launching sound now!" );
    if( bWaitEnd ):
        analyseSound_pause( True );
    if( bDirectPlay ):
        nLang = nUseLang;
        if( nLang == -1 ):
            nLang = getSpeakLanguage();
        nFreq = 22050;
        if( nLang == constants.LANG_CH or nLang == constants.LANG_KO ):
            nFreq = 17000; # parce que c'est beau, (ca fait a peu pres du speed a 72%) # todo: ca désynchronise les yeux qui se lisent trop vite ! argh !
        mySystemCall( "aplay -c1 -r%d -fS16_LE -q %s" % ( nFreq, szPathFilename ), bWaitEnd = bWaitEnd );
    else:
        leds = naoqitools.myGetProxy( "ALLeds", True );
        leds.post.fadeRGB( "RightFootLeds", 0xFF0000, 0.7 ); # right in red (skip)
        audioProxy = naoqitools.myGetProxy( "ALAudioPlayer", True );
        # read it in background and check if someone press the right feet a long times => skip text playing
        
        id = audioProxy.post.playFile(szPathFilename);
        if( not bWaitEnd ):
            # attention: no unpause of analyse dans ce cas la!
            return rLength;
        nbrFramesBumpersPushed = 0;
        nbrFramesBumpersPushedMinToSkip = 2;
        strTemplateKeyName = "Device/SubDeviceList/%sFoot/Bumper/%s/Sensor/Value";
        stm = naoqitools.myGetProxy( "ALMemory" );
        while( audioProxy.isRunning( id ) ):
            time.sleep( 0.1 ); # time for user to release precedent push
            listRightFeetBumpers = stm.getListData( [strTemplateKeyName % ( "R", "Left" ), strTemplateKeyName % ( "R", "Right" )] );
            if( listRightFeetBumpers[0] > 0.0 or listRightFeetBumpers[1] > 0.0 ):
                nbrFramesBumpersPushed += 1;
                if( nbrFramesBumpersPushed >= nbrFramesBumpersPushedMinToSkip ):
                    print( "sayAndCache: skipping current text reading because users press on right bumpers" );
                    audioProxy.stop( id );
        leds.post.fadeRGB( "RightFootLeds", 0x000000, 0.2 ); # turn off it
        # while - end
    #if( bDirectPlay ) - end
    analyseSound_resume( True );
  # if( not bJustPrepare ) - end
  print( "sayAndCache: End !!!");
  return rLength;
# sayAndCache - end



def sayAndCacheAndLight( strTextToSay, bJustPrepare = False, bStoreToNonVolatilePath = False, nEyesColor = 0, nUseLang = -1 ):
    "say a cached text with light animation"
    "nEyesColor: 0: white, 1: blue, 2: green; 3: red"
    "nUseLang: if different of -1: speak with a specific languages (useful, when text are already generated: doesn't need to swap languages for nothing!"
    "return the length of the text in seconds, or None if impossible"
    print( "sayAndCacheAndLight( '%s', bJustPrepare: %s, bStoreToNonVolatilePath: %s, nEyesColor: %s, nUseLang: %s )" % ( strTextToSay, str( bJustPrepare ), str( bStoreToNonVolatilePath ), str( nEyesColor ), str( nUseLang ) ) );
    if( not config.bPrecomputeText ):
        print( "sayAndCacheAndLight: disabled by configuration: bPrecomputeText is false" );
        if( bJustPrepare ):
            return None; # do nothing
        tts = naoqitools.myGetProxy( "ALTextToSpeech" );
        tts.say( strTextToSay );
        return None;

    rLength = sayAndCache( strTextToSay, bJustPrepare = True, bStoreToNonVolatilePath = bStoreToNonVolatilePath, nUseLang = nUseLang, bCalledFromSayAndCacheFromLight = True ); # we store it to disk, only if we must do it

    # this two lines are done too in sayAndCache...
    strTextToSay = assumeTextHasDefaultSettings( strTextToSay, nUseLang );
    szFilename = sayAndCache_getFilename( strTextToSay, nUseLang );

    szPathVolatile = pathtools.getVolatilePath();
    rSampleLenSec = 0.05;
#    szPathFilenamePeak = szPathVolatile + szFilename + ("_%5.3f.egy" % rSampleLenSec);
    szPathFilenamePeak = szFilename + ("_%5.3f.egy" % rSampleLenSec);
    szPathFilenamePeakCache = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szPathFilenamePeak;
    szPathFilenamePeak = szPathVolatile + szPathFilenamePeak;
    anLedsColorSequency = [];
    aBufFile = "";
    bFileGenerated = False;
    if( not filetools.isFileExists( szPathFilenamePeak ) ):
        if( filetools.isFileExists( szPathFilenamePeakCache ) ):
            copyFile( szPathFilenamePeakCache, szPathFilenamePeak );
    if( not filetools.isFileExists( szPathFilenamePeak ) ):
        # generate peak file
        timeBegin = time.time();
        print( "sayAndCacheAndLight: generating peak light - begin\n" );
        szPathFilename = szPathVolatile + szFilename + ".raw";
        anLedsColorSequency = [];
        try:
            une = naoqitools.myGetProxy( 'UsageNoiseExtractor' );
            anLedsColorSequency = une.analyseSpeakSound( szPathFilename, int( rSampleLenSec * 1000 ), False );
        except BaseException, err:
            print( "ERR: sayAndCacheAndLight( '%s' ): err: %s" % ( strTextToSay, str( err ) ) );
            print( "ERR: sayAndCacheAndLight => trying old cpp version" );
            anLedsColorSequency = analyseSpeakSound( szPathFilename, rSampleLenSec * 1000 );
        print( "sayAndCacheAndLight: analyseSpeakSound - end - time: %fs\n" % float( time.time() - timeBegin ) );        
#        print( "anLedsColorSequency: %d samples: %s\n" % ( len( anLedsColorSequency ), str( anLedsColorSequency ) ) );
        
        print( "Writing file with %d peak samples (time: %d)\n" % ( len( anLedsColorSequency ), int( time.time() ) ) );
        #         struct.pack_into( "f"*len( anLedsColorSequency ), aBufFile, anLedsColorSequency[:] );
        for peakValue in anLedsColorSequency:
            aBufFile += struct.pack( "f", peakValue );
        try:
            file = open( szPathFilenamePeak, "wb" );
            file.write( aBufFile );
        except RuntimeError, err:
            print( "ERR: sayAndCacheAndLight( '%s' ): err: %s" % ( strTextToSay, str( err ) ) );
        print( "sayAndCacheAndLight: Written file with a size of %d in '%s'" % ( len( aBufFile ), szPathFilenamePeak ) );
        file.close();
        if( bStoreToNonVolatilePath ):
            copyFile( szPathFilenamePeak, szPathFilenamePeakCache );
        bFileGenerated = True;
        print( "sayAndCacheAndLight: generating peak light - end - time: %fs\n" % float( time.time() - timeBegin ) );
    else:
        if( not bJustPrepare ):
            # read it
            print( "Reading file containing peak samples" );
            try:
                file = open( szPathFilenamePeak, "rb" );
            except RuntimeError, err:
                print( "ERR: sayAndCacheAndLight( '%s' ): err: %s" % ( strTextToSay, str( err ) ) );
                return None;
            try:
                aBufFile = file.read();
                print( "aBufFile len: %d" % len( aBufFile ) );
                nNbrPeak = len( aBufFile ) / struct.calcsize("f");
                anLedsColorSequency = struct.unpack_from( "f"*nNbrPeak, aBufFile );
            finally:
                file.close();

    if( bJustPrepare ):
        return rLength;

#    anLedsColorSequency += (0.05,); # a la fin on laisse les leds un peu allumé (non c'est trop abrupte a voir par ailleurs)
    print( "sending leds order, len: %d" % len( anLedsColorSequency ) );

    bFirst = True;
    if( False ):
        # avec methode postQueueOrders
        strLedsGroup = 'FaceLeds';
        if( nEyesColor == 1 ):
            strLedsGroup = 'AllLedsBlue'; # 'FaceLedsBlue'; mais ca n'existe pas!
        elif( nEyesColor == 2 ):
            strLedsGroup = 'AllLedsGreen';
        elif( nEyesColor == 3 ):
            strLedsGroup = 'AllLedsRed';
        aListOrder = [];
        aListOrder.append( "ALLeds = ALProxy( 'ALLeds')" );
        for value in anLedsColorSequency:
            if( bFirst ):
                bFirst = False;
                rTime = 0.;
            else:
                rTime = 0.02;
            aListOrder.append( "ALLeds.setIntensity( '%s', %f, %f )" % ( strLedsGroup, value, rTime ) );
        aListOrder.append( "ALLeds.fadeRGB( '%s', 0x101010, 0.2 )" % strLedsGroup ); # a la fin on laisse les leds un peu allumé
        postQueueOrders( aListOrder, rSampleLenSec - 0.02 + 0.016 );
    else:
        aRGB = [];
        aTime = [];
        for value in anLedsColorSequency:
            nValue = int( 0xff * value );
            if( nEyesColor == 1 ):
                pass # nValue = nValue
            elif( nEyesColor == 2 ):
                nValue = nValue << 8;
            elif( nEyesColor == 3 ):
                nValue = nValue << 16;
            else:
                nValue = (nValue << 16) | (nValue << 8) | (nValue);
#            print( "0x%s" % nValue );
            aRGB.append( nValue );
            if( bFirst ):
                bFirst = False;
                aTime.append( 0.00 ); # En fait pour le premier coup, on le veut maintenant !
            else:
                aTime.append( rSampleLenSec - 0.00120 );
#        aRGB = [ 0xFFFFFF, 0xFF, 0xFF00, 0xFF0000 ];
#        aTime = [1.0, 1.0, 1.0,1.0];
        aRGB.append( 0x101010 ); # a la fin on laisse les leds un peu allumé
        aTime.append( 0.2 );
#        print( "aRGB: %s" % str( aRGB ) );
#        print( "aTime: %s" % str( aTime ) );
        leds = naoqitools.myGetProxy( 'ALLeds');
        leds.post.fadeListRGB( 'FaceLedsExternal', aRGB, aTime );
    # if test methods - end
    rLength = sayAndCache( strTextToSay, bDirectPlay = True, nUseLang = nUseLang );
    
    if( not bStoreToNonVolatilePath and bFileGenerated ):
        # cleaning file !
        #nothing to do, we don't create it in a hard place
        # os.unlink( szPathFilenamePeak );
        # os.unlink( pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw" );
        pass
    # if - end
    
    return rLength;
    
# sayAndCacheAndLight - end

def sayAndCache_InformProcess():
    "set a peculiar color in eyes before rendering sound"
    leds = naoqitools.myGetProxy( "ALLeds" );
    for i in range( 4 ):
        leds.post.fadeRGB( 'FaceLed' + str( i*2 ), 0xFF00, 0.1 );
        leds.post.fadeRGB( 'FaceLed' + str( i*2+1 ), 0x00FF, 0.1 );
# sayAndCache_InformProcess - end

def sayAndCache_InformProcess_end():
    "set a peculiar color in eyes before rendering sound"
    leds = naoqitools.myGetProxy( "ALLeds" );
    leds.post.fadeRGB( 'FaceLeds', 0x8080FF, 0.1 );
# sayAndCache_InformProcess - end
    

def sayMumbled( strText ):
    sayAndCache( strText, bJustPrepare = True );
    strText = assumeTextHasDefaultSettings( strText );
    szFilename = sayAndCache_getFilename( strText );
    szPathFilename = pathtools.getVolatilePath() + szFilename + ".raw";
    szProcessed = szPathFilename + "_mumbled.raw";
    if( not processSoundMumbled( szPathFilename, szProcessed ) ):
        return False;
    nFreq = 22050;
    mySystemCall( "aplay -c1 -r%d -fS16_LE -q %s" % ( nFreq, szProcessed ) );    
    return True;
# sayMumbled - end
    


def uiSay( strText ):
    strSpeed = "\\RSPD=%d\\ " % config.nSpeakSpeedUI;
    sayAndCache( strSpeed + strText, bJustPrepare = False, bStoreToNonVolatilePath = True ); 
# uiSay - end

def transcriptFloat( rVal ):
    "convert a float to a string speechable"
    "5.3 => '5 point 3'"
    nPart1 = int( rVal );
    nMultiplicatorForPrecision = 1000000000;
    nPart2 = round( ( rVal - nPart1 ) * nMultiplicatorForPrecision );
    nSignifiantZero = 0;
    if( nPart2 == 0 ):
        return "%d" % nPart1;
    while( nPart2 * math.pow( 10, nSignifiantZero ) < nMultiplicatorForPrecision ):
        nSignifiantZero += 1;
    nSignifiantZero -= 1;
    while( nPart2 % 10 == 0 and nPart2 > 0 ):
        nPart2 /= 10;
    #~ print( "modf: " + str( math.modf( rVal ) ) );
    #~ print( "trunc: " + str( math.trunc( rVal ) ) );
    strSignifiantZero = "zero " * nSignifiantZero;
    return "%d point %s%d" % ( nPart1, strSignifiantZero, nPart2 );
# transcriptFloat - end

#print( "transcriptFloat: " + transcriptFloat( 5.00123 ) );
#print( "transcriptFloat: " + transcriptFloat( 0.0 ) );

