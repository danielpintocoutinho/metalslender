import sys,os

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Vec3
from direct.task import Task
from direct.interval.IntervalGlobal import *

def initCamera(pos = Vec3(0,0,0)):
    base.cam.reparentTo(render)
    base.cam.setPos(pos)

class CameraControls(DirectObject):
    '''
    classdocs
    '''


    def __init__(self):
        # Set the current viewing target
        
        self.focus = Vec3(55,-55,20)
        self.heading = 180
        self.pitch = 0
        self.mousex = 0
        self.mousey = 0
        self.last = 0
        self.keys = [0,0,0,0]
        
        # User controls
    
        self.accept('escape',sys.exit)    
        self.accept("w", self.setKeys, [0, 1])#forward
        self.accept("w-up", self.setKeys, [0, 0])
        self.accept("s", self.setKeys, [1, 1])#back
        self.accept("s-up", self.setKeys, [1, 0])
        self.accept("a", self.setKeys, [2, 1])#strafe left
        self.accept("a-up", self.setKeys, [2, 0])
        self.accept("d", self.setKeys, [3, 1])#strafe right
        self.accept("d-up", self.setKeys, [3, 0])
        
        
    def toggleInterval(self, ival):
        if (ival.isPlaying()):
            ival.pause()
        else:
            ival.resume()
             
    def setKeys(self, btn, value):
        self.keys[btn] = value
            
    def moveCamera(self, task):
        # walk (WASD)
        avatar = render.find("avatar")
        self.focus = avatar.getPos()
        flashlight = render.find("Spot")

        elapsed = task.time - self.last

        if (self.last == 0): elapsed = 0
        if (self.keys[0]):
            dir = avatar.getMat().getRow3(1) #0 is x, 1 is y, 2 is z,
            dir.setZ(0)
            self.focus = self.focus + dir * elapsed*40
            avatar.setFluidPos(self.focus )
        if (self.keys[1]):
            dir = avatar.getMat().getRow3(1)
            dir.setZ(0)
            self.focus = self.focus - dir * elapsed*40
            avatar.setFluidPos(self.focus)
        if (self.keys[2]):
            dir = avatar.getMat().getRow3(0)
            dir.setZ(0)
            self.focus = self.focus - dir * elapsed*20
            avatar.setFluidPos(self.focus)
        if (self.keys[3]):
            dir = avatar.getMat().getRow3(0)
            dir.setZ(0)
            self.focus = self.focus + dir * elapsed*20
            avatar.setFluidPos(self.focus)
        
        # positions the flashlight with the player 
        #avatar.setZ(15)
        flashlight.setFluidPos(avatar.getPos())
        flashlight.setZ(flashlight.getZ() + 4)
        flashlight.setHpr( avatar.getHpr())

        self.last = task.time
        return Task.cont
    
    def controlCamera(self, task):
        # player's vision
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, 100, 100):
            self.heading = self.heading - (x - 100) * 0.2
            self.pitch = self.pitch - (y - 100) * 0.2
        if (self.pitch < -90): self.pitch = -90
        if (self.pitch >  90): self.pitch =  90
        render.find("avatar").setHpr(self.heading,self.pitch,0)
        
        return Task.cont
    
    def start(self):
        taskMgr.add(self.controlCamera, "camera-task")
        taskMgr.add(self.moveCamera, "camera-move")
        #self.mainLoop = taskMgr.add(self.movement, 'movement', priority = 99)
        #self.mainLoop.last = 0

    def stop(self):
        taskMgr.remove("camera-task")
        taskMgr.remove("camera-mpve")
        