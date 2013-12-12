from pandac.PandaModules import BitMask32

#TODO: Add nice interface supporting creation and naming of groups.
class CollisionMask:
	ALL   = BitMask32.allOn()
	NONE  = BitMask32.allOff()
	FLOOR = BitMask32.bit(1)
	WALL  = BitMask32.bit(2)