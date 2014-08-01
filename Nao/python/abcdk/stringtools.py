# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# String tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with string."""

print( "importing abcdk.stringtools" );


def findNumber( strText, nMinValue = -99999999, bFindLast = False ): # todo: int_min
    "find a number (int or float) indication in a text line"
    "return the number or None"
    nLen = len( strText );
    nBegin = -1;
    nValueToRet = None;
    bStop = False;
    for i in range( nLen ):
#        debugLog( "findNumber: i: " + strText[i] );
        if( strText[i].isdigit() or strText[i] == '.' ):
            if( nBegin == -1 ):
                nBegin = i;
            if( i+1 == nLen ):
                # la chaine se termine par un chiffre, il faut l'analyser maintenant
                bStop = True;
                i += 1; # car on veut utiliser ce dernier charactere aussi
        else:
            if( nBegin != -1 ):
                bStop = True;
        if( bStop ):
            # print( "trying: '%s'" % strText[nBegin:i] );
            try:
                n = int( strText[nBegin:i] );
            except:                
                try:
                    n = float( strText[nBegin:i] );
                except:
                    nBegin = i;
                    continue; # burk number
            # print( "findNumber(temp): in '%s': %s" %( strText, str( n ) ) );
            if( n > nMinValue ):
                if( not bFindLast ):
                    return n;
                nValueToRet = n; # memorise for later use
            # if( n > nMinValue ) - end
            bStop = False;
            nBegin = -1;
    return nValueToRet; 
# findNumber - end

def autoTest():
    strNumber = "<br><strong>My IP Country Latitude</strong>: (46) <br><b>My IP Address City</b>:&nbsp;&nbsp; <font color='#980000'>Pa";
    nVal = findNumber( strNumber );
    print( "nVal: %s" % str( nVal ) );
    strNumber = "blablabla 3.59";
    nVal = findNumber( strNumber );
    print( "nVal: %s" % str( nVal ) );
    assert( nVal == 3.59 );
# autoTest - end

#autoTest();