from pandac.PandaModules import BitMask32

class CollisionMask:
	ALL      = BitMask32.allOn()
	NONE     = BitMask32.allOff()
	FLOOR    = BitMask32.bit(1)
	WALL     = BitMask32.bit(2)
	HAND     = BitMask32.bit(3)
	PLAYER   = BitMask32.bit(4)
#TODO: Useless flags, should be removed
#	SENTINEL = BitMask32.bit(5)
# 	DOOR     = BitMask32.bit(6)
# 	TREE     = BitMask32.bit(7)
# 	KEEP     = BitMask32.bit(8)