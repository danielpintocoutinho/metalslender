# PANDAI BASIC TUTORIAL
# Author: Srinavin Nair

#for directx window and functions
import direct.directbase.DirectStart
#for most bus3d stuff
from pandac.PandaModules import *
#for directx object support
from direct.showbase.DirectObject import DirectObject
#for tasks
from direct.task import Task
#for Actors
from direct.actor.Actor import Actor
#for Pandai
from panda3d.ai import *

import math
import time
from hooded import *

speed = 0.25

class World(DirectObject):

    def __init__(self):
        #base.disableMouse()
        base.cam.setPosHpr(0,00,60,0,-90,0)
        base.cTrav=CollisionTraverser()
        self.keyMap = {"left":0, "right":0, "up":0, "down":0}
        #movement
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["up",1])
        self.accept("s", self.setKey, ["down",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["up",0])
        self.accept("s-up", self.setKey, ["down",0])
        #movement task
        taskMgr.add(self.Mover,"Mover")
        
        self.loadModels()
        self.setAI()
       
    def loadModels(self):

		# Seeker
        self.seeker = Actor("models/hooded")
        #self.seeker = Actor("models/ralph",{"run":"models/ralph-run", "walk":"models/ralph-walk"})
        self.seeker.setCollideMask(BitMask32.allOff())
        self.seeker.setPos(Vec3(-5, 0, 0))
        self.seeker.reparentTo(render)
        self.seeker.setScale(0.7)
        # Target1
        self.target1 = loader.loadModel("models/arrow")
        self.target1.setColor(1,0,0)
        self.target1.setPos(10,0,0)
        self.target1.setScale(1)
        self.target1.reparentTo(render)
        # Target2
        self.target2 = loader.loadModel("models/arrow")
        self.target2.setColor(0,1,0)
        self.target2.setPos(-10,0,0)
        self.target2.setScale(1)
        self.target2.reparentTo(render)
        # Target3
        self.target3 = loader.loadModel("models/arrow")
        self.target3.setColor(0,0,1)
        self.target3.setPos(-10,10,0)
        self.target3.setScale(1)
        self.target3.reparentTo(render)

        #self.environ = loader.loadModel("models/groundPlane")      
        self.environ = loader.loadModel("models/teste2")
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)


        #self.seeker = Actor("models/ralph",{"run":"models/ralph-run", "walk":"models/ralph-walk"})

        #** our smiley avatar setup - see below that we added more stuff than usual
        self.avatar = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.avatar.setScale(0.5)
        self.avatar.reparentTo(render)
        self.avatar.setCollideMask(BitMask32.allOff())
        self.avatar.setPos(8, -20,0)

        self.avatar.loop("walk")
        # here the additional stuff: it is a collider that will be used by the sentinel's ray to see if smiley is behind a wall - this is essential because the isInView method don't provide geometry culling but act as a body scanner reading everything found into its frustum's sight, including walls and other obstacles as well.
        self.avatarBody = self.avatar.attachNewNode(CollisionNode('ralph'))
        self.avatarBody.node().addSolid(CollisionSphere(0, 0, 0, 1.2))
        self.avatarBody.node().setFromCollideMask(BitMask32.allOff())
        self.avatarBody.node().setIntoCollideMask(SENTINEL_MASK)
        # as you should already know, to be recognized by, we must add the avatar's body collider to the sentinel's handler.
        

        #self.box = loader.loadModel("models/box")
        #self.box.setPos(0,-5,0)
        #self.box.setScale(0.5)
        #self.box.setColor(1,1,0)
        #self.box.reparentTo(render)

        #self.boxBody = self.box.attachNewNode(CollisionNode('box'))
        #self.boxBody.node().addSolid(CollisionSphere(0, 0, 0, 8))
        #self.boxBody.node().setFromCollideMask(BitMask32.allOff())
        #self.boxBody.node().setIntoCollideMask(WALL_MASK)



    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
 
        self.hooded = Hooded("seeker",self.seeker, 100, 0.05, 5)
        self.hooded.initialize()
        base.cTrav.addCollider(self.avatarBody, self.hooded.sentinelHandler)
        #self.hooded.setPatrolPos([Vec3(10,0,0), Vec3(-10, 0, 0), Vec3(-10, 10, 0)])
        #self.target1.hide()
        #self.target2.hide()
        #self.target3.hide()
        #self.avatar.hide()
        self.hooded.setPatrolPos([self.target1, self.target2, self.target3])
        self.AIworld.addAiChar(self.hooded)

        #self.hooded.getAiBehaviors().addStaticObstacle(self.target2)

        #self.seeker.loop("walk")
		
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")


        
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.hooded.update()
        self.AIworld.update()            
        return Task.cont

    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def Mover(self,task):
        startPos = self.avatar.getPos()
        if (self.keyMap["left"]!=0):
            self.avatar.setPos(startPos + Point3(-speed,0,0))
        if (self.keyMap["right"]!=0):
            self.avatar.setPos(startPos + Point3(speed,0,0))
        if (self.keyMap["up"]!=0):
            self.avatar.setPos(startPos + Point3(0,speed,0))
        if (self.keyMap["down"]!=0):
            self.avatar.setPos(startPos + Point3(0,-speed,0))
            
        #if(self.pointer_move == True and self.box != 0):
         #   self.box.setPos(self.avatar.getPos())
                
        return Task.cont
 
w = World()
run()

