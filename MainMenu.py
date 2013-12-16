from direct.gui.DirectGui import *
from panda3d.core import TransparencyAttrib

class MainMenu:
  def __init__(self, parent):
    logoimg = ("assets/images/metalslender.png")
    playimg = ("assets/images/PlayButton.png")
    playimghover = ("assets/images/PlayButtonHover.png")
    exitimg = ("assets/images/ExitButton.png")
    exitimghover = ("assets/images/ExitButtonHover.png")


    self.mainFrame = DirectFrame(
                                 frameColor=(1,0,0,0.0),
                                 #(left, right, bottom, top)
                                 frameSize=(-2,-0.6,0.9,-0.2 )

                                 )
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
    self.exit = DirectButton(
                             parent = self.mainFrame,
                             image = (exitimg, exitimghover, exitimghover),
                             relief = None,
                             #text = ("Exit"), 
                             pos = (0.08,0,-0.2),
                             scale=.05,
                             command=parent.userExit)

    self.image = self.load2Dimage("assets/images/Loading.png")
    self.logo.setTransparency(TransparencyAttrib.MAlpha)
    self.new.setTransparency(TransparencyAttrib.MAlpha)
    self.exit.setTransparency(TransparencyAttrib.MAlpha)

        
  def load2Dimage(self, imagepath):
    img=OnscreenImage(image=imagepath, pos = (0, 0, 0),
      parent=base.render2d, scale=(1,1,1)
    )
    return img


  def hide(self):
    self.mainFrame.hide()
    self.image.hide()
      
  def show(self):
    self.mainFrame.show()

  
  #TODO: check this
  def __del__(self):
    self.new.destroy()
    self.image.destroy()
    self.exit.destroy()
    self.mainFrame.destroy()
