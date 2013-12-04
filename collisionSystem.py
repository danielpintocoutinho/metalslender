'''
Created on 31/10/2013

@author: Glauco
'''
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import ActorNode, CollisionHandlerQueue, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay

floorHandler = CollisionHandlerGravity()
floorHandler.setGravity(9.81+50)
floorHandler.setMaxVelocity(100)

wallHandler = CollisionHandlerPusher()

FLOOR_MASK=BitMask32.bit(1)
WALL_MASK=BitMask32.bit(2)
SENTINEL_MASK=BitMask32.bit(3)
