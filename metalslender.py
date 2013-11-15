#!/usr/bin/python
from panda3d.core import *
import sys,os
loadPrcFileData("", "prefer-parasite-buffer #f")

import direct.directbase.DirectStart
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.actor import Actor
from direct.task.Task import Task
from random import *
import camera
import scene_obj
import scene_actor
import animation_data
import interface
import lighting
import collisionSystem

camera.initCamera(Vec3(-30,45,26))
cons = camera.CameraControls()
cons.start()
menu = interface.Interface()
lights = lighting.Lighting()

floorHandler = collisionSystem.floorHandler
wallHandler = collisionSystem.wallHandler
sentinelHandler = collisionSystem.sentinelHandler

#** Collision masks
FLOOR_MASK=collisionSystem.FLOOR_MASK
WALL_MASK=collisionSystem.WALL_MASK
SENTINEL_MASK=collisionSystem.SENTINEL_MASK

class MetalSlender(DirectObject):
    
        
    def __init__(self):
        # Preliminary capabilities check.
        if (self.initMessages()): return
        
        self.initConfig()
        #Detecao de intrusos
        #frustum=False
        #intruders=base.render.findAllMatches("**/smiley*")

        # Load the scene.
        self.room = scene_obj.SceneObj("room","lcg12")  
        self.room.setTerrainCollision("**/ExtWalls","**/Floor",WALL_MASK,FLOOR_MASK)
        
        self.pandaAxis = scene_actor.SceneActor("panda", "panda-model", pos = Vec3(9,0,100), scale = 0.02, animations = animation_data.panda_anims)

        self.pandaWalk = self.pandaAxis.setAnimInterval('walk', 1.8)
        self.pandaWalk.loop()
        self.pandaMovement = self.pandaAxis.setHprInterval(10.0,Point3(360,0,0),Point3(0,0,0))
        self.pandaMovement.loop()
        self.pandaAxis.setObjCollision()
        self.pandaAxis.setFloorCollision(FLOOR_MASK, BitMask32.allOff())
        
        self.avatar=scene_obj.SceneObj(name = "avatar", pos = Vec3(-30,45,126))
        self.avatar.setObjCollision()
        self.avatar.setFloorCollision(FLOOR_MASK, BitMask32.allOff())
        self.avatar.setWallCollision(WALL_MASK, BitMask32.allOff())
        base.cam.reparentTo(self.avatar.getNodePath())
        base.cam.setPos(Vec3(0,0,5))
        
        self.teapot=scene_obj.SceneObj("teapot","teapot", Vec3(0,-20,10), 1)  
        self.teapotMovement = self.teapot.setHprInterval(10,Point3(0,0,0),Point3(0,360,360), False)
        self.teapotMovement.loop()
        
        # User controls
        self.addCommands()
        
        lights.addSpotlight("Spot", render)
        lights.addSpotlight(name = "Spot2", source = self.teapot.getModel(), near = 10, far = 100)
        lights.setAmbientlight()

        # Important! Enable the shader generator.
        render.setShaderAuto()

    
# end of __init__

    def initConfig(self):
        base.cTrav=CollisionTraverser()
    
        base.setBackgroundColor(0,0,0.2,1)
    
        base.camLens.setNearFar(1.0,10000)
        base.camLens.setFov(75)
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        
    def addCommands(self):
        self.accept('escape',sys.exit)
        self.accept("space",self.avatarjump, [self.avatar])
        #self.accept("f", frustum_toggle)
        self.accept("p", self.toggleInterval, [self.pandaWalk])
        self.accept("t", self.toggleInterval, [self.teapotMovement])
        
    def initMessages(self):
        if (base.win.getGsg().getSupportsBasicShaders()==0):
            self.t=menu.addTitle("Shadow Demo: Video driver reports that shaders are not supported.")
            return False
        if (base.win.getGsg().getSupportsDepthTexture()==0):
            self.t=menu.addTitle("Shadow Demo: Video driver reports that depth textures are not supported.")
            return False
        
        self.inst_m = menu.addInstructions(0.95 , 'WASD : walk')
        self.inst_p = menu.addInstructions(0.90 , 'P : stop/start the Panda Rotation')
        self.inst_t = menu.addInstructions(0.85 , 'T : stop/start the Teapot')
        self.inst_h = menu.addInstructions(0.80 , 'space : Jump')

    def toggleInterval(self, ival):
        if (ival.isPlaying()):
            ival.pause()
        else:
            ival.resume()
            
    def avatarjump(self, obj):
        if obj.getFloorHandler().isOnGround(): obj.getFloorHandler().addVelocity(40)
    
    def set_siren(v):
        if v:
            sirensound.play()
            siren.show()
            sirenrotival.loop()
        else:
            sirensound.stop()
            siren.hide()
            sirenrotival.pause()
    
    def frustum_toggle():
        global frustum, tsk
        frustum=not frustum
        if frustum: slight.showFrustum()
        else: slight.hideFrustum()

#** Now check this out closely: this function will be called by some routine below to shoot the sentinel ray and see what is traversed by it - as you know from the basic/step1 and 2, after the traverse, the queue is full of what is found colliding with the handler - since we got a particular kind of FROM collider - a ray - that spear like a long pike everything on his path, if we sort the queue with sortEntries() we could know who's the first object the ray has pierced, and of course if it is not our avatar we don't care further to know who'll come then, simulating indeed a seek and hide feature.
    def sent_traverse(o):
        # start the ray traverse
        base.cTrav.traverse(render)
        # align the colliders by order of piercing
        if (sentinelHandler.getNumEntries() > 0):
            sentinelHandler.sortEntries()
            entry = sentinelHandler.getEntry(0)
            colliderNode = entry.getIntoNode()
            # if the name of the 1st collider is our avatar then we say GOTCHA! the rest of the stuff is just for the show
            if colliderNode.getName() == 'smileybody':
                avatar_in_sight=True
                if sentrotival.isPlaying():
                    sentrotival.pause()
                    set_siren(1)
                return True
        if not sentrotival.isPlaying():
            sentrotival.loop()
            set_siren(0)
        avatar_in_sight=False
        return False

    def sent_detect(task):
        for o in intruders:
        # query the spotlight if something listed as 'intruders' is-In-View at its position and if this is the case we'll call the traverse function above to see if is open air or hidden from the sentinel's sight
            if slnp.node().isInView(o.getPos(slnp)):
                sentinel.lookAt(o)
                if sent_traverse(o): return task.cont
        if not sentrotival.isPlaying():
            sentrotival.loop()
            set_siren(0)
        return task.cont
  
    def shaderSupported(self):
        return base.win.getGsg().getSupportsBasicShaders() and \
               base.win.getGsg().getSupportsDepthTexture() and \
               base.win.getGsg().getSupportsShadowFilter()
  

MetalSlender()
run()
