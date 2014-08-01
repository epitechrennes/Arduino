# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Type tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called Type, but risk of masking with the keyword type.

"""Tools to know the type of a variable."""
print( "importing abcdk.typetools" );

def isInt( nVariable ):
    "has the variable the dict type ?"
    return isinstance( nVariable, int );
# isArray - end

def isDict( aVariable ):
    "has the variable the dict type ?"
    return isinstance( aVariable, dict );
# isArray - end    

def isArray( aVariable ):
    "has the variable the array type ?"
    try:
        aVariable[0];
    except BaseException, err:
        return False;
    return not isString( aVariable ); #car les strings aussi ont la méthode crochet
# isArray - end    

def isString( strVariable ):
  "has the variable the string type ? (bytes or unicode)"
  try:
    # if( type( strVariable ) == type( "some string") ):
    if isinstance( strVariable, basestring ): # True for both Unicode and byte strings
      return True;
  except BaseException, err:
    pass
  return False;
# isString - end

def isString_Bytes( strVariable ):
  "has the variable the string type bytes ?"
  try:
    if isinstance( strVariable, str ):
      return True;
  except BaseException, err:
    pass
  return False;
# isString_Bytes - end

def isString_Unicode( strVariable ):
  "has the variable the string type unicode ?"
  return isString( strVariable ) and not isString_Bytes( strVariable );
# isString_Unicode - end
