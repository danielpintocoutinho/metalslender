#!/usr/bin/ppython
import panda3d
from panda3d.core import TransparencyAttrib
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task

class HUD(DirectObject):
	#TODO: Preload all images
	#TODO: Find out how many sprites are available
	#TODO: Parameters to againrol screen resolution?
	def __init__(self,player):
		self.player = player

		self.heartbasis = 'assets/images/heartbeat2-%d.png'
		self.heartframe = 0
		self.heartimage = OnscreenImage(self.heartbasis % (1,), scale=(0.1,1,0.1), pos=(0,1,-0.8))
		self.text = OnscreenText('', pos=(0, -0.975), scale=0.05, fg=(0,1,0,1),	bg=(0,0,0,1))

		taskMgr.add(self.update, 'hud')

	def update(self, task):
		if self.player.breath == -1:
			self.text.setFg((1,1,1,1))
			self.text.setText('0 BPM')
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			return task.done
		else:
			self.heartframe = int(8 * self.player.heartaccum / 60) % 8
			self.heartimage.setImage(self.heartbasis % (self.heartframe + 1,))
			self.heartimage.setTransparency(TransparencyAttrib.MAlpha)

			heartampl = self.player.heartmax - self.player.heartmin
			if self.player.heartbpm < self.player.heartmax:
				s = float(self.player.heartbpm - self.player.heartmin) / heartampl
				self.text.setFg((s,1,0,1))
			else:
				s = float(self.player.heartbpm - self.player.heartmax) / heartampl
				self.text.setFg((1,1-s,0,1))

			self.text.setText('%d BPM' % (self.player.heartbpm,))
			return task.again
