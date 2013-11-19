'''
Created on 31/10/2013

@author: Glauco
'''
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import ActorNode, CollisionHandlerQueue, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay

floorHandler = CollisionHandlerGravity()
floorHandler.setGravity(9.81+25)
floorHandler.setMaxVelocity(100)
# wall
wallHandler = CollisionHandlerPusher()
# and the sentinel
sentinelHandler = CollisionHandlerQueue()
#** Collision masks
FLOOR_MASK=BitMask32.bit(1)
WALL_MASK=BitMask32.bit(2)
SENTINEL_MASK=BitMask32.bit(3)

class Stage(DirectObject):
    '''
    classdocs
    '''


    def __init__(self, name,):
        '''
        Constructor -- Em desenvolvimento
        '''
        
        
        
        #** Here the sentinel - the only collider we put in it is the ray detector (see below)
        sentinel = loader.loadModel("frowney")
        sentinel.setCollideMask(BitMask32.allOff())
        sentinel.reparentTo(render)
        sentinel.setPos((7.83, -25.31, 24))
        player_in_sight=False
        # we create a spotlight that will be the sentinel's eye and will be used to fire the inView method
        slight = Spotlight('slight')
        slight.setColor((1, 1, 1, 1))
        lens = PerspectiveLens()
        lens.setFar(80)
        slight.setLens(lens)
        slnp = sentinel.attachNewNode(slight)
        render.setLight(slnp)
        # this is important: as we said the inView method don't cull geometry but take everything is in sight frustum - therefore to simulate an hide and seek feature we gotta cheat a little: this ray is masked to collide with walls and so if the player is behind a wall the ray will be 'deflected' (we'll see how later in the sent_traverse function) - so we know who's behind a wall but we fake we can't see it.
        sentraygeom = CollisionRay(0, 0, 0, 0, 1, 0)
        sentinelRay = sentinel.attachNewNode(CollisionNode('sentinelray'))
        sentinelRay.node().addSolid(sentraygeom)
        # we set to the ray a cumulative masking using the or operator to detect either the player's body and the wall geometry
        sentinelRay.node().setFromCollideMask(SENTINEL_MASK|WALL_MASK)
        sentinelRay.node().setIntoCollideMask(BitMask32.allOff())
        # we add the ray to the sentinel collider and now it is ready to go
        base.cTrav.addCollider(sentinelRay, sentinelHandler)
        # this interval will rotate the sentinel 360 deg indefinitely
        a=-30
        sentrotival = sentinel.hprInterval(8, (630,a,0), startHpr=(270,a,0))
        
        #** the floor handler need to know what it got to handle: the player and its floor ray
        playerFloorHandler.addCollider(playerRay, playerNP)
        # ...then add the player collide sphere and the wall handler
        wallHandler.addCollider(playerCollider, playerNP)
        # let's start'em up
        base.cTrav.addCollider(playerRay, playerFloorHandler)
        base.cTrav.addCollider(playerCollider, wallHandler)
        
        #** this is a siren, just for the show (and to annoy ppl)
        siren=snipstuff.load3Dimage('textures/siren.png')
        siren.hide()
        siren.setScale(30,1,10)
        siren.setPos(sentinel.getPos())
        sirenrotival=siren.hprInterval(3, (360,0,0), startHpr=(0,0,0))
        sirensound = loader.loadSfx("sounds/siren.mp3")
        sirensound.setLoop(True)
        
