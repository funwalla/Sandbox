# -*- coding: utf-8 -*-
"""
From http://www.joelonsoftware.com/items/2006/08/01.html
"""

## First example
#print "I'd like some Spaghetti!"
#print "I'd like some Chocolate Moose!"

## First example refactored
def SwedishChef( food ):
    print "I'd really like some " + food + "!"

## Second example    
def PutInPot( thing ):
    print "Put the " + thing + " in the pot."

def BoomBoom( thing ):
    print "Dice the " + thing + "."
    
#def Cook( i1, i2, f ):
    #print "Get the " + i1
    #f(i1)
    #f(i2)
    #print
    
def printFunction(x):
    print x

def Cook( i1, i2, f1, f2 ):
    print "Get the " + i1
    f1( f2(i1) )
    f1( f2(i2) )
    print

## Third example -- mapping
def map2( f, a):
    return [ f(i) for i in a]



if __name__ == '__main__':
    
    #SwedishChef("Spaghetti")
    #SwedishChef("Chocolate Moose")

    #Cook("lobster", "water", PutInPot)
    #Cook("chicken", "coconut", BoomBoom)

    #Calling Cook with lambda functions
    Cook("lobster", "water", 
         printFunction, lambda x:"Put the " + x + " in the pot. (lambda)")
    Cook("chicken", "coconut", 
         printFunction, lambda x: "Dice the " + x + ". (lambda)")
    
    #print map2( lambda x: x*2, range(4))
    print map2( printFunction, range(4))