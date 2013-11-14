from panda3d.core import *
import sys,os

import direct.directbase.DirectStart
from pandac.PandaModules import ActorNode, CollisionHandlerQueue, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay
from pandac.PandaModules import Vec3
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.actor import Actor
from direct.task.Task import Task
from random import *

class SceneObj(DirectObject):
    '''
    classdocs
    '''


    def __init__(self, name, model_path = '' , pos=Vec3(0,0,0), scale=1.0, source = render,actor=False):
        
        self.modelNP =source.attachNewNode(name)
        self.name = name
        if (actor==False):
            if (model_path):
                self.model = loader.loadModel(model_path)
                self.model.reparentTo(self.modelNP)
                self.setModelPos(Vec3(0,0,0))
                self.model.setScale(scale)
                self.model.setCollideMask(BitMask32.allOff())
                self.hasModel = True
            else: self.hasModel = False
            self.setNodePathPos(pos)
        self.modelCollider = None
        self.modelRay = None
        self.floorHandler = CollisionHandlerGravity()
        self.floorHandler.setGravity(9.81+25)
        self.floorHandler.setMaxVelocity(100)
        # wall
        self.wallHandler = CollisionHandlerPusher()
    
    def setObjCollision(self, solid = CollisionSphere(0, 0, 0, 2)):
        self.modelCollider = self.modelNP.attachNewNode(CollisionNode(self.name + 'cnode'))
        self.modelCollider.node().addSolid(solid)
    
    def setFloorCollision(self, fromMask, intoMask):
        # the avatar's ray collider for ground collision detection
        raygeometry = CollisionRay(0, 0, 1, 0, 0, -1)
        self.modelRay = self.modelNP.attachNewNode(CollisionNode(self.name + 'Ray'))
        self.modelRay.node().addSolid(raygeometry)
        self.modelRay.node().setFromCollideMask(fromMask)
        self.modelRay.node().setIntoCollideMask(intoMask)
        self.floorHandler.addCollider(self.modelRay, self.modelNP)
        # ...then add the avatar collide sphere and the wall handler
        base.cTrav.addCollider(self.modelRay, self.floorHandler)
        
        
    def setWallCollision(self, fromMask, intoMask):
        self.modelCollider.node().setFromCollideMask(fromMask)
        self.modelCollider.node().setIntoCollideMask(intoMask)
        self.wallHandler.addCollider(self.modelCollider, self.modelNP)
        
        base.cTrav.addCollider(self.modelCollider, self.wallHandler)
    
    def setOtherCollision(self, fromMask, intoMask, handler):
        self.avatarBody = avatar.attachNewNode(CollisionNode('smileybody'))
        self.avatarBody.node().addSolid(CollisionSphere(0, 0, 0, 1.2))
        self.avatarBody.node().setFromCollideMask(fromMask)
        self.avatarBody.node().setIntoCollideMask(intoMask)
        base.cTrav.addCollider(self.avatarBody, handler)
        
    def setTerrainCollision(self, wallPath, floorPath, wallMask, floorMask):
        self.floorcollider=self.model.find(floorPath)
        self.floorcollider.node().setFromCollideMask(BitMask32.allOff())
        self.floorcollider.node().setIntoCollideMask(floorMask)
        self.wallcollider=self.model.find(wallPath)
        self.wallcollider.node().setFromCollideMask(BitMask32.allOff())
        self.wallcollider.node().setIntoCollideMask(wallMask)
        
    def getFloorHandler(self):
        return self.floorHandler
    
    def getPos(self):
        return self.model.getPos()
    
    def setModelPos(self,pos):
        self.model.setPos(pos)
        
    def setNodePathPos(self,pos):
        self.modelNP.setPos(pos)
    
    def getScale(self):
        return self.model.getScale()
    
    def setScale(self,scale):
        self.model.setScale(scale)
    
    def setPosInterval(self, time, startPos, finalPos, onAxis = True):
        if (onAxis): return self.modelNP.posInterval(time,finalPos,startPos)
        else: return self.model.posInterval(time,finalPos,startPos)
    
    def setHprInterval(self, time, startAngle, finalAngle, onAxis = True):
        if (onAxis): return self.modelNP.hprInterval(time,finalAngle,startAngle)
        else: return self.model.hprInterval(time,finalAngle,startAngle)
    
    def getModel(self):
        return self.model
    
    def getNodePath(self):
        return self.modelNP
        