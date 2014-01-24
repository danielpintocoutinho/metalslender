from pandac.PandaModules import BitMask32

class CollisionMask:
	ALL    = BitMask32.allOn()
	NONE   = BitMask32.allOff()
	SCENE  = BitMask32.bit(1)
	HAND   = BitMask32.bit(2)
	PLAYER = BitMask32.bit(3)