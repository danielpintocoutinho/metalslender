from direct.gui.DirectGui import *
from panda3d.core import TransparencyAttrib

class MainMenu:
	#TODO: Refactor names
	def __init__(self, parent):
		logoimg = ("assets/images/metalslender.png")
		playimg = ("assets/images/PlayButton.png")
		playimghover = ("assets/images/PlayButtonHover.png")
		exitimg = ("assets/images/ExitButton.png")
		exitimghover = ("assets/images/ExitButtonHover.png")

		self.mainFrame = DirectFrame(
		frameColor=(1,0,0,0.0),
		#(left, right, bottom, top)
		frameSize=(-2,-0.6,0.9,-0.2 ))

		self.logo = DirectButton(
			parent = self.mainFrame,
			image = logoimg,
			image_scale = (3.66,1,1),
			relief = None,
			#text = ("Singleplayer"), 
			pos = (0.15,0,0.15),
			scale=0.15,
			command = parent.newGame
			)
			
		self.new = DirectButton(
			parent = self.mainFrame,
			image = (playimg, playimghover, playimghover),
			#image_scale = (2.5,1,1),
			relief = None,
			#text = ("Singleplayer"), 
			pos = (0.08,0,-0.1),
			scale=.05,
			command = parent.newGame
			)
			
		self.pause = DirectButton(
			parent = self.mainFrame,
			image = playimg,
			image_scale = (2.5,1,1),
			relief = None,
			#text = ("Singleplayer"), 
			pos = (0,2,0.0),
			scale=.08,
			command = parent.pauseGame
			)
			
		self.exit = DirectButton(
			parent = self.mainFrame,
			image = (exitimg, exitimghover, exitimghover),
			relief = None,
			#text = ("Exit"), 
			pos = (0.08,0,-0.2),
			scale=.05,
			command=parent.userExit)

		self.image = self.load2Dimage("assets/images/Loading.png")
# <<<<<<< HEAD
		self.logo.setTransparency(TransparencyAttrib.MAlpha)
		self.new.setTransparency(TransparencyAttrib.MAlpha)
		self.exit.setTransparency(TransparencyAttrib.MAlpha)

# =======
		self.pause.hide()
# >>>>>>> refs/remotes/origin/master

	#TODO: check this
	def __del__(self):
		self.new.destroy()
		self.image.destroy()
		self.exit.destroy()
		self.mainFrame.destroy()
				
	def load2Dimage(self, imagepath):
		img=OnscreenImage(image=imagepath, pos = (0, 0, 0),
			parent=base.render2d, scale=(1,1,1)
		)
		return img

	def hideNewGame(self):
		self.mainFrame.hide()
		self.new.hide()
		self.image.hide()
			
	def showNewGame(self):
		self.mainFrame.show()
		self.new.show()
		self.pause.hide()
		self.image.show()
	
	def hidePauseGame(self):
		self.mainFrame.hide()
		self.pause.hide()
		self.image.hide()
			
	def showPauseGame(self):
		self.mainFrame.show()
		self.pause.show()
		#self.image.show()