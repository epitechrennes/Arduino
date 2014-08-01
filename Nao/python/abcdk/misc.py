# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Misc tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Misc tools"

print( "importing abcdk.misc" );

import os
import constants


def reloadAllModules():
    allModules = constants.allModuleName;
    strLocalPath = os.path.dirname( __file__ );
    strThisModuleName = os.path.basename( __file__ ).split('.')[0];
    print( "abcdk.misc.reloadAllModules: reloading all abcdk module, from this path '%s'" % strLocalPath );
    for strModuleName in allModules:
        if( strModuleName == strThisModuleName ): # zap this module
            continue;
        print( "reloading '%s'" % strModuleName );
        obj = __import__( strModuleName, globals() );
        reload( obj );
# reloadAllModules - end

def duplicateList( pOriginalList ):
    "totally duplicate a list object, even if it contents enclosed list or sub enclosed list..."
    newlist = [];
#    newList = pOriginalList;
    for elem in pOriginalList:
        if( isinstance( elem, list ) ):
            newlist.append( duplicateList( elem ) );
        else:
            newlist.append( elem );
    return newlist;
# duplicateList - end

def duplicateList_test():
    "test the duplicateList method"
    def mafuncChange( somelist ):
        "without duplication"
        for i in range( len(somelist) ):
            somelist[i][0]*=2;
            
    def mafunc( pSomelist ):
        "with duplication"
        somelist = duplicateList( pSomelist );
        mafuncChange( somelist );

    maliste= [[1],[3],[5],[10,20,30],[[100,200]], ];

    print( str( maliste ) );
    mafunc( maliste );
    print( str( maliste ) );    
    mafuncChange( maliste );
    print( str( maliste ) );
# duplicateList_test - end
    
# duplicateList_test();