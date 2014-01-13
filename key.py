from collectible import Collectible

class Key(Collectible):
	KEY_PICK_SOUND = "assets/sounds/items/keys.mp3"
	
	def __init__(self, base, np):
		Collectible.__init__(self, base, np, Key.KEY_PICK_SOUND)
		self.lock = np.getTag('Key')