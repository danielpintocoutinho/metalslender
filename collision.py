from pandac.PandaModules import BitMask32

#TODO: Add nice interface supporting creation and naming of groups.
class CollisionMask:
	ALL      = BitMask32.allOn()
	NONE     = BitMask32.allOff()
	FLOOR    = BitMask32.bit(1)
	WALL     = BitMask32.bit(2)
	#TODO: Currently useless
	SENTINEL = BitMask32.bit(3)
	#TODO: Currently useless
	PLAYER   = BitMask32.bit(4)
	DOOR     = BitMask32.bit(5)
	#TODO: Currently useless
	TREE     = BitMask32.bit(6)
	#TODO: Currently useless
	KEEP     = BitMask32.bit(7)
	HAND     = BitMask32.bit(8)