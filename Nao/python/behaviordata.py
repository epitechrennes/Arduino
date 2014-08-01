# -*- coding: utf-8 -*-

###########################################################
# The brain of nao - v1.29 (penser a reporter le version number dans getVersion)
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2009 All Rights Reserved - This file is confidential.
###########################################################
#import sys
#import os
#sys.path.append(os.getcwd())


def getVersion():
    return 1.29;
# getVersion - end

import xml.dom.minidom
import altools
import random
import time
import mutex
import os
import array
import sys
import math
try: 
    import Image
    import ImageDraw    
except BaseException, err:
    print( "WRN: behaviordata: module image loading error: " + str( err ) );


altools.const.area_stay_sit = 0
altools.const.area_stay_there = 1
altools.const.area_limited = 2
altools.const.area_free = 3

altools.const.state_stopped = 0
altools.const.state_running = 1
altools.const.state_freeze = 2

altools.const.step_unknown = 0
altools.const.step_paused = 1
altools.const.step_init = 2
altools.const.step_wait = 3


altools.const.order_none = 0
altools.const.order_sit = 1
altools.const.order_stand = 2
altools.const.order_behavior = 3
altools.const.order_freeze_a_little = 4
altools.const.order_sit_and_freeze = 5
altools.const.order_stand_and_freeze = 6


def isTextContainsBoolAndIsTrue( strText ):
    "return true if the text contains bool"
    return ( len( strText ) > 1 and strText[1] == 'r' ) or strText[0] == '1';
# isTextContainsBoolAndIsTrue - end

def typeToString( value ):
    theType = type( value );
    if( theType == type( 0 ) ):
        return 'int';
    elif( theType == type( 's' ) ):
        return 'str';
    elif( theType == type( 0.0 ) ):
        return 'flo';
    elif( theType == type( [] ) ):
        return 'arr';        
    else:
        return 'unknown type';
# typeToString - end

def timeToHuman( oneTime ):
    "convert a time.time() to a string humanized"
    "if will be expressed compared to current time"
    strFormatDate = "%Y/%m/%d ";    
    strFormatTime = "%Hh%Mm%S";
    strOut = "";
    strLocal = time.strftime( strFormatDate, time.localtime( oneTime ) );
    strNow = time.strftime( strFormatDate, time.localtime() );
    if( strNow != strLocal ):
        # ce n'est pas le meme jour, on va préciser la date
        strOut = strLocal;
    strOut += time.strftime( strFormatTime, time.localtime( oneTime ) );
    return strOut;
# timeToHuman - end
    

class UsageData:
    
    def __init__(self, strName = None ):
        self.mutex = mutex.mutex();        
        self.strName = strName;
        self.allValue = [];  # a big array of triple [time, type, value] en fait maintenant on va simplifier: juste: [time, type, value], car c'est deja self explained
        # precomputed value:
        self.lastValue = None; 
        if( strName != None ):
            self.readFromFile();
    # __init__ - end
    
    def __del__(self):
        print( "INF: UsageData.__del__ called" );
        self.writeToFile();
    # __del__ - end
    
    def updateData( self, value ):
#        print( "INF: UsageData.updateData: %s set to '%s'" % ( self.strName, str( value ) ) );
        while( self.mutex.testandset() == False ):
            print( "UsageData(%s).updateData: locked" % self.strName );
            time.sleep( 0.1 ); 
#        self.allValue.append( [ time.time(), typeToString( value ), value ] );
        self.allValue.append( [ time.time(), value ] );
        if( len( self.allValue ) > 200 ):
            print( "%s: UsageData(%s).updateData: reducing history" % ( altools.getHumanTimeStamp(), self.strName ) ); # permet aussi de voir si il n'y a pas des valeurs dans lesquels on poste un peu trop souvent
            self.allValue = self.allValue[-100:]; # ne garde que les 100 derniers !
        self.lastValue = value;
        self.mutex.unlock();
    # updateData - end
    
    def getData( self ):
#        print( "INF: UsageData.getData of %s return '%s'" % ( self.strName, str( self.lastValue ) ) );
        return self.lastValue;
    # getData - end    
    
    def getDataHist( self, nNbrValue = 3 ):
        if( len( self.allValue ) < 1 ):
            return [];
        elif( len( self.allValue ) < nNbrValue ):
            nNbrValue = len( self.allValue );
        return self.allValue[-nNbrValue:];
    # getDataHist - end
    
    def getDataHistLength( self ):
        return len( self.allValue );
    # getDataHistLength - end
    
    
    @staticmethod 
    def getVarPath():
        return altools.getCachePath() + 'var' + altools.getDirectorySeparator();
    # getVarPath - end
    
    # je ne sais pas pourquoi dans cette classe il veut pas que j'appelle UsageData.getVarPath() (depuis une méthode non statique) (c'est nul ca!!!)
    def __getVarPath_Inner__( self ):
        import altools        
        return altools.getCachePath() + altools.getDirectorySeparator() + 'var' + altools.getDirectorySeparator();
    # getVarPath - end
    
    def readFromFile( self ):
        print( "INF: UsageData.readFromFile: reading previous value for %s" % self.strName );
        while( self.mutex.testandset() == False ):
            print( "UsageData(%s).readFromFile: locked" % self.strName );
            time.sleep( 0.1 );         
        cleanedName = str.replace( self.strName, "/", "__" );
        filename = self.__getVarPath_Inner__() + cleanedName + '.dat';
        try:
            file = open( filename, 'rb' );
            if( file ):
                buf = file.read();
                file.close();
                self.allValue = eval( buf );
                if( len( self.allValue ) > 0 ):
                    self.lastValue = self.allValue[len(self.allValue)-1][1]; # 1 is the index of the value
                    print( "INF: UsageData.readFromFile: lastValue: %s"% str( self.lastValue ) );
        except BaseException, err:
            altools.debug( "WRN: UsageData.readFromFile(%s)\nWRN: error: '%s'\nWRN: => no value readed" % ( filename, err) );
        self.mutex.unlock();
    # readFromFile - end
    
    def writeToFile( self ):
        print( "INF: UsageData.writeToFile: storing value for %s (%d value(s))" % ( self.strName, len( self.allValue ) ) );
        while( self.mutex.testandset() == False ):
            print( "UsageData(%s).writeToFile: locked" % self.strName );
            time.sleep( 0.1 );        
#        print( "allValue: %s"% str( self.allValue ) );
        cleanedName = str.replace( self.strName, "/", "__" );
        filename = self.__getVarPath_Inner__() + cleanedName + '.dat';
        try:
            file = open( filename, 'wb' );
            if( file ):
                buf = str( self.allValue );
                
                #~ buf = "[";
                #~ for value in self.allValue:
                    #~ buf += "[%s,%s,%s]" % ( value[0], typeToString, str( value[2] ) );                    
                #~ buf += "]";
                
                file.write( buf );
                file.close();
                
        except BaseException, err:
            import altools # because when exiting, altools is sometimes already unloaded
            altools.debug( "WRN: UsageData.writeToFile(%s) error: '%s'" % ( filename, err ) );
            pass
        self.mutex.unlock();
    # writeToFile - end
    
    def exportToALMemory( self ):
        "write all value of this variable to the ALMemory"
        mem = altools.myGetProxy( "ALMemory" );
        while( self.mutex.testandset() == False ):
            print( "UsageData(%s).exportToALMemory: locked" % self.strName );
            time.sleep( 0.1 );        
        strKeyname = "behaviordata/" + self.strName;
#        print( "INF: UsageData.exportToALMemory: exporting value for %s (%d value(s))" % ( self.strName, len( self.allValue ) ) );
        if( mem != None ):
            mem.insertData( strKeyname, self.allValue );
        self.mutex.unlock();
    # exportToALMemory - end
    
    def importFromALMemory( self, strName, strSpecificIP = "localhost" ):
        "read a value from a distant ALMemory on a robot"
        mem = altools.myGetProxy( "ALMemory", strSpecificIP );        
        while( self.mutex.testandset() == False ):
            print( "UsageData(%s).importFromALMemory: locked" % self.strName );
            time.sleep( 0.1 );                
        self.strName = strName;
        strKeyname = "behaviordata/" + self.strName;
        self.allValue = mem.getData( strKeyname );
        self.mutex.unlock();
        print( "self.allValue: " + str( self.allValue ) );
    # importFromALMemory - end
    
    def generateGraph( self ):
        import matplotlib
        import pylab
        while( self.mutex.testandset() == False ):
            print( "UsageData(%s).generateGraph: locked" % self.strName );
            time.sleep( 0.1 );        
        valueToGraph = [];
        listLibelle = [];
        bHasLibelle = False;
        bHasValue = False;
        for i in range( len( self.allValue ) ):
            val = self.allValue[i][1];
            if( altools.isString( val ) ):
                valueToGraph.append( None );
                listLibelle.append( val );
                bHasLibelle = True;
            else:
                valueToGraph.append( val );
                listLibelle.append( '' );
                bHasValue = True;
#        valueToGraph = [ 0, 3, 2, 0, 5, 7 ];
        pylab.plot(valueToGraph);
        pylab.grid( True );
        pylab.title( self.strName );
        if( bHasLibelle ):
            if( not bHasValue ):
                pylab.axis([0,len( self.allValue ),-3,3] );
#            pylab.legend( listLibelle ); # non en fait c'est des etiquettes que je veux et pas une légende !
            for i in range( len( listLibelle ) ):
                pylab.text( i, ((i+2)%5)-2, listLibelle[i] );
            pass
        self.mutex.unlock();
    # generateGraph - end
    
    
    def drawGraph( self, nPosX = 0, nPosY = 0, nSizeX = 320, nSizeY = 200 ):
        "draw a graph on screen showing all values of this data"
        import matplotlib
        import pylab
        
        self.generateGraph();
        
        matplotlib.pyplot.show()
        matplotlib.pyplot.close();
    # drawGraph - end    
        
    
    def saveGraph( self, strFilename = "" ):
        "save a png file showing all values into a graph"
        import matplotlib
        import pylab
        
        try:
            if( len( self.allValue ) < 1 ):
                return False;
            strGraphPath = self.__getVarPath_Inner__() + "graph/";
            if( strFilename == "" ):
                try:
                    os.makedirs( strGraphPath );
                except:
                    pass
                strFilename =  strGraphPath + str.replace( self.strName, "/", "__" ) + ".png";
            print( "UsageData.saveGraph: saving graph of variable to file '%s'" % ( strFilename ) );
            self.generateGraph();
            matplotlib.pyplot.savefig( strFilename, format="png", transparent=True); # dpi=50 => 400x300 au lieu de 800x600
            matplotlib.pyplot.close()
        except BaseException, err:
            altools.debug( "WRN: UsageData.saveGraph(%s) error: '%s'" % ( self.strName, err ) );
            return False;
        return True;
    # saveGraph - end
    
    
# class UsageData - end

class UsageDataManager:
    """ store data with history"""
    def __init__(self):
        print( "INF: UsageDataManager.__init__ called" );
        self.allData = {};
        self.mutexListData = mutex.mutex();
        try:
            os.makedirs( UsageData.getVarPath() );
        except:
            pass # le dossier existe deja !
    # __init__ - end
    
    def __del__(self):
        print( "INF: UsageDataManager.__del__ called" );
        self.exportToALMemory(); # before that we export one time to the ALMemory, it doesn't cost a lot and can help users later (debug or...)
        self.allData = {};
    # __del__ - end

    def updateData( self, strName, value ):
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.updateData(%s): locked" % strName );
            time.sleep( 0.1 ); 
        if( not strName in self.allData ):
            self.allData[strName] = UsageData( strName );
        self.mutexListData.unlock();
        self.allData[strName].updateData( value ); # on ne mutex pas l'update (ca sera fait dans la méthode)
    # updateData - end
    
    def getData( self, strName, defautValue = altools.const.state_unknown ):
        if( not strName in self.allData ):
            altools.debug( "WRN: UsageDataManager.getData not found: '%s' returning default" % strName, bIgnoreDuplicateMessage = True );
            return defautValue;
        return self.allData[strName].getData();
    # getData - end
    
    def loadAll( self ):
        "load all variables present on disk in the normal path"
        "That's usefull before calling saveGraphs"
        print( "INF: UsageDataManager.loadAll called" );
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.loadAll: locked" );
            time.sleep( 0.1 );         
        strPath = UsageData.getVarPath();
        allFiles = altools.findFile( strPath,  ".dat", False );
        for file in allFiles:
            strVarName = str.replace( file, strPath, "" );
#            strVarName = str.replace( strVarName, "extracted_data__", "" );
            strVarName = str.replace( strVarName, ".dat", "" );
#            print( strVarName );
            if( not strVarName in self.allData ):
                self.allData[strVarName] = UsageData( strVarName );
        self.mutexListData.unlock();
        print( "loadAll: %d variable(s) loaded" % len( allFiles ) );
    # loadAll - end
    
    def storeAll( self ):
        "store all variable"
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.storeAll: locked" );
            time.sleep( 0.1 );        
        print( "INF: UsageDataManager.storeAll: storing %d variable(s)" % len( self.allData ) );
        for k, v in self.allData.iteritems():
            v.writeToFile();
        self.mutexListData.unlock();
    # storeAll - end
    
    def saveGraphs( self ):
        "store all variable"
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.saveGraphs: locked" );
            time.sleep( 0.1 );        
        print( "INF: UsageDataManager.saveGraphs: graphing %d variable(s)" % len( self.allData ) );
        for k, v in self.allData.iteritems():
            v.saveGraph();
        self.mutexListData.unlock();
    # saveGraphs - end
    
    def exportToALMemory( self ):
        "copy all variable to ALMemory"
        print( "INF: UsageDataManager.exportToALMemory: exporting %d variable(s)" % len( self.allData ) );
        mem = altools.myGetProxy( "ALMemory" );
        if( mem == None ):
            print( "WRN: UsageDataManager.exportToALMemory: can't connect to ALMemory" );
            return;
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.exportToALMemory: locked" );
            time.sleep( 0.1 );            
        allVarName = [];
        mem = altools.myGetProxy( "ALMemory" );
        for k, v in self.allData.iteritems():
            allVarName.append( v.strName );
            v.exportToALMemory();
        mem.insertData( "UsageDataManager_all_vars", allVarName );
        self.mutexListData.unlock();
    # exportToALMemory - end
    
    def importFromALMemory( self, strSpecificIP = "localhost" ):
        "import all variables from a (remote) ALMemory"
        try:
            mem = altools.myGetProxy( "ALMemory", strSpecificIP );
            allVarName = mem.getData( "UsageDataManager_all_vars" );
        except BaseException, err:
            altools.debug( "WRN: importFromALMemory: %s" % str( err ) );
            return;
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.importFromALMemory: locked" );
            time.sleep( 0.1 );            
        self.allData = {};
        for strVarName in allVarName:
            someData = UsageData();
            someData.importFromALMemory( strVarName, strSpecificIP );
            self.allData[strVarName] = someData;
        self.mutexListData.unlock();
        print( "importFromALMemory: %d variable(s) loaded" % len( self.allData ) );
    # exportToALMemory - end
    
    def dumpAll( self ):
        "dump to print all the outputted extracted data"
        print( "UsageDataManager.dumpAll at %d - humantime: %s" % ( int( time.time() ), altools.getHumanTimeStamp() ) );
        print( "*" * 30 );
        while( self.mutexListData.testandset() == False ):
            print( "UsageDataManager.dumpAll: locked" );
            time.sleep( 0.1 );            
        for k, v in self.allData.iteritems():
            strOut = "%s " % ( k );
            strOut += "(%d val): " % v.getDataHistLength();
            aLastValue = v.getDataHist( 3 );
            for val in aLastValue:
                strOut += "%s: %s; " % ( timeToHuman( val[0] ), str( val[1] ) );
            print( strOut );
        print( "*" * 30 );
        self.mutexListData.unlock();        
    # dumpAll - end
    
    def getHist( self, strDataName, nNbrValue = 3 ):
        return self.allData[strDataName].getDataHist( nNbrValue );
    # getHist - end
        
            
        
# class UsageDataManager - end    

usageDataManager = UsageDataManager();
    
  
class ExtractedData:
    """ a small class to transform data access to naoqi code"""
    def __init__(self):
#        self.listListVarDebug = set(); # a list of var to enable debug dumping
        
        # initialisation of some default variable (often string!) (because len(0) => bug)
        self.updateValue( 'ui_state', '' );
        self.updateValue( 'life_last_start', int( time.time() ) );
        
    def __getattr__(self, strValueName, defautValue = altools.const.state_unknown):
        aValue = self.getValue( strValueName, defautValue );
        if( aValue == altools.const.state_unknown ):
            # On imagine qu'on est tout le temps dans cette fonction a cause de l'evaluation des regles (et pas a d'autres moment)
            # par défaut on veut que l'evaluation d'une regle du type if( isRain ) vaille False si la variable n'existe pas, 
            # donc il faut retourner une valeur egale a 0, 
            # et on la retourne en float, car c'est plus sur si jamais c'est utilisé dans des calculs
            aValue = 0.;
        return aValue;        
    # __getattr__ - end
    
    def getValue(self, strValueName, defautValue = altools.const.state_unknown):
        value = defautValue;
        try:
            #mem = altools.myGetProxy( "ALMemory" );
            #value = mem.getData( ExtractedData.getStmRootName() + strValueName );
            value = usageDataManager.getData( ExtractedData.getStmRootName() + strValueName );
        except BaseException, err:
#            altools.debug( "WRN: ExtractedData.getattr: '%s' (Here, when naoqi is present, we should access value contains in '%s' in ALMemory/%s)\n" % ( err, strValueName, ExtractedData.getStmRootName() ) );
            return defautValue;
        return value;
    # getValue - end
    
    def getUnknownValue( self ):
        return altools.const.state_unknown;
    # getValueUknown - end
    
    def updateValue( self, strValueName, value, bPostToALMemoryToo = False ):
        "update a value in the ALMemory extracted_data"
        # debug print value
        if( value == altools.const.state_unknown ):
            strValueToPrint = "unknown";
        elif( altools.isString( value ) ):
            strValueToPrint = "'%s'" % value;
        else:
            strValueToPrint = str( value );
#        altools.debug( "ExtractedData::updateValue %s => %s" % ( strValueName, strValueToPrint ) );
#        self.listListVarDebug.add( strValueName );
        try:
            usageDataManager.updateData( ExtractedData.getStmRootName() + strValueName, value );
            if( bPostToALMemoryToo ):
                print( "extractedData.updateValue: Updating in ALMemory: %s=%s" % ( ExtractedData.getStmRootName() + strValueName, str( value ) ) );
                mem = altools.myGetProxy( "ALMemory" );
                value = mem.raiseMicroEvent( ExtractedData.getStmRootName() + strValueName, value );                
        except BaseException, err:
            print( "ERR: ExtractedData.updateValue: '%s' (Here, when naoqi is present, we should write in ALMemory/%s%s the value '%s')\n" % ( err, ExtractedData.getStmRootName(), strValueName, str( value ) ) );
        return value;    
    # updateValue - end
    
    def dumpAllExtractedData( self ):
        "dump to print all the outputted extracted data"
        #~ print( "ExtractedData.dumpAllExtractedData at %d - humantime: %s" % ( int( time.time() ), altools.getHumanTimeStamp() ) );
        #~ print( "*" * 30 );
        #~ for strName in self.listListVarDebug:
            #~ print( "%s: %s" % ( strName, self.getValue( strName ) ) );
        #~ print( "*" * 30 );        
        usageDataManager.dumpAll();        
    # dumpAllExtractedData - end
        
    @staticmethod
    def getStmRootName():
        return "extracted_data/";
    # getStmRootName - end
# ExtractedData - end

extractedData = ExtractedData();


def domNodeTypeToString( nNodeType ):
    if( nNodeType == xml.dom.minidom.Node.ELEMENT_NODE ):
        return "ELEMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.ATTRIBUTE_NODE ):
        return "ATTRIBUTE_NODE";
    if( nNodeType == xml.dom.minidom.Node.TEXT_NODE ):
        return "TEXT_NODE";
    if( nNodeType == xml.dom.minidom.Node.CDATA_SECTION_NODE ):
        return "CDATA_SECTION_NODE";
    if( nNodeType == xml.dom.minidom.Node.ENTITY_REFERENCE_NODE ):
        return "ENTITY_REFERENCE_NODE";
    if( nNodeType == xml.dom.minidom.Node.PROCESSING_INSTRUCTION_NODE ):
        return "PROCESSING_INSTRUCTION_NODE";
    if( nNodeType == xml.dom.minidom.Node.COMMENT_NODE ):
        return "COMMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.DOCUMENT_NODE ):
        return "DOCUMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.DOCUMENT_TYPE_NODE ):
        return "DOCUMENT_TYPE_NODE";
    if( nNodeType == xml.dom.minidom.Node.DOCUMENT_FRAGMENT_NODE ):
        return "DOCUMENT_FRAGMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.NOTATION_NODE ):
        return "NOTATION_NODE";

    return "unknown type";
# domNodeTypeToString - end

def domNodeToString( node, nDepth = 0, aListChildParentNum = [], aListChildParentName = [] ):
    "print a node list to a string" 
    strTab = "    " *  nDepth;
    if( nDepth > 0 ):
        strTab += "| ";
    strOut = strTab + "--------------------\n";
    if( node == None ):
        return strTab + "None!";
    try:
        strOut += strTab + "nodeType: %d (%s)\n" % ( node.nodeType, domNodeTypeToString( node.nodeType ) );
    except:
        pass
    try:
        strOut += strTab + "localName: '%s'\n" % node.localName;
    except:
        pass
    try:
        strOut += strTab + "nodeName: '%s'\n" % node.nodeName;
    except:
        pass
    try:
        strOut += strTab + "nodeValue: '%s'\n" % node.nodeValue;
    except:
        pass
    try:
        strOut += strTab + "nodeData: '%s'\n" % node.nodeData;
    except:
        pass
#            try:
    if( node.hasChildNodes() ):
            strOut += strTab + "Child(s): %d child(s):\n" % len( node.childNodes );
            nNumChild = 1;
            aListChildParentName.append( node.localName );
            strTotalPath = "";
            for name in aListChildParentName:
                strTotalPath += "/%s" % name;
            for nodeChild in node.childNodes:
                strChildNumberParentPrefix = "";
                for number in aListChildParentNum:
                    strChildNumberParentPrefix += "%d." % number;
                aListChildParentNum.append( nNumChild );
                strOut += strTab + "Child " + strChildNumberParentPrefix + str(  nNumChild ) + " (%s):\n" % strTotalPath+ domNodeToString( nodeChild, nDepth + 1, aListChildParentNum, aListChildParentName );
                aListChildParentNum.pop();
                nNumChild += 1;
            aListChildParentName.pop();
#                    strOut += strTab + "\n";
#            except:
#                strOut += strTab + "(error occurs while accessing to child)";
    strOut += "    " *  nDepth + "--------------------\n";
    return strOut;
# domNodeToString - end

def domGetFirstText(node):
    "travel the node and return the value of the first node type found with type TEXT_NODE"
    "it's a travel in depth first"
    
    if( node != None ):
        if( node.nodeType == node.TEXT_NODE ):
            return node.nodeValue.strip();
        if( node.hasChildNodes() ):
            for nodeChild in node.childNodes:
                text = domGetFirstText( nodeChild );
                if( text != None ):
                    return text;
    return None;
# getText - end

def domFindElement( node, strElementName ):
    "find a child by its name"
    if( not node.hasChildNodes() ):
        if(  node.nodeName == strElementName ):
            return node;
    else:
        for nodeChild in node.childNodes:
            if( nodeChild.nodeName == strElementName ):
                return nodeChild;
    return None;
# domFindElement - end
    
def domFindElementByPath( node, astrElementPathName ):
    """find a child of a child of a child... by its name tree"""
    """eg: ["starting-condition", "condition", "script_type"] """
    element = node;
    for name in astrElementPathName:
        element = domFindElement( element, name );
        if( element == None ):
            return None;
    return element;
# domFindElementByPath - end




class BehaviorDesc:
    "A class to store and evaluate information about a behavior"
    def __init__( self, strPath, strXarName = ""):
        if( strPath[len( strPath ) - 1] != altools.getDirectorySeparator() ):
            strPath += altools.getDirectorySeparator();
        self.strPath = strPath; # the directory where is the xar
        self.strXarName = strXarName;
        self.strStartingConditionScriptType = ""; # the script language (often: python)
        self.strStartingCondition = "False"; # a script directly evaluable condition (transformed from a xml-read condition)
        self.strBehaviorType = "";
        self.aLang = []; # empty => all
        self.rUserNote = -1;
        self.bInterruptableByTimeout = True;
        self.bFallAuthorised = False;
        self.bEnabled = True;
        
        # stats part - saved
        self.nNbrLaunched = 0;
        self.lastLaunch_TimeStart = 0;  # time of start of last launch
        self.lastLaunch_TimeStop = 0;   # time of stop of last launch
        self.rAverage_Duration = 0;        # average duration of launches (in sec)
        self.rHappyNote = 0.;                # an idea of the happyness given to the user by this behavior (related to caress or tap)
        
        # working variables - not saved
        self.bStarted = False;  # is this behaviors started (not stopped)
        
    # __init__ - end
    
    def toString( self ):
        strOut = ".............................\n";
        strOut += "strPath: '%s'\n" % self.strPath;
        strOut += "strXarName: '%s'\n" % self.strXarName;
        strOut += "strVersion: %s\n" % self.strVersion;
        strOut += "bEnabled: %d\n" % int( self.bEnabled );
        strOut += "strStartingConditionScriptType: '%s'\n" % self.strStartingConditionScriptType;
        strOut += "strStartingCondition: '%s'\n" % self.strStartingCondition;
        strOut += "strBehaviorType: '%s'\n" % self.strBehaviorType;
        strOut += "aLang: '%s'\n" % str( self.aLang );
        strOut += "rUserNote: %f\n" % self.rUserNote;
        strOut += "bInterruptableByTimeout: %s\n" % str( self.bInterruptableByTimeout );
        strOut += "bFallAuthorised: %s\n" % str( self.bFallAuthorised );
        strOut += "nNbrLaunched: %d\n" % self.nNbrLaunched;
        strOut += "lastLaunch_TimeStart: %s (since: %d)\n" % ( str( self.lastLaunch_TimeStart ) , int( time.time() - self.lastLaunch_TimeStart ) );
        strOut += "lastLaunch_TimeStop: %s (since: %d)\n" % ( str( self.lastLaunch_TimeStop ) , int( time.time() - self.lastLaunch_TimeStop ) );
        strOut += "rAverage_Duration: %f (last: %d)\n" % ( self.rAverage_Duration, int( self.lastLaunch_TimeStop - self.lastLaunch_TimeStart ) );
        strOut += "rHappyNote: %f\n" % ( self.rHappyNote );
        strOut += "launchable (at this moment): %d\n" % ( self.isLaunchable() );
        strOut += ".............................\n";
        return strOut;
    # toString - end
    
    def getPath( self ):
        return self.strPath;
    # getPath - end
    
    def getXarName( self ):
        return self.strXarName;
    # getPath - end
    
    def getPathXarName( self ):
        return self.getPath(); # + self.getXarName();
    # getPath - end
    
    def isSystem( self ):
        return self.strBehaviorType == "system";
    # isSystem - end
        
      
    def load( self ):
        "load from disk"
        
        print( "BehaviorDesc: loading behavior data in '%s'"  % self.strPath);
        
        try:
            print( "metadata: " + self.strPath + "metadata.xml" );
            metaData = xml.dom.minidom.parse( self.strPath + "metadata.xml" );
        except BaseException, err:
            try:    
                print( "ERR: BehaviorDesc: couldn't load extended data for directory: '%s' => error: '%s'" % ( self.strPath, str( err ) ) );
                print( "ERR: (trying other name as in a local test?)" );
                metaData = xml.dom.minidom.parse( self.strPath + "behaviordata_metadata_sample.xml" );
            except:
                print( "ERR: BehaviorDesc: couldn't load extended data for directory: '%s'" % self.strPath );
                return False;
        self.rUserNote = 0;
        behaviorData = metaData.getElementsByTagName("behavior")[0]; # handle only first behavior
#        print( "behavior:\n" + domNodeToString( behaviorData ) );
        
        self.strBehaviorType = domGetFirstText( domFindElement( behaviorData, 'type' ) );
        strText = domGetFirstText( domFindElement( behaviorData, 'user_note' ) );
        self.rUserNote = float( strText );
        strText = domGetFirstText( domFindElement( behaviorData, 'enabled' ) );
        self.bEnabled = isTextContainsBoolAndIsTrue( strText );
        strText = domGetFirstText( domFindElement( behaviorData, 'version' ) );
        if( strText != None ):
            self.strVersion = str( strText );
        else:
            self.strVersion = "";
        strText = domGetFirstText( domFindElement( behaviorData, 'interruptable_by_timeout' ) );
        if( strText != None ):
            self.bInterruptableByTimeout = isTextContainsBoolAndIsTrue( strText );
        strText = domGetFirstText( domFindElement( behaviorData, 'fall_authorised' ) );
        if( strText != None ):
            self.bFallAuthorised = isTextContainsBoolAndIsTrue( strText );
        strText = domGetFirstText( domFindElement( behaviorData, 'lang' ) );
        if( strText != None ):
            try:
#                print( "TODO: text: %s" % strText );
                self.aLang = eval( strText );
#                print( "TODO: self.aLang: %s" % str( self.aLang ) );
                if( self.aLang  == "all" or "all" in self.aLang ): # handle "all" and ["all"]
                    # default: empty => all
#                    print( "resetting language - trucmuche !!!" );
                    self.aLang = [];
            except BaseException, err:
                print( "ERR: load, error parsing lang params: '%s', err: %s" % ( strText, str( err ) ) );
                self.aLang = [];
        # if( strText != None ) - end
        self.strStartingConditionScriptType = domGetFirstText( domFindElementByPath( behaviorData, ["starting-condition","condition","script_type"] ) );
        self.strStartingCondition = domGetFirstText( domFindElementByPath( behaviorData, ["starting-condition","condition","condition_value"] ) );
        # pythonise condition
        self.strStartingCondition = self.strStartingCondition.replace( "nao.", "extractedData." );
        self.strStartingCondition = self.strStartingCondition.replace( "env.", "extractedData." );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "false", "False" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "true", "True" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "last_start", "last_start()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "last_stop", "last_stop()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "now", "time.time()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "hour", "extractedData.hour" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "minute", "extractedData.minute" );
        
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "nao.is_excited", "isExcited()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "nao.is_nearly_excited", "isNearlyExcited()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "nao.is_sleepy", "isSleepy()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "nao.is_sleeping", "isSleeping()" );
        self.strStartingCondition = altools.replaceWord( self.strStartingCondition, "nao.is_deep_sleeping", "isDeepSleeping()" );
        
        # copy some variables to make the evaluation works
        life = altools.myGetProxy( 'ALLife' );
        extractedData.updateValue( 'is_master', life.isMaster() );
        extractedData.updateValue( 'is_feet_fixed', life.isFeetFixed() );
        extractedData.updateValue( 'is_disable_stiffness', life.isDisableStiffness() );
            
        metaData.unlink(); # clean the document
        
        return True;
    # load - end
  
    def isLaunchable( self, aAuthorizedBehaviorType = False, strCurrentLang = "" ):
        "Analyse the starting condition"
        "return True or False"
        
#        altools.debug( "INF: behaviordata.isLaunchable: testing %s" % ( self.strPath ) );

        if( aAuthorizedBehaviorType == False ):
            # do it on the fly (not optimal)
            life = altools.myGetProxy( "ALLife" );
            aAuthorizedBehaviorType = life.getAuthorizedBehaviorType();
            
        
        # check language
        if( strCurrentLang == "" ):
            strCurrentLang = altools.getSpeakAbbrev( altools.getSpeakLanguage() );
        if( len( self.aLang ) != 0 and not strCurrentLang in self.aLang ):
            altools.debug( "INF: behaviordata.isLaunchable: behav %s: %s not compatible with language %s" % ( self.strPath, self.aLang, strCurrentLang ) );
            return False;            
#        print( "LANGAGE IS OK: %s in %s (or empty)" % ( strCurrentLang, self.aLang ) );

        if( not self.bEnabled ):
            altools.debug( "INF: behaviordata.isLaunchable: behav %s: desactivated" % ( self.strPath ) );
            return False;
            
        # check note
        if( self.rHappyNote < -2. ):
            altools.debug( "INF: behaviordata.isLaunchable: behav %s: not enough happy note: %f" % ( self.strPath, self.rHappyNote ) );
            return False;
            
        # check type
#        if( bRemoveInteraction and ( self.strBehaviorType == 'init_interaction' or self.strBehaviorType == 'interaction'  ) ):
#            altools.debug( "INF: behav %s: contains interaction => skipped (type is '%s')" % ( self.strPath, self.strBehaviorType ) );
#            return False;
        if( not self.strBehaviorType in aAuthorizedBehaviorType ):
            altools.debug( "INF: behav %s: doesn't have an authorized type => skipped (type '%s' not in '%s')" % ( self.strPath, self.strBehaviorType, str( aAuthorizedBehaviorType ) ) );
            return False;
        
        # check premisses        
        try:
            bRet = eval( self.strStartingCondition );
            return bRet;
        except BaseException, err:
            print( "BehaviorDesc.isLaunchable: ERR: evaluating your behavior starting condition:" );
            print( "BehaviorDesc.isLaunchable: ERR: file: '%s'" % ( self.getPath() ) );
            print( "BehaviorDesc.isLaunchable: ERR: condition: '%s'" % ( self.strStartingCondition ) );
            print( "BehaviorDesc.isLaunchable: ERR: '%s'\n" % str( err ) );
        return False;
    # isLaunchable - end
    
    def last_start( self ):
        "return the time of last start"
#        nTimeSec = int( time.time() - self.lastLaunch_TimeStart );
#        print( "BehaviorDesc.last_start: '%s': %d sec" % ( self.strPath, nTimeSec ) );
#        return nTimeSec;
        return self.lastLaunch_TimeStart;
    # last_start - end

    def last_stop( self ):
        "return the time of last stop"
        return self.lastLaunch_TimeStop;
    # last_stop - end

# BehaviorDesc - end

class BehaviorDescManager:
    "Manage Behavior description: load them, read and update stats, ..."
    "Each behavior is nammed by its folder (bcause now all .xar are named behavior.xar, pfff)"
    def __init__( self ):
        self.listBehaviorDesc = [];
        self.strStatsFileName = altools.getCachePath() + "behavior_stats.dat";
        self.mutex = mutex.mutex();
        self.logMutex = mutex.mutex();
        self.logLastTime = time.time();
        self.aAuthorizedBehaviorType = []; # a cached value too limit call from python => cpp
    # __init__ - end
    
    def getAllBehaviorsDesc(self):
        return self.listBehaviorDesc;
    # getAllBehaviorsDesc - end    
    
    def loadAllBehaviorDesc( self, bForceReload = False ):
        "scan all directories and load every behaviors"
        "bForceReload: force reload of informations, even if previously loaded"
        if( not bForceReload and len( self.listBehaviorDesc ) > 0 ):
            return; # do nothing!
        strBehaviorRootPath = getStandardBehaviorPath() + getBehaviorPath();
        listXarFile = altools.findFile( strBehaviorRootPath, ".xar" );
#        print( "BehaviorDesc.loadAllBehaviorData: %s" % str( listXarFile ) );
        listBehaviorData = [];
        for strTotalPathAndXarFile in listXarFile:
            strPathOfXar = altools.getDirectoryName( strTotalPathAndXarFile );
            newBehav = BehaviorDesc( strPathOfXar, strTotalPathAndXarFile );
            # check doublons
            bDoublons = False;
            for bea in listBehaviorData:
                if( bea.strPath == newBehav.strPath ):
                    print( "BehaviorDescManager.loadAllBehaviorData: '%s' already in base, (some .xar.bak or .xar.~ are perhaps present ?)" % bea.strPath );
                    bDoublons = True;
                    break;
            if( not bDoublons ):
                if( newBehav.load() ):
                    listBehaviorData.append( newBehav );
        print( "BehaviorDescManager.loadAllBehaviorData: %d behavior(s) loaded" % len( listBehaviorData ) );
        self.listBehaviorDesc = listBehaviorData;
        self.readAllStats();
        self.printAll(); # pour debugger
    # loadAllBehaviorDesc - end
    
    def getActiveBehavior( self ):
        "return all active behavior (.xar)"
        return altools.getActiveXarList();
    # getActiveBehavior - end
    
    def findOneBehaviorIndex( self, strFolderName ):
        "find a behavior, return -1 if not found"
        if( not getStandardBehaviorPath() in strFolderName ):
            strFolderName = getStandardBehaviorPath() + strFolderName;        
        nIndex = 0;
        for behav in self.listBehaviorDesc:
#            print( "BehaviorDescManager.readAllStats: comparing '%s' with '%s'" % ( strFolderName, behav.strPath ) );
            if( behav.strPath == strFolderName ):
                return nIndex;
            nIndex += 1;
        return -1;
    # findOneBehaviorIndex - end
    
    def findOneBehavior( self, strFolderName ):
        "find a behavior, return None if not found"
        if( not getStandardBehaviorPath() in strFolderName ):
            strFolderName = getStandardBehaviorPath() + strFolderName;
        for behav in self.listBehaviorDesc:
            if( behav.strPath == strFolderName ):
                return behav;
        return None;
    # findOneBehaviorIndex - end    
    
    def readAllStats( self ):
        "read stats for all behavior and store it in each behavior"
        bufFile = altools.getFileContents( self.strStatsFileName );
        if( bufFile == "" ):
            print( "WRN: BehaviorDescManager.readAllStats: there's no previous stats" );
            return;
        while( self.mutex.testandset() == False ):
            print( "readAllStats: locked" );
            time.sleep( 0.1 );            
        nNumLine = 0;
        bufLine =altools. getLine( bufFile, nNumLine );
        nNbrReaded = 0;
        while bufLine != "":
            fields = bufLine.split( ':' );
            print( "fields: %s" % str( fields ) );
            if( len( fields ) > 0 ):
                strName = fields[0];
                nbrOcc = fields[1];
                strTimeLastStart = fields[2];
                strTimeLastStop = fields[3];
                strAverage = fields[4];
                if( len( fields ) > 5 ):
                    strHappyNote = fields[5];
                else:
                    strHappyNote = "0.0";
                nIndex = self.findOneBehaviorIndex( strName );
                if( nIndex == -1 ):
                    print( "ERR: BehaviorDescManager.readAllStats: behavior '%s' not found in known base" % strName );
                else:
                    self.listBehaviorDesc[nIndex].nNbrLaunched = int( nbrOcc );
                    
                    nTimeLastStart = int( strTimeLastStart );
                    if( nTimeLastStart > time.time() ):
                        print( "WRN: BehaviorDescManager.readAllStats: time has drifted => resetting! (last launch behavior: %d and curent time is anterior: %d)" % ( nTimeLastStart, int( time.time() ) ) );
                        nTimeLastStart = int( time.time() );                        
                    self.listBehaviorDesc[nIndex].lastLaunch_TimeStart = nTimeLastStart;
                    
                    nTimeLastStop = int( strTimeLastStop );
                    if( nTimeLastStop > time.time() ):
                        print( "WRN: BehaviorDescManager.readAllStats: time has drifted => resetting! (last launch behavior: %d and curent time is anterior: %d)" % ( nTimeLastStart, int( time.time() ) ) );
                        nTimeLastStop = int( time.time() );
                    if( nTimeLastStop < nTimeLastStart ):
                        print( "WRN: BehaviorDescManager.readAllStats: stop is anterior to start => changint it ! (start: %d, stop: %d)" % ( nTimeLastStart , nTimeLastStop ) );
                        nTimeLastStop = nTimeLastStart + 1; # +1 pour le plaisir !
                    self.listBehaviorDesc[nIndex].lastLaunch_TimeStop = nTimeLastStop;
                    
                    rAverage = float( strAverage );
                    self.listBehaviorDesc[nIndex].rAverage_Duration = rAverage;
                    
                    rHappyNote = float( strHappyNote );
                    self.listBehaviorDesc[nIndex].rHappyNote = rHappyNote;                    
                    
                                        
                    nNbrReaded += 1;
            nNumLine += 1;
            bufLine = altools.getLine( bufFile, nNumLine );
        # while - end
        self.mutex.unlock();
        print( "BehaviorDescManager.readAllStats: %d stat(s) readed\n" % nNbrReaded );
    # readAllStats - end
    
    def updateStats_start( self, strBehaviorName ):
        "Update statistics about behaviors starts"
        altools.debug( "updateStats_start( '%s' ): %f" % ( strBehaviorName, time.time() ) );
        while( self.mutex.testandset() == False ):
            print( "updateStats_start(%s): locked" % strBehaviorName );
            time.sleep( 0.1 );
        nIndex = self.findOneBehaviorIndex( strBehaviorName );
        if( nIndex == -1 ):
            print( "ERR: BehaviorDescManager.updateStats_start: behavior '%s' not found in known base" % strBehaviorName );
            self.mutex.unlock();            
            return;
        extractedData.updateValue( 'any_behaviors_last_start', int( time.time() ) ); # update this value
        if( self.listBehaviorDesc[nIndex].bStarted ):
            print( "WRN: BehaviorDescManager.updateStats_start: this behavior has already been started or hasn't been stopped" );
        self.listBehaviorDesc[nIndex].nNbrLaunched = self.listBehaviorDesc[nIndex].nNbrLaunched + 1;
        self.listBehaviorDesc[nIndex].lastLaunch_TimeStart = int( time.time() );
        self.listBehaviorDesc[nIndex].bStarted = True;
        self.mutex.unlock();
         # method below has inner mutex
        self.sortByInterest();
        self.saveAllStats();
        self.log( "%s: start" % strBehaviorName );
    # updateStats_start - end
    
    def updateStats_stop( self, strBehaviorName ):
        "Update statistics about behaviors: time of stoping"
        altools.debug( "updateStats_stop( '%s' ): %f" % ( strBehaviorName, time.time() ) );
        while( self.mutex.testandset() == False ):
            print( "updateStats_stop(%s): locked" % strBehaviorName );
            time.sleep( 0.1 );
        nIndex = self.findOneBehaviorIndex( strBehaviorName );
        if( nIndex == -1 ):
            print( "ERR: BehaviorDescManager.updateStats_stop: behavior '%s' not found in known base" % strBehaviorName );
            self.mutex.unlock();
            return;            
        extractedData.updateValue( 'any_behaviors_last_stop', int( time.time() ) ); # update this value
        if( not self.listBehaviorDesc[nIndex].bStarted ):
            print( "WRN: BehaviorDescManager.updateStats_stop: this behavior has already been stopped or never been started" );
            self.mutex.unlock();
            return;
        self.listBehaviorDesc[nIndex].lastLaunch_TimeStop = int( time.time() );
        nThisDuration = self.listBehaviorDesc[nIndex].lastLaunch_TimeStop - self.listBehaviorDesc[nIndex].lastLaunch_TimeStart;
        altools.debug( "updateStats_stop: nThisDuration: %d" % nThisDuration );
        if( nThisDuration < 0 ):
            print( "WRN: BehaviorDescManager.updateStats_stop: stop time is anterior to start time => don't know what to do... (start: %d; stop: %d)" % ( self.listBehaviorDesc[nIndex].lastLaunch_TimeStart, self.listBehaviorDesc[nIndex].lastLaunch_TimeStop ) );
            nThisDuration = 0;
        self.listBehaviorDesc[nIndex].rAverage_Duration = ( ( self.listBehaviorDesc[nIndex].rAverage_Duration * ( self.listBehaviorDesc[nIndex].nNbrLaunched - 1 ) ) + nThisDuration )  / float( self.listBehaviorDesc[nIndex].nNbrLaunched );
        self.listBehaviorDesc[nIndex].bStarted = False;        
        self.mutex.unlock();
        self.sortByInterest();
        self.saveAllStats();
        self.log( "%s: stop" % strBehaviorName );
    # updateStats_stop - end

    def updateStats_user_taste( self, strBehaviorName,  rTaste = 1. ):
        "Update statistics about a mood of user"
        "rTaste: 1: good, -1: bad"
        altools.debug( "updateStats_user_taste( '%s', %f ): %f" % ( strBehaviorName, rTaste, time.time() ) );
        while( self.mutex.testandset() == False ):
            print( "updateStats_user_taste(%s): locked" % strBehaviorName );
            time.sleep( 0.1 );
        nIndex = self.findOneBehaviorIndex( strBehaviorName );
        if( nIndex == -1 ):
            print( "ERR: BehaviorDescManager.updateStats_stop: behavior '%s' not found in known base" % strBehaviorName );
            self.mutex.unlock();            
            return;            
        self.listBehaviorDesc[nIndex].rHappyNote += rTaste * 0.2;
        self.mutex.unlock();
        self.saveAllStats();
        self.log( "%s: user_taste: %f" % ( strBehaviorName, rTaste ) );
    # updateStats_user_taste - end
    
    def saveAllStats( self ):
        "save all stats"
        while( self.mutex.testandset() == False ):
            print( "saveAllStats: locked" );
            time.sleep( 0.1 );                    
        bufFile = "";
        for behav in self.listBehaviorDesc:
            bufFile += "%s: %d: %s: %s: %f: %f\n" % ( behav.strPath, behav.nNbrLaunched, str( behav.lastLaunch_TimeStart ), str( behav.lastLaunch_TimeStop ),  behav.rAverage_Duration, behav.rHappyNote );
        # for - end
        try:
            file = open( self.strStatsFileName, "wt" );
            file.write( bufFile );
        finally:
            file.close();
        self.mutex.unlock();
        altools.debug( "BehaviorDescManager.saveAllStats: %d stat(s) saved" % len( self.listBehaviorDesc ) );
    # saveAllStats - end
    
    def printAll( self ):
        "Print all info about active behavior"
        print( "BehaviorDescManager.printAll at %d - humantime: %s" % ( int( time.time() ), altools.getHumanTimeStamp() ) );
        for behav in self.listBehaviorDesc:
            print( behav.toString() );
        # for - end
    # printAll - end
    
    def findLessLaunched( self ):
        "return the list of behavior with the less launched times"
        "not used: it's better to sortBy...() after each update"
        nTimesMin = -1;
        listBehav = [];
        for behav in self.listBehaviorDesc:
            if( behav.nNbrLaunched < nTimesMin ):
                nTimesMin = behav.nNbrLaunched;
                listBehav = [];
            if( behav.nNbrLaunched == nTimesMin ):
                listBehav.append( behav );
        return listBehav;
    # findLessLaunched - end
    
    def sortByInterest( self ):
        "sort all behaviors from the less launched to the most launched (interesting to have novelty, but we allways test all premisses to get to the frequent ones"
        while( self.mutex.testandset() == False ):
            print( "sortByInterest: locked" );
            time.sleep( 0.1 );    
#        print( "sortByInterest: begin" );
#        self.printAll();
        orig = self.listBehaviorDesc;
        self.listBehaviorDesc = [];
        while len( orig ) > 0:
            nIdxMin = 0;
            for i in range( 1, len( orig ) ):
                # critere: les plus apprécié en premier et sépare les ex-aequo en sortant en priorité les moins lancé
                if( 
                         orig[i].rHappyNote > orig[nIdxMin].rHappyNote 
                    or ( orig[i].rHappyNote == orig[nIdxMin].rHappyNote and orig[i].nNbrLaunched < orig[nIdxMin].nNbrLaunched )
                ): 
                    nIdxMin = i;
            # for - end
            # nIdxMin is the now the index of the prior behavior
#            print( "nIdxMin: %d, nMin: %d" % ( nIdxMin, nMin ) );
            self.listBehaviorDesc.append( orig[nIdxMin] );
            del orig[nIdxMin];
        # while - end
#        print( "sortByInterest: after" );
#        self.printAll();
        self.mutex.unlock();
    # sortByInterest - end
        
    def preProcessBeforeEvaluatingLaunchability( self ):
        "update some variables before evaluating every behaviors launchability(quick/immediate variable)"
      
        timeBegin = time.time();
        # post some information changing every time - for beautifullity in the rules - meta information / are computed in the choregraphe box project
        extractedData.updateValue( "hour", int( time.strftime( "%H", time.localtime() ) ) );
        extractedData.updateValue( "minute", int( time.strftime( "%M", time.localtime() ) ) );
        info = altools.myGetProxy( "ALInfo" );
        extractedData.updateValue( "duration_sitting", info.getDuration_Sitting() );
        extractedData.updateValue( "duration_standing", info.getDuration_Standing() );
        extractedData.updateValue( "cpu_temperature", int( altools.getHeadTemperature() ) );
        
        # because of the new UsageData in python, we have to export some variables from ALMemory to UsageDataManager
        mem = altools.myGetProxy( "ALMemory" );        
        # info
        try:
            extractedData.updateValue( "body_position", info.getBodyPosition() );
            extractedData.updateValue( "walking", mem.getData( "extracted_data/walking" ) );
            #extractedData.updateValue( "walking_activity", mem.getData( "extracted_data/walking_activity" ) );
            extractedData.updateValue( "walking_activity", info.getWalkingActivity() );
            extractedData.updateValue( "body_temperature", mem.getData( "extracted_data/body_temperature" ) );
            extractedData.updateValue( "boredom", mem.getData( "extracted_data/boredom" ) );
            extractedData.updateValue( "battery_level", mem.getData( "ALSentinel/BatteryLevel" ) );
            extractedData.updateValue( "max_consumption", info.getElectricConsumptionMax() );
            extractedData.updateValue( "camera_medium_average_moving", mem.getData( "extracted_data/camera_medium_average_moving" ) );
            extractedData.updateValue( "is_charging", mem.getData( "extracted_data/is_charging" ) );
            extractedData.updateValue( "is_charging_last_false", mem.getData( "extracted_data/is_charging_last_false" ) );            
        except BaseException, err:
            print( "WRN: preProcessBeforeEvaluatingLaunchability: some variables were never posted before (module info) (err:%s)" % str( err ) );
            pass
        
        # life
        try:        
            extractedData.updateValue( "life_area", mem.getData( "extracted_data/life_area" ) );
        except BaseException, err:
            print( "WRN: preProcessBeforeEvaluatingLaunchability: some variables were never posted before (module life) (err:%s)" % str( err ) );
            pass
        
        # vision
        try:
            # pour limiter les try catch, on les met dans l'ordre "d'oftenité"
            extractedData.updateValue( "camera_luminosity", mem.getData( "extracted_data/camera_luminosity" ) );
            extractedData.updateValue( "camera_average_color", mem.getData( "extracted_data/camera_average_color" ) );
            extractedData.updateValue( "camera_darkness", mem.getData( "extracted_data/camera_darkness" ) );
            extractedData.updateValue( "camera_darkness_last_false", mem.getData( "extracted_data/camera_darkness_last_false" ) ); # on poste ca car sinon l'event est trop court pour l'avoir ! (beurk!!!)
            extractedData.updateValue( "camera_darkness_last_true", mem.getData( "extracted_data/camera_darkness_last_true" ) );
            extractedData.updateValue( "camera_lightness", mem.getData( "extracted_data/camera_lightness" ) );            
        except BaseException, err:
#            altools.debug( "INF: preProcessBeforeEvaluatingLaunchability: some variables were never posted before (module vision) (err:%s)" % str( err ) );
            pass
    
#        print( "INF: preProcessBeforeEvaluatingLaunchability: preprocess time: %s" % str( ( time.time() - timeBegin ) ) );
        life = altools.myGetProxy( "ALLife" );
        self.aAuthorizedBehaviorType = life.getAuthorizedBehaviorType();
    # preProcessBeforeEvaluatingLaunchability - end
    
    def getAllPossibleBehavior( self ):
        "compute all possible behavior at this moment"
        "return a list of pair [pathxarname, is_system]"
        timeBegin = time.time();        
        self.preProcessBeforeEvaluatingLaunchability();
        listPossible = [];
        strCurrentLang = altools.getSpeakAbbrev( altools.getSpeakLanguage() );
        for behav in self.listBehaviorDesc:
            if( behav.isLaunchable( aAuthorizedBehaviorType = self.aAuthorizedBehaviorType, strCurrentLang = strCurrentLang  ) ):
#                self.log( "this behavior is launchable so we append it to possible:\n" + behav.toString() );
                listPossible.append( [ behav.getPathXarName(), behav.isSystem()] );        
                
#        print( "BehaviorDescManager.getAllPossibleBehavior: time of evaluation: %fs" % ( time.time() - timeBegin ) );
        return listPossible;
    # getAllPossibleBehavior - end

    def log( self, strMessage ):
        timeNow = time.time();
        rDurationSec = timeNow - self.logLastTime;
        self.logLastTime = timeNow;
        while( self.logMutex.testandset() == False ):
            print( "log(%s): locked" % strMessage );
            time.sleep( 0.02 );
        
        strFilename = altools.getCachePath() + "BehaviorDescManager.log";
        file = open( strFilename, "at" );
        file.write( "%s (%5.2fs): %s\n" % ( altools.getHumanTimeStamp(), rDurationSec, strMessage ) );
        file.close();
        self.logMutex.unlock();
    # log - end

    def logIsLoaded( self, strBehaviorName):
        self.log( "%s: loaded" % strBehaviorName );
    # logIsLoaded - end
    
    def logFall( self, strBehaviorName ):
        self.log( "%s: fall" % strBehaviorName );
    # logFall - end
        
    def logTimeoutLoad( self, strBehaviorName ):
        self.log( "%s: timeout while loading" % strBehaviorName );
    # logTimeoutLoad - end
    
    def logTimeoutExecute( self, strBehaviorName):
        self.log( "%s: timeout while executing" % strBehaviorName );
    # logTimeoutExecute - end

    def logTimeoutNoMove( self, strBehaviorName):
        self.log( "%s: timeout no move" % strBehaviorName );
    # logTimeoutExecute - end
    
    
    def updateInfo( self ):
        "update info from various locations to the naoqi world and reciprocally"
        self.preProcessBeforeEvaluatingLaunchability();
        
        # update to ALMemory some info from python world
        try:
            mem = altools.myGetProxy( "ALMemory" );
            mem.raiseMicroEvent( ExtractedData.getStmRootName() + "excitement", extractedData.getValue( "excitement" ) );
        except BaseException, err:
            print( "WNG: BehaviorDescManager.updateInfo: ? (err:%s)" % ( err ) );        
        
            
        
    # updateInfo - end
    
# BehaviorDescManager - end

behaviorDescManager = BehaviorDescManager();

class WayMap:
    "store the travel of Nao on a 2D map"
    "we activate all by default, but desactivate what takes times (eg: output to image)"
    def __init__(self):
        timer = altools.TimeMethod();
        self.rPrecision = 10.; # if 100, each point is a cm, if 1000, each point is a mm, if 10, each point is a dm, if 40, each point is 2.5cm
        self.nSizeX = 400; # nbr of position in our tabs - in cm if self.nPrecision is 100
        self.nSizeY = self.nSizeX;
        self.aMap = array.array( 'B', [0]*self.nSizeX*self.nSizeY );        
        # les lignes suivantes prennent 7.3sec sur le robot, avec l'init de la ligne précédente => 1.4sec
        #~ for y in range( self.nSizeY ):
            #~ for x in range( self.nSizeX ):
                #~ self.aMap.append( 0 );
        self.motion = altools.myGetProxy( "ALMotion" );                
        if( self.motion == None ):
            print( "ERR: WayMap: ALMotion is required!" );
            return;
        aRobotPos = self.motion.getRobotPosition( False );
        self.rPosXAtStartup = aRobotPos[0] - self.nSizeX / (2*self.rPrecision); # offset in meters
        self.rPosYAtStartup = aRobotPos[1] - self.nSizeY / (2*self.rPrecision);
        print( "WayMap: begin offset: %f, %f" % ( self.rPosXAtStartup, self.rPosYAtStartup ) );
        self.loadFromDisk();
        self.objectif = None; # objectif stored in matrix coordinate (ie in map)
    # __init__ - end
    
    def __del__( self ):
#        timer = altools.TimeMethod(); # ici souvent altools a deja disparu..
        self.saveToDisk();
#        print( self.toString() );
#        self.drawToImage();
    # __del__ - end
    
    def loadFromDisk( self ):
        #~ try:
            #~ file = open( "/home/nao/waymap.dat", "rb" );
            #~ aBuf = file.read();
            #~ file.close();
        #~ except:
            #~ print( "%s.loadFromDisk: no waymap found" % self.getName() );
            #~ return;
    
        #~ nMaxPoint = 0;
        #~ for y in range( self.nSizeY ):
            #~ for x in range( self.nSizeX ):
                #~ nVal = struct.unpack_from( "l", aBuf, ( x+y*self.nSizeX ) * struct.calcsize("l") )[0];
#~ #                print( "loadFromDisk: (%d,%d): %d" % ( x, y, nVal ) );
                #~ if( nVal > nMaxPoint ):
                    #~ nMaxPoint = nVal;
                #~ self.aMap[x+y*self.nSizeX] = nVal;
        #~ print( "%s.loadFromDisk: nMaxPoint: %d" % ( self.boxName, nMaxPoint ) );
        
        try:
            file = open( altools.getCachePath() + "waymap.dat", "rb" );        
            self.aMap.fromfile( file, self.nSizeX * self.nSizeY );
            file.close();
        except BaseException, err:
            print( "INF: WayMap.loadFromDisk: no waymap found ? (err:%s)" % ( err ) );        
            self.aMap = array.array( 'B' ); # reset it
            for y in range( self.nSizeY ):
                for x in range( self.nSizeX ):
                    self.aMap.append( 0 );            
            return;
    # loadFromDisk - end
    
    def saveToDisk( self ):
        try:
            timer = altools.TimeMethod();    
        except:
            pass
        print( "WayMap.saveToDisk: begining..." );
        # la méthode suivante prend 4.5 secondes pour du 400x400
        #~ file = open( "/home/nao/waymap.dat", "wb" );
        #~ aBufOut = "";
        #~ nMaxPoint = 0;        
        #~ for y in range( self.nSizeY ):
            #~ for x in range( self.nSizeX ):
                #~ nVal = self.aMap[x+y*self.nSizeX];
#~ #                print( "saveToDisk: (%d,%d): %d" % ( x, y, nVal ) );                
                #~ strSample = struct.pack( "l", nVal );
                #~ aBufOut += strSample;
                #~ if( nVal > nMaxPoint ):
                    #~ nMaxPoint = nVal;                
        #~ file.write( aBufOut );
        #~ file.close();
        # cette méthode prend 0.03 secondes pour du 400x400
        file = open( altools.getCachePath() + "waymap.dat", "wb" );
        self.aMap.tofile( file );
        file.close();
        print( "WayMap.saveToDisk: end" );
    # saveToDisk - end
    
    def getCurrentRobotPositionInMapCoord( self ):
        "return the x,y in the map (and the angular of body position)"
#        aRobotPos = ALMotion.getRobotPosition( True );
#        self.log( "aRobotPosSensors: %s" % str( aRobotPos ) );            
        aRobotPos = self.motion.getRobotPosition( False );
        #~ print( "aRobotPos: %s" % str( aRobotPos ) );
        xcm = int( ( aRobotPos[0] - self.rPosXAtStartup ) * self.rPrecision );
        ycm = int( ( aRobotPos[1] - self.rPosYAtStartup ) * self.rPrecision );
#        self.log( "xcm: %d, ycm: %d" % ( xcm, ycm ) );
        if( xcm < 0 ):
            xcm = 0;
        if( xcm >= self.nSizeX ):
            xcm = self.nSizeX - 1;
        if( ycm < 0 ):
            ycm = 0;
        if( ycm >= self.nSizeY ):
            ycm = self.nSizeY - 1;
        return [xcm, ycm, aRobotPos[2] ];
    # getCurrentRobotPositionInMapCoord - end
    
    def updateRobotPosition( self ):
        xmap, ymap, rAngle = self.getCurrentRobotPositionInMapCoord();
        #~ print( "WayMap.updateRobotPosition: updating %d, %d (current value is %d)" % ( xmap, ymap, self.aMap[xmap+ymap*self.nSizeX] ) );
        if( self.aMap[xmap+ymap*self.nSizeX] < 255 ):
            self.aMap[xmap+ymap*self.nSizeX] += 1;
    # updateRobotPosition - end
    
    def setTarget( self, x_meters, y_meters = 0 ):
        "set target for the robot (in meters), described in current body position (straight far away is x>0, left if y>0"
        xmap, ymap, rAngle = self.getCurrentRobotPositionInMapCoord();
        #~ rAngle = 1.57;
        # rotating projection of target
        x_map_target = x_meters * math.cos( rAngle ) + y_meters * math.sin( rAngle );
        y_map_target = x_meters * math.sin( rAngle ) + y_meters * math.cos( rAngle );
        print( "x_map: %f, y_map: %f" % ( x_map_target, y_map_target ) );

        # discretisation
        x_map_target = int( x_map_target * self.rPrecision );
        y_map_target = int( y_map_target * self.rPrecision );
        print( "x_map: %f, y_map: %f" % ( x_map_target, y_map_target ) );
        
        # adding offset from current position
        x_map_target += xmap;
        y_map_target += ymap;
        print( "x_map: %f, y_map: %f" % ( x_map_target, y_map_target ) );
        
        self.objectif = [ x_map_target, y_map_target ];
        print( "WayMap.setTarget: relative (%f, %f) => absolute (%f, %f) (center is at %d, %d)" % (x_meters, y_meters, x_map_target, y_map_target, self.rPosXAtStartup, self.rPosYAtStartup ) );
    # setTarget - end
    
    def resetTarget( self ):
        "remove current target"
        self.objectif = None;
    
    def getTarget( self ):
        "return target in meters relatively to nao body position"
        if( self.objectif == None ):
            return [0.,0.];
        xmap, ymap, rAngle = self.getCurrentRobotPositionInMapCoord();
        #~ rAngle = 1.57;
        x_map_target, y_map_target = self.objectif;
        print( "x_map_target: %f, y_map_target: %f" % ( x_map_target, y_map_target ) );
        print( "x_map: %f, y_map: %f" % ( xmap, ymap ) );        
        x_map_target = float( x_map_target - xmap ) / self.rPrecision;
        y_map_target = float( y_map_target - ymap ) / self.rPrecision;
        
        print( "x_map_target: %f, y_map_target: %f" % ( x_map_target, y_map_target ) );
        
        xm = +x_map_target * math.cos( rAngle ) - y_map_target * math.sin( rAngle );
        ym = -x_map_target * math.sin( rAngle ) + y_map_target * math.cos( rAngle );
        
        return [xm, ym];
    # setTarget - end
    
    def toString( self ):
        # sortie en mode texte, pffff
        timer = altools.TimeMethod();
        #~ sys.stdout.write( "WayMap: \n" );       
        #~ for y in range( self.nSizeY ):
            #~ for x in range( self.nSizeX ):
                #~ nVal = self.aMap[x+y*self.nSizeX];
                #~ if( nVal > 20 ):
                    #~ sys.stdout.write( "X" ); # like print but without the space between each chars
                #~ elif( nVal > 10 ):
                    #~ sys.stdout.write( "x" );
                #~ elif( nVal > 0 ):
                    #~ sys.stdout.write( "-" );
                #~ else:
                    #~ sys.stdout.write( "." );
            #~ sys.stdout.write( "\n" );

        strOut = "";
        for y in range( self.nSizeY ):
            for x in range( self.nSizeX ):
                nVal = self.aMap[x+y*self.nSizeX];
                if( nVal > 20 ):
                    strOut += "X";
                elif( nVal > 10 ):
                    strOut += "x";
                elif( nVal > 0 ):
                    strOut += "-";
                else:
                    strOut += ".";
            strOut += "\n";
        return strOut;
    # toString - end
    
    def drawToImage( self ):
        # If you want to get access to each byte ...
        # Include the PIL image package
        timer = altools.TimeMethod();
        print( "WayMap.drawToImage: begining..." );
        imageWidth = self.nSizeX;
        imageHeight = self.nSizeY;        
        im = Image.new("RGB", (imageWidth, imageHeight), (0,255,0)); # image is filled in green
        timer.setIntermediate( "draw" );
        draw = ImageDraw.Draw(im)
        timer.setIntermediate( "fill pixel" );        
        # is there any other faster method to copy an image ?
        nMax = 0;
        nInterestingPoint = 0;

        # find max, so that, we will "zoom color" for colorise.
        nMaxPoint = 0;
        for y in range(0, imageHeight):
            for x in range(0, imageWidth):
                nValue = self.aMap[x+y*self.nSizeX]; # 400x400: 2sec
                if( nValue > nMaxPoint ):
                    nMaxPoint = nValue;
        nMaxPoint = altools.limitRange( nMaxPoint, 5, 255 );
                
        for y in range(0, imageHeight):
            for x in range(0, imageWidth):
                nValue = self.aMap[x+y*self.nSizeX]; # 400x400: 2sec
                if( nValue > 0 ):
                    nInterestingPoint += 1;
                    #~ nColor = altools.valueToPseudoColor( nValue, 480 ); # 480 => full = . # 240 secondes = 4 min to save (pour du 800x800)
                    #~ b,g,r = altools.colorHexaToComp( nColor ); # TODO: dommage de refaire un colorHexaToComp ici !
                    b, g, r = altools.valueToPseudoColor255( nValue, nMaxPoint ); # deux lignes en une => 400x400: 33s (au lieu de 66)
                    if( self.objectif != None and self.objectif[0] == x and self.objectif[1] == y ):
                        r,g,b = [0, 0, 0]; # objectif is black
                    draw.point( (x, y), (r,g,b) ); # 400x400: 18sec
                    if( nValue > nMax ):
                        nMax = nValue;
    #                self.log( "%d => %x\n" % ( self.aMap[x+y*self.nSizeX], nColor ) );

        # 288 secondes pour la partie draw!
        # 0.9 secondes pour la partie save!
        timer.setIntermediate( "saving" );
        strFilename = altools.getCachePath() + 'waymap_' + altools.getFilenameFromTime() + '.png';
        im.save( strFilename, "PNG" );    
        print( "WayMap.drawToImage: image outputted to %s (interest: %d, max passage:%d)" % ( strFilename, nInterestingPoint, nMax ) );
    # drawToImage - end
    
# WayMap - end
        
wayMap = WayMap();


#~ for i in range( 100 ):
    #~ wayMap.updateRobotPosition();
#~ motion = altools.myGetProxy( "ALMotion" );
#~ wayMap.setTarget( 0.5, 0.1 );
#~ target = wayMap.getTarget();
#~ print( "target: %s\n" % str( target ) );

#~ motion.setStiffnesses( "Body", 1.0, 1.0 );
#~ #motion.walkTo( 0.0, 0.0, 1.57 );
#~ motion.walkTo( 1.0, 0.0, 0.0 );
#~ motion.waitUntilWalkIsFinished();

#~ target = wayMap.getTarget();
#~ print( "target after rot: " + str( target ) );
#~ motion.walkTo( target[0], target[1], 0.0 );
#~ motion.waitUntilWalkIsFinished();

#~ print( "new target, must be the same!\n" );
#~ wayMap.setTarget( 0.25, 1.0 );
#~ wayMap.drawToImage();

    

def updateBodyPosition():
    #get value Torso Angle Y & X from Memory to check if the robot is on the belly or on the back DEPRECATED; use Autonomous/ALInfo
    strVarName = "body_position";
    mem = altools.myGetProxy( "ALMemory" );
    motion = altools.myGetProxy( "ALMotion" );
    rAngleX, rAngleY = mem.getListData( [ "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value", "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value" ] );
    
#    altools.debug( "DetectPosition: rAngleX: %5.3f; rAngleY: %5.3f" % (rAngleX, rAngleY ) );

    rTemp1, rTemp2 = motion.getAngles( ['LHipPitch', 'RHipPitch' ], True );
    rJointValHipPitch = ( rTemp1 + rTemp2 ) / 2.;
    rTemp1, rTemp2 = motion.getAngles( ['LKneePitch', 'RKneePitch' ], True );
    rJointValKneePitch = ( rTemp1 + rTemp2 ) / 2.;
    rTemp1, rTemp2 = motion.getAngles( ['LAnklePitch', 'RAnklePitch' ], True );
    rJointValAnklePitch = ( rTemp1 + rTemp2 ) / 2.;
    
    if( rJointValHipPitch > -0.9 and rJointValKneePitch > 1.2 and rJointValAnklePitch > 0.3 and rAngleY < 1.2 ):
#        altools.debug( "output_kneeling" );
        extractedData.updateValue( strVarName, "kneeling" );
        return;

    if  rAngleY > -0.82 and rAngleY < 0.9 and abs(rAngleX) < 0.5:
#        altools.debug( "the torso is vertical" );
        
        rJointValHipRoll, rJointValLHipYawPitch = motion.getAngles( ['LHipRoll', 'LHipYawPitch' ], True );

#        altools.debug( "DetectPosition: HipPitch: %5.3f; KneePitch: %5.3f; AnklePitch: %5.3f; LHipRoll: %5.3f; LHipYawPitch: %5.3f" % (rJointValHipPitch, rJointValKneePitch, rJointValAnklePitch, rJointValHipRoll, rJointValLHipYawPitch ) );
        if( rJointValHipPitch < -0.45 and rJointValKneePitch > 1.8 and rJointValAnklePitch < -0.7 ):
#            altools.debug( "output_crouch" );
            extractedData.updateValue( strVarName, "crouching" );
        elif(  rJointValHipPitch < -1.2 or ( rJointValHipPitch < -0.8 and rJointValKneePitch < 0.5 ) ):
#            altools.debug( "output_sit" );
            extractedData.updateValue( strVarName, "sitting" );
        # Alma: avant le hip pitch etat a 0.3 mais pourquoi pas 0.5 ? idem pour rJointValHipRoll (pour position avec une jambe sur le coté)
        # Alma: modif ankle 0.1 => 0.54 pour quand Nao fait caca debout (fesses en arrieres)
        elif( rJointValHipPitch < 0.5 and rJointValKneePitch < 1.1 and rJointValAnklePitch < 0.54 and rJointValHipRoll < 0.5 ):
#            altools.debug( "output_standing" );
            extractedData.updateValue( strVarName, "standing" );
        elif( rJointValHipPitch < -1.2 and rJointValKneePitch > 1.1 ):
            # predefined position: "intermediary" => stand, sit or lying (already done in the horizontal case)
            if( rAngleY > -0.7 and rAngleY < 0.1 ):
#                altools.debug( "output_sit2" );
                extractedData.updateValue( strVarName, "sitting" );
            elif( rAngleY > 0.4 ):
#                altools.debug( "output_standing2" );
                extractedData.updateValue( strVarName, "standing" );
            else:
#                altools.debug( "output_unknown1" );
                extractedData.updateValue( strVarName, "unknown" );
        else:
#            altools.debug( "output_unknown2" );
            extractedData.updateValue( strVarName, "unknown" );
    else:
#        altools.debug( "the torso is horizontal" );
#        altools.debug( "DetectPosition: HipPitch: %5.3f; KneePitch: %5.3f" % (rJointValHipPitch, rJointValKneePitch ) );
        rAngleX_Side = 1.3;
        rErrorMax = 0.3;
        if( rAngleY > 1.0 ):
#            altools.debug( "output_belly" );
            extractedData.updateValue( strVarName, "lying" );
        elif( rAngleY < -0.85 ):
#            altools.debug( "output_back" );
            extractedData.updateValue( strVarName, "lying" );
        elif( rAngleY > -0.6 and rAngleY < 0.6 and 
            (
                    ( rAngleX > rAngleX_Side-rErrorMax  and rAngleX < rAngleX_Side+rErrorMax)
                or ( rAngleX < -(rAngleX_Side-rErrorMax)   and rAngleX > -(rAngleX_Side+rErrorMax ) )
                )
        ):
            # on the right side = (0.0, 1.35), on the left side:  (0.0, -1.30)
            if( rAngleX > 0 ):
#                altools.debug( "output_side_right" );
                extractedData.updateValue( strVarName, "lying" );
            else:
#                altools.debug( "output_side_left" );
                extractedData.updateValue( strVarName, "lying" );
        else:
#            altools.debug( "output_unknown3" );
            extractedData.updateValue( strVarName, "unknown" );
# updateBodyPosition - end
    

def branchOnNaoPosition():
    "return 0 if nao is standing, 1 if nao is sitting, 2 if unknown or extractor not launched"
    strCurrentPos = extractedData.getValue( "body_position" );
    nRet = 2;
    if( strCurrentPos == "standing" or strCurrentPos == "crouching" ):
        nRet = 0;
    elif( strCurrentPos == "sitting" ):
        nRet = 1;
    else:
        print( "altools.branchOnNaoPosition: triggered, but position is not managed: '%s'" % ( strCurrentPos ) );
    return nRet;
# branchOnNaoPosition - end

def isExcited():
    "return true if excited > 0.5"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement > 0.5 ):
        return True;
    return False;
# isExcited - end

def isNearlyExcited():
    "return true if excited > 0.35"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement > 0.30 or rExcitement == extractedData.getUnknownValue() ):
        return True;
    return False;
# isNearlyExcited - end

def isSleepy():
    "return true if ambiance is to sleep"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement < 0.15 ):
        return True;
    return False;
# isSleepy - end

def getSleepingValue():
    return 0.07;
# getSleepingValue - end

def isSleeping():
    "return true if nao is sleeping => stop moving"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement < getSleepingValue() ):
        return True;
    return False;
# isSleeping - end

def isDeepSleeping():
    "return true if nao is deep sleeping => even lightoff leds"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement < 0.03 ):
        return True;
    return False;
# isDeepSleeping - end

def playSoundSometimes( strFilename, bWait = True, bNaoqiSound = False ):
    "dependings of ambiant sounds and life, play sounds, or not"
    "return true if sound is launched"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement == extractedData.getUnknownValue() or isNearlyExcited() ):
        # no autonomous => allways plays
        # excited => play
        altools.playSound( strFilename, bWait, bNaoqiSound, bDirectPlay = True );
        return True;
    return False;
# isExcited - end

def saySometimes( strText ):
    "dependings of ambiant sounds and life, speak, or not"
    "return true if sound is launched"
    rExcitement = extractedData.getValue( "excitement" );
    if( rExcitement == extractedData.getUnknownValue() or isNearlyExcited() ):
        # no autonomous => allways plays
        # excited => play
        altools.sayAndCacheAndLight( strText );
        return True;
    return False;
# isExcited - end

def expressYouhou( bForceSoundEvenIfSleepy = False ):
    if( isNearlyExcited() or bForceSoundEvenIfSleepy ):
        if( random.random() > 0.35 or bForceSoundEvenIfSleepy ):
            nNumSound = random.randint( 1, 8 );
            altools.playSound( 'youhou%d.wav' % nNumSound, bDirectPlay = True );
#    if( random.random() > 0.6 ):
    if( False ):
        # ouvre-ferme les mains
        motion = altools.myGetProxy( "ALMotion" );    
        aJointName = ["RHand", "LHand"];
        aPos = [2.,2.];
        motion.post.angleInterpolationWithSpeed( aJointName, aPos, 1. );
        aPos = [0.,0.];
        motion.post.angleInterpolationWithSpeed( aJointName, aPos, 0.35 );
# expressYouhou - end

def expressHey():
    if( not isSleepy() ):
        nNumSound = random.randint( 1, 19 );
        altools.playSound( 'hey%d.wav' % nNumSound, bDirectPlay = True );
# expressHey - end

def expressAngry():
    if( not isSleepy() ):
        nNumSound = random.randint( 1, 8 );
        altools.playSound( 'angry%d.wav' % nNumSound, bDirectPlay = True );
# expressAngry - end

def testThings():
    testBehavior = BehaviorDesc( "./" );
    testBehavior.load();
    print( "testBehavior:\n" + testBehavior.toString() );
    print( "testBehavior.isLaunchable: '%s'" % str( testBehavior.isLaunchable() ) );
# testThings - end

def freezeLife():
    altools.myGetProxy( "ALLife" );
# freezeLife - end

#
# Wait anim and stuff
#

def getStandardBehaviorPath():
    "return the path containing standard behavior"
    return "/home/nao/behaviors/";
# getStandardBehaviorPath - end

def isAutonomousStyleDefault():
    "are we in 'debase' life"
    life = altools.myGetProxy( "ALLife" );
    style = life.getStyle();
    return style == 'default' or style == '' or style == 'life2';
# isAutonomousStyleDefault - end

def isAutonomousStyleDemo():
    "are we in shanghai or saloon style"
    life = altools.myGetProxy( "ALLife" );
    style = life.getStyle();
    return style == 'shanghai' or style == 'party';
# isAutonomousStyleDefault - end

    
def getAutonomousPathFromStyle():
    life = altools.myGetProxy( "ALLife" );
    style = life.getStyle();
    strPath = '../Applications/autonomous/'
    if( style == "default" or style == ''):
        return strPath;
    return strPath + style + '/';
# getAutonomousPathFromStyle - end
    
def getWaitAnimationPath():
    "return the path containing all wait animation"
    return getAutonomousPathFromStyle() + 'wait_anim/';
# getWaitAnimationPath - end

def getBehaviorPath():
    "return the path containing all behaviors"
    return getAutonomousPathFromStyle() + 'behaviors/';
# getBehaviorPath - end

def getReactionBehaviorName( strName ):
    return getAutonomousPathFromStyle() + 'reactions/' + strName;
# getReactionBehaviorName - end

def getBehaviorsLookupPath():
    "pour rétro-compatibilité"
    #~ try:
        #~ bm = altools.myGetProxy( "ALBehaviorManager" );
        #~ return bm.getBehaviorsLookupPath();
    #~ except BaseException, err:
        #~ print( "WRN: behaviordata: getBehaviorsLookupPath seems deprecated, returning hard coded path, error: " + str( err ) );
    return "/home/nao/behaviors";
# getBehaviorsLookupPath  - end

def listBehavior( strStartPath, bStanding = False, nFrequency = -1 ):
    "return a list of all behavior in a path"
    "if nFrequency is -1: don't jump in an occurence/frequency directory"
    strSpecificPath = "";
    if( bStanding ):
        strSpecificPath = "standing/";
    else:
        strSpecificPath = "sitting/";
    astrOccurence = ['1_often', '2_sometimes', '3_rarely' ];
    if( nFrequency != -1 ):
        strSpecificPath += astrOccurence[nFrequency] + '/';
    strNewLookupPath = getStandardBehaviorPath() + strStartPath + strSpecificPath;
    print( "listBehavior: strNewLookupPath: %s" % strNewLookupPath );
    listBe = altools.findFile( strNewLookupPath, ".xar", True );
#    print( "listBe: %s" % str( listBe ) );
    for i in range( len( listBe ) ):
        # listBe[i] = strStartPath + strSpecificPath + listBe[i]; # absolute path
        listBe[i] = listBe[i]; # absolute path
    return listBe;
# listBehavior - end

def getOneWaitAnimationName():
    "choose randomly one wait animation, and return its name"
    bStanding = ( branchOnNaoPosition() == 0 );
    
    nRand = random.randint( 0,99 );
    nOccurence = -1;
    if( nRand < 80 ):
        print( "getOneWaitAnimationName: %s: anim often" % ( altools.getHumanTimeStamp() ) );
        nOccurence = 0;
    elif( nRand < 97 ):
        print( "getOneWaitAnimationName: %s: anim sometimes !" % ( altools.getHumanTimeStamp() ) );
        nOccurence = 1;
    else:
        print( "getOneWaitAnimationName: %s: anim RARE !!!" % ( altools.getHumanTimeStamp() ) );
        nOccurence = 2;
    listPossible = listBehavior( getWaitAnimationPath(), bStanding, nOccurence );
    if( len( listPossible )  < 1 ):
        print( "WRN: getOneWaitAnimationName: no behavior for the position (%d,%d)\n" % ( bStanding, nOccurence ));
        return "";
    nChoosen = random.randint( 0, len( listPossible) - 1 );
    strChoosen = listPossible[nChoosen];
    print( "getOneWaitAnimationName: %s: choosen: '%s'" %  ( altools.getHumanTimeStamp(), strChoosen ) );
    return strChoosen;
    
# getOneWaitAnimationName - end

def getOnePossibleBehaviorName():
    "choose one behavior, return '', if no possible behavior"
    bStanding = ( branchOnNaoPosition() == 0 );
    listPossible = listBehavior( getBehaviorPath(), bStanding, -1 );
    if( len( listPossible ) < 1 ):
        print( "WRN: getOnePossibleBehaviorName: no behavior for this position\n" );
        return "";
    nChoosen = random.randint( 0, len( listPossible) - 1 );
    strChoosen = listPossible[nChoosen];    
    print( "getOnePossibleBehaviorName: %s: choosen: '%s'" %  ( altools.getHumanTimeStamp(), strChoosen ) );
    return strChoosen;
# getOnePossibleBehaviorName - end

def isItTheMomentToStandup():
    "decide to standup or not"
    if( isAutonomousStyleDefault() ):
        return isItTheMomentToStandup_Default();
    return isTheMomentToStandup_Shanghai(); # TODO: moins crado: faire un vrai test/switch/eval ...
# isItTheMomentToStandup - end

def isItTheMomentToStandup_Default():
    info = altools.myGetProxy( "ALInfo" );
    life = altools.myGetProxy( 'ALLife' );
    nBodyTemp = extractedData.getValue( 'body_temperature' );
    bRecentCalmdown = time.time() - extractedData.getValue( "calmdown_last_true", 0 ) < 180;
    print( "bRecentCalmdown: %d (duration: %d)" % ( int( bRecentCalmdown), int( time.time() - extractedData.getValue( "calmdown_last_true", 0 ) ) ) );
    
    
    if( info.getDuration_Standing() == -1 ):
        # standup condition
        bSittingTooShort = info.getDuration_Sitting() < 60; # can't stand less than 60 seconds after sitting
        if( not bSittingTooShort and nBodyTemp  < 67 and life.getArea() != altools.const.area_stay_sit and ( random.random() < 0.2 or life.getTryToStandMaxTimeValue() ) and not bRecentCalmdown ):
            if( life.isDisableStiffness() ):
                return False; # on met le cas a la suite, pour ne pas se bouffer du cpu pour un cas ultra rare
            return True;
        return False;

    # stop standing condition
    bStandingTooShort =  info.getDuration_Standing() < 15; # can't sit less than 15 second after standing
    bStandingTooLong = ( info.getDuration_Standing() > 60*5 and not life.getTryToStandMaxTimeValue() ) or nBodyTemp > 72;
    bEnoughBattery = extractedData.getValue( "battery_level" ) > 1;
    if( ( not bStandingTooLong or bStandingTooShort ) and not  bRecentCalmdown and bEnoughBattery ):
        # we stand ground !
        return True;
    return False;
# isItTheMomentToStandup_Default

def isTheMomentToStandup_Shanghai():
    return isItTheMomentToStandup_Default(); # TODO: your true Shanghai condition there
# isTheMomentToStandup_Shanghai

def getOneWait_6Poses():
    "recupere une série de 6 poses pour faire l'interpolation"
    bStanding = ( branchOnNaoPosition() == 0 );
    if( isAutonomousStyleDefault() ):
        import autonomous_pose_default
        if( bStanding ):
            listlist = autonomous_pose_default.listListMatrixes_standing;
        else:
            listlist = autonomous_pose_default.listListMatrixes_sitting;
    else:
        import autonomous_pose_shanghai
        if( bStanding ):
            listlist = autonomous_pose_shanghai.listListMatrixes_standing;
        else:
            listlist = autonomous_pose_shanghai.listListMatrixes_sitting;
    nNbrSerie = len( listlist );
    nNumSerie = random.randint( 0, nNbrSerie - 1 );
    return listlist[nNumSerie];
# getOneWait_6Poses - end

global_logBehavior_Mutex = mutex.mutex();
global_logBehavior_LastTime = time.time();
def logBehavior( strBehaviorName, strMessage ):
    global global_logBehavior_Mutex;
    global global_logBehavior_LastTime;    
    timeNow = time.time();
    rDurationSec = timeNow - global_logBehavior_LastTime;
    global_logBehavior_LastTime = timeNow;
    while( global_logBehavior_Mutex.testandset() == False ):
        print( "logBehavior(%s): locked" % strBehaviorName );
        time.sleep( 0.02 );
    
    strFilename = altools.getCachePath() + "Behav_%s.log" % strBehaviorName;
    file = open( strFilename, "at" );
    file.write( "%s (%5.2fs): %s\n" % ( altools.getHumanTimeStamp(), rDurationSec, strMessage ) );
    file.close();
    global_logBehavior_Mutex.unlock();
# logBehavior - end


global_autonomousLife_LogVar_nCpt = 0;
global_autonomousLife_LogVar_nCpuLoad = -1;
def autonomousLife_LogVar():
    global global_autonomousLife_LogVar_nCpt;
    global global_autonomousLife_LogVar_nCpuLoad;
    
    info = altools.myGetProxy( "ALInfo" );
    life = altools.myGetProxy( "ALLife" );    
    sentinel = altools.myGetProxy( "ALSentinel" );    
    mem = altools.myGetProxy( "ALMemory" );
    #~ rAvgMove = extractedData.getValue( "camera_medium_average_moving", 0 );
    #~ rLongAvgMove = extractedData.getValue( "camera_long_average_moving", 0 );
    rAvgMove = mem.getData( "extracted_data/camera_medium_average_moving", 0 );
    rLongAvgMove = mem.getData( "extracted_data/camera_long_average_moving", 0 );
    
    rAvgNoise = mem.getData( "UsageNoiseExtractor/MediumAverageEnergy", 0 );    
    rLongAvgNoise = mem.getData( "UsageNoiseExtractor/LongAverageEnergy", 0 );
    rExcitement = extractedData.getValue( "excitement" );
    rBoredom = extractedData.getValue( "boredom" );
    nState = mem.getData( "Autonomous/Life/State", 0 );
    nHumanVisible = int( extractedData.getValue( "human_visible_face_number" ) );
    strPosition = info.getBodyPosition();
    nTemperatureBody = extractedData.getValue( "body_temperature" );
    nTemperatureCpu = altools.getHeadTemperature();
    
    rWalkActivity = info.getWalkingActivity();
    
    if( global_autonomousLife_LogVar_nCpt == 0 ):
        # make some system call, less often
        global_autonomousLife_LogVar_nCpuLoad = int( altools.getCpuLoad() ) ;        
        
    nRam = sentinel.getRemainingRam() / 1024;
    bInternet = extractedData.getValue( "internet" );
    nBatteryLevel = mem.getData( "ALSentinel/BatteryLevel" );
    strOrder = life.getOrderParams();
    if( strOrder == None ):
        strOrder = "";
        
    # petit nettoyage:
    if( bInternet == altools.const.state_unknown ):
        bInternet = "no";
    if( nHumanVisible == altools.const.state_unknown ):
        nHumanVisible = "no";        
    strPosition = strPosition[0:len(strPosition)-3];
    
    altools.logToFile( "t: %d/%3d, ram:%3d, cpu:%3d, bat: %d, area: %d, stat: %d, step: %d, pos:%6s, sit/std: %3d/%3d, walk:%2.0f, hum: %s, int: %s, mov:%4.1f/%4.1f, nois:%4.0f/%4.0f, excit:%4.2f, bored:%3.2f,%s,%s,%d,%s" % 
            ( nTemperatureBody, nTemperatureCpu, nRam, global_autonomousLife_LogVar_nCpuLoad, nBatteryLevel, life.getArea(), nState, life.getStep(), strPosition, info.getDuration_Sitting(), info.getDuration_Standing(), rWalkActivity, str( nHumanVisible), str( bInternet ), rAvgMove, rLongAvgMove, rAvgNoise, rLongAvgNoise, rExcitement, rBoredom, life.getCurrentReaction(), life.getCurrentBehavior(), life.getOrder(), strOrder ) );
        
    global_autonomousLife_LogVar_nCpt += 1;
    if( global_autonomousLife_LogVar_nCpt > 10 ):
        global_autonomousLife_LogVar_nCpt = 0;
# autonomousLife_LogVar - end  


#testThings();

if( not altools.isOnNao() ):
    # test:
    if( False ):
        # testing
        usageDataManager.loadAll();
        usageDataManager.updateData( 'string_state_test', "coucou" );
        usageDataManager.updateData( 'string_state_test', "salut" );
        usageDataManager.updateData( 'time', time.time() );
        usageDataManager.exportToALMemory();
        # usageDataManager.saveGraphs();
    
    
    
    # graph des variables en temps presque réel:
    if( False ):
        someData = UsageData();
        someData.importFromALMemory("extracted_data/boredom");
        someData.drawGraph();
        
    # generation du graph de toutes les variables sur le robot:
    usageDataManager.importFromALMemory();    
    usageDataManager.dumpAll();
    print( "HISTO BODY:" + str( usageDataManager.getHist( "extracted_data/body_position", 200 ) ) );
    usageDataManager.saveGraphs();
    if( altools.isOnWin32() ):
        os.system( "explorer %s" % UsageData.getVarPath() + "graph" );
     

pass