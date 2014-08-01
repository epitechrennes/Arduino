# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Choregraphe tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Choregraphe tools"""
print( "importing abcdk.choregraphetools" );

import debug
import naoqitools

def boxGetParentName( strBoxName, nParentLevel = 1 ):
    "analyse box name and get the name of parent - in the future we will juste make a self.getParent().getName()"
    "nParentLevel: level of parentness, 2 => grandfather, ..."
    listBoxName = boxExplodeBoxName( strBoxName );
    for i in range( 0, nParentLevel ):
        listBoxName.pop(); # remove last name
    strParentBoxName = "__".join( listBoxName );
#    print( "%s -> %s" % ( strBoxName, str( strParentBoxName ) ) );
    return strParentBoxName;
# boxGetParentName - end

def boxGetLastName( strBoxName ):
    "analyse box name and get the name of the last box - in the future we will juste make a self.getParent().getName()"
    listBoxName = boxExplodeBoxName( strBoxName );
    return listBoxName.pop(); # remove last name
# boxGetLastName - end

def boxPathNameToBoxName( strBoxName ):
    "transform complete choregraphe name to a boxName ALFrameManager__0xace99400__root__cascadedtemplatewhile_1 => cascadedtemplatewhile"
    lastName = boxGetLastName( strBoxName );
    listUnderScored = lastName.split( "_" );
    listUnderScored.pop();
    lastName = "_".join( listUnderScored );

    return lastName; # remove last name
# boxPathNameToBoxName - end

def boxExplodeBoxName( strBoxName ):
    "analyse box name and return all the path of a box ALFrameManager__0xace99400__root__cascadedtemplatewhile_1 => ['ALFrameManager', '0xace99400', 'root', 'cascadedtemplatewhile_1']"
    listBoxName = strBoxName.split( "__" );
    return listBoxName;
# boxExplodeBoxName - end

global_coloriseBox_ActivateOneBox_allBoxState = []; # will contents [ ["pathboxname", nbrActivation], ...]

def coloriseBox_ActivateOneBox_internal( strPathBoxName, bActivate = True ):
    "add an activation color to a single level box"
    global global_coloriseBox_ActivateOneBox_allBoxState;
    debug( "coloriseBox_ActivateOneBox_internal( '%s', %d )" % ( strPathBoxName, bActivate ) );

    global global_SectionCritique;
    while( global_SectionCritique.testandset() == False ):
        debug( "coloriseBox_ActivateOneBox_internal: locked" );
        time.sleep( 0.05 );

    nIdx = -1;
    for i in range( len( global_coloriseBox_ActivateOneBox_allBoxState ) ):
        if( global_coloriseBox_ActivateOneBox_allBoxState[i][0] == strPathBoxName ):
            nIdx = i;
            break;
    if( nIdx == -1 ):
        # first time
        nIdx = len( global_coloriseBox_ActivateOneBox_allBoxState );
        global_coloriseBox_ActivateOneBox_allBoxState.append( [ strPathBoxName, 0 ] );

    strBoxName = choregrapheBoxPathNameToBoxName( strPathBoxName );
    debug( "coloriseBox_ActivateOneBox_internal: '%s' last => '%s'" % ( strPathBoxName, strBoxName ) );
    if( bActivate ):
        global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] +=1;
        if( global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] == 1 ):
            # colorise it!
            controller = naoqitools.myGetProxy( "ALChoregrapheController" );
            try:
                controller.setBoxTitleColor( strBoxName, 0., 0., 1. );
            except BaseException, err:
                debug( "coloriseBox_ActivateOneBox_internal: Exception catched: %s" % err );
    else:
        global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] -=1;
        if( global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] == 0 ):
            # reset it!
            controller = naoqitools.myGetProxy( "ALChoregrapheController" );
            try:
                controller.setBoxTitleColor( strBoxName, 0., 0., 0. );
            except BaseException, err:
                debug( "coloriseBox_ActivateOneBox_internal: Exception catched: %s" % err );


    global_SectionCritique.unlock();
# coloriseBox_ActivateOneBox_internal - end

def coloriseBox_Activate( strPathBoxName, bActivate = True ):
    "colorise the title of a box and all its parents, to show it's activity"
    "we will memorise for each box, the number of child activated, so it will show the state of all child"
    try:
        controller = naoqitools.myGetProxy( "ALChoregrapheController" );
    except:
        return; # no controller found...

    strParentName = boxGetParentName( strPathBoxName );
    if( strParentName != "root" ):
        coloriseBox_ActivateOneBox_internal( strParentName, bActivate );

    # activate this level
    coloriseBox_ActivateOneBox_internal( strPathBoxName, bActivate );
# coloriseBox_Activate - end

def coloriseBox_Desactivate( strPathBoxName ):
    return coloriseBox_Activate( strPathBoxName, False );
# coloriseBox_Desactivate - end



def boxGetFrameNumber( strPathBoxName ):
    "Get the frame number of the timeline of a box running in a timeline"
    "return None if the box isn't in a timeline"
    strTimelineName = boxGetParentName( strPathBoxName, 3 );
    try:
        mem = naoqitools.myGetProxy( "ALMemory" );
        nVal = mem.getData( strTimelineName );
        return nVal;
    except BaseException, err:
#        print( "WRN: boxGetFrameNumber: error is: %s" % str( err ) );
        return None;
# boxGetFrameNumber - end

class FrameNumber:
    def __init__( self ):
        self.animations_FrameNumber = dict(); # will store for each total box name the number of frame in the enclosed box
    
    def reset( self ):
        self.animations_FrameNumber = dict(); 
        
    def resetBox( self, strPathBoxName ):
        "reset the sub tree of one box"
        debug.debug( "INF: choregraphetools.FrameNumber.resetBox( '%s' )" % strPathBoxName );    
        self.animations_FrameNumber[strPathBoxName] = 0;
    # resetBox - end
    
    def increaseParent( self, strPathBoxName ):
        "called from children"
        fm = naoqitools.myGetProxy( "ALFrameManager" );
        nNbrFrame = fm.getMotionLength( strPathBoxName ) * fm.getTimelineFps( strPathBoxName );
        debug.debug( "INF: choregraphetools.FrameNumber.increaseParent( '%s' ), nNbrFrame: %d )" % ( strPathBoxName, nNbrFrame ) );
        strBoxParentName = boxGetParentName( strPathBoxName );
        try:
            self.animations_FrameNumber[strBoxParentName] += nNbrFrame;
        except:
            # not existing => create it
            self.animations_FrameNumber[strBoxParentName] = nNbrFrame;
    # increaseParent - end
    
    def get( self, strPathBoxName ):
        try:
            nNbrFrame = self.animations_FrameNumber[strPathBoxName];
        except:
            nNbrFrame = 0;
        debug.debug( "INF: choregraphetools.FrameNumber.get( '%s' ): %d" % ( strPathBoxName, nNbrFrame ) );
        return nNbrFrame;
    # get - end
    
# class FrameNumber - end

frameNumber = FrameNumber(); # the singleton

#~ frameNumber.resetBox( "toto" );
#~ frameNumber.increaseParent( "toto__tutu" );
#~ print( "fng: %d" + frameNumber.get( "toto" ) );
