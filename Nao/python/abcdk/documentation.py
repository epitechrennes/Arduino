# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Documentation tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Aldebaran Behavior Complementary Development Kit: documentation module"""

import cache
import config
import constants
import documentation
import debug
import evaltools
import filetools
import misc
import naoqitools
import pathtools
import profiler
import system
import test
import typetools

def generateDocumentation( objectToDocument, bShowPrivate = False, nBaseLevel = 0 ):
    "return a documentation of all methods and objects contains in an object"
    class Dummy:
        """ a small class just to deduce class type further"""
        def __init__(self):
            pass
    # class Dummy - end
    
    strDoc = "";
    nLenHashLine = 60;
    strDoc += "#" + " " * nBaseLevel + "-" * nLenHashLine + "\n";
    try:
        strName = objectToDocument.__name__;
    except:
        strName = "(noname)";
    try:
        strTypeName = type( objectToDocument ).__name__;
    except:
        strTypeName = "(noname)";        
    strDoc += "#" + " " * nBaseLevel + " %s '%s': %s\n" % ( strTypeName, strName, str( objectToDocument.__doc__ ) );
    strDoc += "#" + " " * nBaseLevel + "-" * nLenHashLine + "\n";
#    strDoc += "# summary:\n";
    stdDocClass = "";
    stdDocMethod = "";
    stdDocData = "";
    
    for attrName in dir( objectToDocument ):
        if( not bShowPrivate and ( attrName[0:2] == '__' or attrName[0:4] == "dict" ) ):
            continue;
        some_object = getattr( objectToDocument, attrName );
        try:
            if( isinstance( some_object, type(constants) ) ): # quand on importe un module, il apparait dans le scope de l'objet qui l'a importé
                continue;
        except BaseException, err:
            print( "ERROR: generateDocumentation: pb on object '%s' (err:%s)" % ( attrName, err ) );
#            continue;
        strDesc = "";
        if( typetools.isDict( some_object ) ):
            strDesc = "a dictionnary.";
        elif( isinstance( some_object, type( bool ) ) ):
            strDesc = "a bool.";
        elif( typetools.isInt( some_object ) ):
            strDesc = "an integer.";
        elif( isinstance( some_object, float ) ):
            strDesc = "a float.";            
        elif( isinstance( some_object, list ) ):
            strDesc = "a list.";            
        elif( typetools.isString( some_object ) ):
            strDesc = "a string.";            
        elif( isinstance( some_object, type( Dummy ) ) ):
            attrName = "class " + attrName;
            strDesc = some_object.__doc__;
        else:
            if( some_object.__doc__ == None ):
                strDesc = "TODO: DOCUMENT ME";
            else:
                strDesc = some_object.__doc__;
        if( isinstance( some_object, type( generateDocumentation ) ) ):
            attrName = attrName + "(" + ")";
        strToAdd = "#" + " " * nBaseLevel + " - %s: %s\n" % ( attrName, strDesc );
        if( isinstance( some_object, type( generateDocumentation ) ) ):
            stdDocMethod += strToAdd;
        elif( isinstance( some_object, type( Dummy ) ) ):
            stdDocClass += strToAdd;
            stdDocClass += generateDocumentation( some_object, nBaseLevel = nBaseLevel + 6 );            
        else:
            stdDocData += strToAdd;
    if( stdDocClass != "" ):
        strDoc += "#" + " " * nBaseLevel + " Class:\n" + stdDocClass;            
    if( stdDocMethod != "" ):
        strDoc += "#"+ " " * nBaseLevel +" Method:\n" + stdDocMethod;
    if( stdDocData != "" ):
        strDoc += "#"+ " " * nBaseLevel +" Data:\n" + stdDocData;
    strDoc += "#" + " " * nBaseLevel + "-" * nLenHashLine + "\n";            
    return strDoc;
# generateDocumentation - end

def generateAllDocumentation():

    strDoc = "";
    strDoc += '#' * 60 + "\n";
    strDoc += "### Aldebaran Behavior Complementary Development Kit: Full Module documentation  ###\n";
    strDoc += '#' * 60 + "\n";

    allModules = constants.allModuleName;
    for strModuleName in allModules:
        if( strModuleName  == "documentation" ):
            continue; # weird: it doesn't accept this module type anymore
        #import importlib # argh require python 2.7. #=> faire les import a la main
        # importlib.import_module( strModuleName ); 
        strDoc += generateDocumentation( eval( strModuleName ) );

    print( strDoc );    

# print( generateDocumentation( constants ) );

# try to get params info:
#print( generateDocumentation( generateDocumentation, bShowPrivate = True ) );
#import inspect
#print( "le truc: " + inspect.getdoc(generateDocumentation) or inspect.getcomments(generateDocumentation) );
#    args, varargs, varkw = getargs(func.func_code)


# TODO: generer aussi les html avec pydoc
#import pydoc
#pydoc.writedocs( "config" )

#generateAllDocumentation();