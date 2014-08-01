# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Profiler tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Profiler tools"""
print( "importing abcdk.profiler" );

import naoqitools

def getBoxConstantName( strPathBoxName ):
    "extract from a long choregraphe name, a short name"
    "eg: ALFrameManager__0xad95c6c0__root__TestBattery_4  => TestBattery_4"
    strPick = "__root";
    nPos = strPathBoxName.find( strPick );
    return "Box_" + strPathBoxName[nPos+len(strPick)-4:];
# getBoxConstantName - end

#~ print( getBoxConstantName( "ALFrameManager__0xad95c6c0__root" ) );
#~ print( getBoxConstantName( "ALFrameManager__0xad95c6c0__root__TestBattery_4" ) );

def startBox( strBoxName ):
    up = naoqitools.myGetProxy( "UsageProfiler" );
    up.startMeasure ( getBoxConstantName( strBoxName ), "", "", 0 );
# startBox - end
    
def stopBox( strBoxName ):
    up = naoqitools.myGetProxy( "UsageProfiler" );
    up.stopMeasure( getBoxConstantName( strBoxName ), "", "", 0 );
# startBox - end

class UsageProfilerHelper:
    "A small helper to use UsageProfiler"
    "just create it in some methods"
    def __init__( self, pstrModuleName, pstrFunctionName = "",  pstrTaskName = "" ):
        self.up = naoqitools.myGetProxy( "UsageProfiler" );
        self.strModuleName = pstrModuleName;
        self.strFunctionName = pstrFunctionName;
        self.strTaskName = pstrTaskName;
        self.up.startMeasure( pstrModuleName, pstrFunctionName, pstrTaskName, -1 );
    # __init__ - end
    
    def __del__( self ):
        self.up.stopMeasure( self.strModuleName, self.strFunctionName, self.strTaskName );
    # __del__ - end
    
    #~ def idle( self ):
        #~ "fait croire au systme que l'objet est utilisé est donc qu'il ne faut pas le garbager tout de suite"
        #~ if( self.up == 421 ): # impossible...
            #~ self.strModuleName = "pipi";
    #~ # idle - end        
    
# class UsageProfilerHelper - end

def UsageProfilerHelperBox( strBoxName ):
    "use UsageProfilerHelper in a choregraphe box"
    return UsageProfilerHelper( getBoxConstantName( strBoxName ) );
# startBox - end
