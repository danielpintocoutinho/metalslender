# from pandac.PandaModules import *
# from direct.showbase.DirectObject import DirectObject
# from direct.task import Task
# from direct.actor.Actor import Actor

from panda3d.core import CollisionHandlerQueue, CollisionNode, CollisionRay, CollisionSegment, NodePath, PerspectiveLens, Spotlight
from panda3d.ai import AICharacter

import math
import time

from collision import CollisionMask
from scene_obj import SceneObject

class Hooded(AICharacter):
	
	SIGHT=7.5
	FOV=60.0
	
	HEIGHT = 1.3
	
	STATE_PATROL = 0
	STATE_SEARCH = 1
	STATE_WANDER = 2
	STATE_ATTACK = 3
	STATE_PAUSED = 4
	
	class StatePatrol:
		pass

	def __init__(self, name, root, route, mass, movforce, maxforce):
		AICharacter.__init__(self, name, root, mass, movforce, maxforce)
		
		self.state = Hooded.STATE_PATROL
		
		self.initTimer = True
		self.attackTimer = True

		# we create a spotlight that will be the sentinel's eye and will be used to fire the inView method
		self.slight = Spotlight('slight')
		self.slight.setColor((1, 1, 1, 1))
		lens = PerspectiveLens()
		lens.setNear(0.1)
		lens.setFar(Hooded.SIGHT)
		lens.setFov(Hooded.FOV)
		
		self.slight.setLens(lens)
		self.slnp = self.get_node_path().attachNewNode(self.slight)
		#TODO: Substitute for a collision polygon, so that the player class alerts an enemy of its presence
		#self.slight.showFrustum()
		
		self.slnp.setH(self.slnp.getH()-180)
		self.slnp.setPos(0, 0, Hooded.HEIGHT)
		
		self.hearing = 5.0
		self.dynamicObstacles = []

		self.detected = False
		self.pathfinding = False
		self.lostTarget = False
		self.countTime = False
		self.goingBack = False
		self.heard = False
		self.isProtected = False
		self.attacked = False
		self.started = False

		self.sentinelHandler = CollisionHandlerQueue()
		
		#TODO: Intruders should be added via an external method
		self.intruders = []

		# this is important: as we said the inView method don't cull geometry but take everything is in sight frustum - therefore to simulate an hide and seek feature we gotta cheat a little: this ray is masked to collide with walls and so if the avatar is behind a wall the ray will be 'deflected' (we'll see how later in the sent_traverse function) - so we know who's behind a wall but we fake we can't see it.
		sentraygeom = CollisionSegment(0, 0, Hooded.HEIGHT, 0, Hooded.SIGHT, Hooded.HEIGHT)
		sentinelRay = self.get_node_path().attachNewNode(CollisionNode('sentinelray'))
		sentinelRay.node().addSolid(sentraygeom)
		# we set to the ray a cumulative masking using the or operator to detect either the avatar's body and the wall geometry
		sentinelRay.node().setFromCollideMask(CollisionMask.PLAYER)
		sentinelRay.node().setIntoCollideMask(CollisionMask.NONE)
		# we add the ray to the sentinel collider and now it is ready to go
		base.cTrav.addCollider(sentinelRay, self.sentinelHandler)
		
		self.screechsound = loader.loadSfx("assets/sounds/enemies/nazgul_scream.mp3")
		
		self.setPatrolPos(route)
		
	def __del__(self):
		self.slnp.removeNode()
		
	def addIntruder(self, intruder):
		self.intruders.append(intruder)

	def setPatrolPos(self, route):
		self.currentTarget = 0
		self.route = route
		self.numTargets = len(route)
		self.increment = 1
		self.getAiBehaviors().seek(self.route[0])
		
	#to update the AIWorld	  
   
	def update(self):
		if (self.started == False):
			return False
		captured = self.sent_detect()
		if (captured):
			if (self.isProtected):
				self.state = Hooded.STATE_PAUSED
			elif (self.state != Hooded.STATE_SEARCH):
				self.state = Hooded.STATE_SEARCH
				self.getAiBehaviors().pauseAi("all")
			self.lostTarget = False
			self.heard = False
			self.resetTimer()
		"""elif (self.heard):
			self.heard = False
			self.pursueTarget = self.hearingPos
			self.getAiBehaviors().pauseAi("all")
			self.state = Hooded.STATE_SEARCH
		elif (self.state == Hooded.STATE_SEARCH and self.lostTarget == False and self.goingBack == False):
			self.startTimer(1.5)
			hasFinished = self.timer()
			if (hasFinished == True):
				self.lostTarget = True
				self.getAiBehaviors().pauseAi("all")
				#self.state = 4
				self.pursueTarget = self.TargetPos
			else:
				self.lostTarget = False"""
				
		if self.state == Hooded.STATE_PATROL:
			self.patrol()
		elif self.state == Hooded.STATE_SEARCH:
			self.pursue()
		elif self.state == Hooded.STATE_WANDER:
			self.wander()
		elif self.state == Hooded.STATE_ATTACK:
			self.kill()
		elif self.state == Hooded.STATE_PAUSED:
			self.pause()


		#elif self.state == Hooded.STATE_SEARCH:
			#self.pathfind()
			
		if (self.attacked):
			self.attacked = False
			return True
		return False
 
 	#TODO: Patrol is ready for refactoring, if needed
 	PATROL_PAUSE = 3.0
 	PATROL_DISTANCE = 1.0
	def patrol(self):
		distance = self.get_node_path().getDistance(self.route[self.currentTarget])
		if (distance < Hooded.PATROL_DISTANCE):
			self.startTimer(Hooded.PATROL_PAUSE)
			self.getAiBehaviors().pauseAi("all")
			if self.timer():
				self.currentTarget = (self.currentTarget + 1) % len(self.route)
				self.resetTimer()
				self.getAiBehaviors().pauseAi("all")
				self.getAiBehaviors().seek(self.route[self.currentTarget])
				self.getAiBehaviors().resumeAi("seek")

	def pathfind(self):
		if (not self.getAiBehaviors().behaviorStatus("pathfollow") in ["active", "done"]):
			self.getAiBehaviors().initPathFind("assets/navmesh.csv")
			self.getAiBehaviors().pauseAi("all")
			if isinstance(self.pursueTarget, NodePath):
				self.getAiBehaviors().pathFindTo(self.pursueTarget)
			else:
				self.getAiBehaviors().pathFindTo(self.pursueTarget.getNodePath())
			for i in self.dynamicObstacles:
				self.getAiBehaviors().addDynamicObstacle(i)

		#self.pathfinding = True
		currentPos = self.get_node_path().getPos(render)

		if (isinstance(self.pursueTarget, NodePath)):
			self.TargetPos = self.pursueTarget
		else:
			self.TargetPos = self.pursueTarget.getNodePath()

# 		print currentPos, self.TargetPos
		distance = self.get_node_path().getDistance(self.TargetPos)
			
		if (self.getAiBehaviors().behaviorStatus("pathfollow") == "done"):
			if (distance > 5):
				self.getAiBehaviors().pauseAi("all")
				return

			if (self.lostTarget == False):
				if (self.goingBack == True):
					self.getAiBehaviors().pauseAi("all")
					self.getAiBehaviors().seek(self.route[self.currentTarget])
					self.state = Hooded.STATE_PATROL
					self.getAiBehaviors().resumeAi("seek")
					self.resetTimer()
					self.goingBack = False
				elif (self.heard == True):
						if (isinstance(self.pursueTarget, NodePath)):
							self.getAiBehaviors().pauseAi("all")
							self.state = Hooded.STATE_ATTACK
						else:
							self.startTimer(5)
							self.countTime = True
							self.pathfinding = False
							self.state = Hooded.STATE_WANDER
							self.radius = 5
							self.aoe = 10
				else:
					self.getAiBehaviors().pauseAi("all")
					self.state = Hooded.STATE_ATTACK
			else:
				self.startTimer(5)
				self.countTime = True
				self.pathfinding = False
				self.state = Hooded.STATE_WANDER
				self.radius = 5
				self.aoe = 10

	def wander(self):
		if (self.getAiBehaviors().behaviorStatus("wander") != "active"):
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
				self.pursueTarget = self.route[self.currentTarget]
				self.state = Hooded.STATE_SEARCH
				self.goingBack = True
				self.lostTarget= False
				self.getAiBehaviors().pauseAi("all")

				#self.getAiBehaviors().seek(self.route[self.currentTarget])
		
	def kill(self):
		if (self.attackTimer):
			self.attacked = True
			self.attackTimer = False
			self.startTimer(3)
			self.pause()
		else:
			hasFinished = self.timer()
			if (hasFinished):
				self.attackTimer = True
				self.resetTimer()
				self.state = Hooded.STATE_SEARCH
			else:
				self.attacked = False

	#TODO: Use event handling, instead?
	def sent_traverse(self, suspect):
		if (self.sentinelHandler.getNumEntries() > 0):
			self.sentinelHandler.sortEntries()
# 			for i in range(self.sentinelHandler.getNumEntries()):
# 				print self.sentinelHandler.getEntry(i)
			entry = self.sentinelHandler.getEntry(0)
			self.sentinelHandler.clearEntries()
			colliderNP = entry.getIntoNodePath()
			if colliderNP.getParent() == suspect.getNodePath():
# 				self = False
				if self.detected == False:
					self.detected = True
					self.screechsound.play()
					suspect.boo()
				return True
			#TODO: This was meant for the implementation of safe areas, where the player could not be reached
			elif colliderNP.getName() == 'lightarea':
				newEntry = self.sentinelHandler.getEntry(1)
				newColliderNode = newEntry.getIntoNode()
				if (newColliderNode.getName() == 'playercol'):
					#check if player is really inside light area
					self.isProtected = True
					return True
		return False

	#** Here then we'll unleash the power of isInView method - this function is just a query if a 3D point is inside its frustum so it works for objects with lens, such as cameras or even, as in this case, a spotlight. But to make this happen, we got cheat a little, knowing in advance who we're going to seek, to query its position afterwards, and that's what the next line is about: to collect all the references for objects named 'smiley'
   
	def sent_detect(self):
		for o in self.intruders:
		# query the spotlight if something listed as 'intruders' is-In-View at its position and if this is the case we'll call the traverse function above to see if is open air or hidden from the sentinel's sight
			if self.slnp.node().isInView(o.getNodePath().getPos(self.slnp)):
				self.get_node_path().lookAt(o.getNodePath())
				if self.sent_traverse(o):
					self.pursueTarget = o
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

	def addDynamicObject(self, dynamicObject):
		self.dynamicObstacles.append(dynamicObject)

	def hear(self, noisePos):
		dist = self.get_node_path().getDistance(noisePos)
		if (dist <= self.hearing):
			self.heard = True
			self.hearingPos = noisePos

	def pause(self):
		self.getAiBehaviors().pauseAi("all")
		#print "nao pausei?"

	def start(self):
		self.started = True

	def stop(self):
		self.started = False

	def clean(self):
		loader.unloadSfx(self.screechsound)

	def pursue(self):
		self.getAiBehaviors().pursue(self.pursueTarget.getNodePath())
		if (self.get_node_path().getDistance(self.pursueTarget.getNodePath()) < 1):
			self.state = Hooded.STATE_ATTACK