# PANDAI BASIC TUTORIAL
# Author: Srinavin Nair

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


FLOOR_MASK=BitMask32.bit(1)
WALL_MASK=BitMask32.bit(2)
SENTINEL_MASK=BitMask32.bit(3)

class Hooded(AICharacter):

    def initialize(self):
        self.initTimer = True
        self.currentStatus = 0

        # we create a spotlight that will be the sentinel's eye and will be used to fire the inView method
        self.slight = Spotlight('slight')
        self.slight.setColor((1, 1, 1, 1))
        lens = PerspectiveLens()
        lens.setNear(0.1)
        lens.setFar(30)
        lens.setFov(60)
        self.slight.setLens(lens)
        self.slnp = self.get_node_path().attachNewNode(self.slight)
        self.slight.showFrustum()
        self.slnp.setH(self.slnp.getH()-180)
        self.hearing = 5.0

        self.detected = False
        self.pathfinding = False
        self.lostTarget = False
        self.countTime = False
        self.goingBack = False
        self.heard = False
        self.lastPos = self.get_node_path().getPos(render)


        self.sentinelHandler = CollisionHandlerQueue()

        # this is important: as we said the inView method don't cull geometry but take everything is in sight frustum - therefore to simulate an hide and seek feature we gotta cheat a little: this ray is masked to collide with walls and so if the avatar is behind a wall the ray will be 'deflected' (we'll see how later in the sent_traverse function) - so we know who's behind a wall but we fake we can't see it.
        sentraygeom = CollisionRay(0, 0, 0, 0, 1, 0)
        sentinelRay = self.get_node_path().attachNewNode(CollisionNode('sentinelray'))
        sentinelRay.node().addSolid(sentraygeom)
        # we set to the ray a cumulative masking using the or operator to detect either the avatar's body and the wall geometry
        sentinelRay.node().setFromCollideMask(SENTINEL_MASK|WALL_MASK)
        sentinelRay.node().setIntoCollideMask(BitMask32.allOff())
        # we add the ray to the sentinel collider and now it is ready to go
        base.cTrav.addCollider(sentinelRay, self.sentinelHandler)
        
        self.screechsound = loader.loadSfx("assets/sounds/enemies/nazgul_scream.mp3")


    def setPatrolPos(self, PatrolPos):
        
        self.currentTarget = 0
        self.PatrolPos = PatrolPos
        self.numTargets = len(PatrolPos)
        self.increment = 1
        self.getAiBehaviors().seek(self.PatrolPos[0])
      

    def distance(self, p1, p2):
        d = (p1.x - p2.x)**2  + (p1.y - p2.y)**2 + (p1.z - p2.z)**2
        return math.sqrt(d)

        
    #to update the AIWorld    
    def update(self):
        #self.currentStatus = 5
        captured = self.sent_detect()
        if (captured):
            if (self.currentStatus != 1):
                self.currentStatus = 1
                self.getAiBehaviors().pauseAi("all")
            self.lostTarget = False
            self.heard = False
            self.resetTimer()
            #print "To vendo"
        elif (self.heard):
            self.heard = False
            self.pursueTarget = self.hearingPos
            self.getAiBehaviors().pauseAi("all")
            self.currentStatus = 1
        elif (self.currentStatus == 1 and self.lostTarget == False and self.goingBack == False):
            self.startTimer(1.5)
            hasFinished = self.timer()
            if (hasFinished == True):
                self.lostTarget = True
                self.getAiBehaviors().pauseAi("all")
                #self.currentStatus = 4
                self.pursueTarget = self.TargetPos
                #print "perdi mesmo? "
            else:
                self.lostTarget = False
                #print "perdi, mas to procurando"
        #print "status: ", self.currentStatus
        if self.currentStatus == 0:
            self.patrol()
        elif self.currentStatus == 1:
            self.pathfind()
        elif self.currentStatus == 2:
            self.wander()
        elif self.currentStatus == 3:
            self.kill()
 
    def patrol(self):
        distance = self.distance(self.get_node_path().getPos(render), self.PatrolPos[self.currentTarget].getPos(render))
        self.goingBack = False
        #print "distance: ", distance
        if (distance < 1.0):
            self.startTimer(3)
            self.getAiBehaviors().pauseAi("all")
            #self.getAiBehaviors().wander(0.5, 0,0.5, 1.0)
            #self.getAiBehaviors().resumeAi("wander")
            hasFinished = self.timer()
            if (hasFinished == True):
                self.currentTarget += self.increment
                if (self.currentTarget == self.numTargets - 1):
                    self.increment = -1
                else:
                    if (self.currentTarget == 0):
                        self.increment = 1
                self.resetTimer()
                self.getAiBehaviors().pauseAi("all")
                self.getAiBehaviors().seek(self.PatrolPos[self.currentTarget])
                self.getAiBehaviors().resumeAi("seek")

    def pathfind(self):
        #print self.getAiBehaviors().behaviorStatus("pathfollow")
        if (not self.getAiBehaviors().behaviorStatus("pathfollow") in ["active", "done"]):
            self.getAiBehaviors().initPathFind("assets/navmesh.csv")
            #print "to entrando aqui", self.lostTarget
            self.getAiBehaviors().pauseAi("all")
            #print "vai coisar aqui de novo"
            self.getAiBehaviors().pathFindTo(self.pursueTarget)
            #print "mas aqui nao"
            #print "source: ", self.get_node_path().getPos(render)
            if (isinstance(self.pursueTarget, NodePath)):
                pass
                #print "aqui?"
                #print self.pursueTarget.getPos(render)
            else:
                #print "ou aqui?"
                #print self.pursueTarget
                pass

        #self.pathfinding = True
        currentPos = self.get_node_path().getPos(render)

        if (isinstance(self.pursueTarget, NodePath)):
            self.TargetPos = self.pursueTarget.getPos(render)
        else:
            self.TargetPos = self.pursueTarget
        #print currentPos, self.TargetPos
        #print self.TargetPos

        #if (self.getAiBehaviors().behaviorStatus("pathfollow") == "done"):
            #print "done"

        distance = self.distance(currentPos, self.TargetPos)
        #print distance

        #if (self.getAiBehaviors().behaviorStatus("pathfollow") == "done"):
            

        if (self.getAiBehaviors().behaviorStatus("pathfollow") == "done"):
            print "entrei?"
            print self.get_node_path().getPos()
            if (isinstance(self.pursueTarget, NodePath)):
                print "aqui?"
                print self.pursueTarget.getPos(render)
            else:
                print "ou aqui?"
                print self.pursueTarget
            if (self.lostTarget == False):
                if (self.goingBack == True):
                    print "uhul"
                    self.getAiBehaviors().pauseAi("all")
                    self.getAiBehaviors().seek(self.PatrolPos[self.currentTarget])
                    self.currentStatus = 0
                    self.getAiBehaviors().resumeAi("seek")
                    self.resetTimer()
                    self.goingBack = False
                else:
                    self.getAiBehaviors().pauseAi("all")
                    self.currentStatus = 3
                    print "aqui tambem?"
            else:
                print "perdi? ", self.lostTarget
                self.startTimer(5)
                self.countTime = True
                self.pathfinding = False
                self.currentStatus = 2
                self.radius = 5
                self.aoe = 10

        #print distance
        

    def wander(self):
        #print "wander - ", self.lostTarget
        if (self.getAiBehaviors().behaviorStatus("wander") != "active"):
            print "entrei aqui uma unica vez"
            self.getAiBehaviors().pauseAi("all")
            self.getAiBehaviors().wander(self.radius, 0,self.aoe, 1.0)
            #self.getAiBehaviors().resumeAi("wander")

        if (self.lostTarget == True and self.countTime == True):
            self.startTimer(5)
            hasFinished = self.timer()
            if (hasFinished == True):
                self.currentTarget += self.increment
                if (self.currentTarget == self.numTargets - 1):
                    self.increment = -1
                else:
                    if (self.currentTarget == 0):
                        self.increment = 1
                self.pursueTarget = self.PatrolPos[self.currentTarget]
                self.currentStatus = 1
                self.goingBack = True
                self.lostTarget= False
                self.getAiBehaviors().pauseAi("all")

                #self.getAiBehaviors().seek(self.PatrolPos[self.currentTarget])
                print "vai voltar pro pathfinding ", self.currentStatus
        


    def kill(self):
        print "Vou te kill"
        

    def sent_traverse(self, o):
        print ""
        # start the ray traverse
        base.cTrav.traverse(render)
        # align the colliders by order of piercing
        if (self.sentinelHandler.getNumEntries() > 0):
            self.sentinelHandler.sortEntries()
            entry = self.sentinelHandler.getEntry(0)
            colliderNode = entry.getIntoNode()
            # if the name of the 1st collider is our avatar then we say GOTCHA! the rest of the stuff is just for the show
            #for i in self.sentinelHandler.getEntries():
                #print i.getIntoNode().getName()
            if colliderNode.getName() == 'playercol':
                avatar_in_sight=True
                if self.detected == False:
                    self.detected = True
                    self.screechsound = loader.loadSfx("assets/sounds/enemies/anazgul_scream.mp3")
                    self.screechsound.play()
                return True
        avatar_in_sight=False
        return False

    #** Here then we'll unleash the power of isInView method - this function is just a query if a 3D point is inside its frustum so it works for objects with lens, such as cameras or even, as in this case, a spotlight. But to make this happen, we got cheat a little, knowing in advance who we're going to seek, to query its position afterwards, and that's what the next line is about: to collect all the references for objects named 'smiley'
    def sent_detect(self):
        intruders=base.render.findAllMatches("**/player*")
        #print "numero de intruders: ", len(intruders)
        for o in intruders:
            #print o.getPos()
        # query the spotlight if something listed as 'intruders' is-In-View at its position and if this is the case we'll call the traverse function above to see if is open air or hidden from the sentinel's sight
            #print o.getPos(render)
            if self.slnp.node().isInView(o.getPos(self.slnp)):
                #print "Ta no meu campo de visao"
                self.get_node_path().lookAt(o)
                if self.sent_traverse(o):
                    self.pursueTarget = o
                    #print "detectando: ", self.pursueTarget.getPos(render)
                    return True
        return False


    def timer(self):
        currentTime = time.time()
        diff = currentTime - self.time
        if (diff > self.interval):
            self.initTimer = True
            return True
        else:
            return False

    def resetTimer(self):
        self.initTimer = True

    def startTimer(self, interval):
        if (self.initTimer == True):
            self.interval = interval
            self.initTimer = False
            self.time = time.time()

    def addDynamicObject(self, object):
        self.getAiBehaviors().addDynamicObstacle(object)


    def hear(self, noisePos):
        dist = distance(self.get_node_path().getPos(), noisePos)
        if (dist <= self.hearing):
            self.heard = True
            self.hearingPos = noisePos
