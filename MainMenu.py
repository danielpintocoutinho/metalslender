from direct.gui.DirectGui import *

class MainMenu:
  def __init__(self, parent):
    playimg = ("assets/images/PlayButton.png")
    resumeimg = ("assets/images/PlayButton.png")
    exitimg = ("assets/images/ExitButton.png")

    self.mainFrame = DirectFrame(
                                 frameColor=(1,0,0,0.0),
                                 #(left, right, bottom, top)
                                 frameSize=(-2,-0.6,0.9,-0.2 )

                                 )
    self.new = DirectButton(
                            parent = self.mainFrame,
                            image = playimg,
                            image_scale = (2.5,1,1),
                            relief = None,
                            #text = ("Singleplayer"), 
                            pos = (0,0,0.0),
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
                             image = exitimg, 
                             #text = ("Exit"), 
                             pos = (0.0,1,-0.3),
                             scale=.05,
                             command=parent.userExit)

    self.image = self.load2Dimage("assets/images/Loading.png")
    self.pause.hide()
        
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

  
  #TODO: check this
  def __del__(self):
    self.new.destroy()
    self.image.destroy()
    self.exit.destroy()
    self.mainFrame.destroy()
