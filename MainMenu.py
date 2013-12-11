from direct.gui.DirectGui import *

class MainMenu:
  def __init__(self, parent):
    playimg = ("assets/images/PlayButton.png")
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
    self.exit = DirectButton(
                             parent = self.mainFrame,
                             image = exitimg, 
                             #text = ("Exit"), 
                             pos = (0.0,1,-0.3),
                             scale=.05,
                             command=parent.exit)

    self.image = self.load2Dimage("loading.png")
        
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
