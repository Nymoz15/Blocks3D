from Objects.Game3DObjects import *
import pygame as pg



# A basic brick that is hitable, used as a base for game bricks
class HitBrick(Brick):
    
    def __init__(self, position, width, height, textures, color, maxHit):
        super().__init__(position, width, height, color)
        self.maxHit = maxHit
        self.currentHits = 0
        self.textures = textures
        self.destroy = False
        self.animationStart = 0
        self.animationTime = 0
        self.animationDirection = 0

    # Updates the current number of hits
    def update(self):
        self.pop = pg.mixer.Sound('sounds/pop.mp3')
        if self.collided:
            self.collided = False
            self.currentHits += 1
            if self.currentHits >= self.maxHit:
                self.pop.play()
                self.destroy = True
    def display(self, model_matrix, shader):
        if self.destroy:
            return
        if self.currentHits != 0:
            if self.currentHits > 3:
                index = 2
            else:
                index = self.currentHits - 1
            shader.set_using_tex(1.0)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.textures[index])
            shader.set_dif_tex(0)

        super().display(model_matrix, shader)
        shader.set_using_tex(0.0)
# Next 3 classes represent the game bricks, they initialize themselves with the number of hits they can take,
# else they use the inherited class
class OneHitBrick(HitBrick):
    def __init__(self, position, width, height, textures):
        # Naranja neón → (1.0, 0.4, 0.0)
        super().__init__(position, width, height, textures, Color(1.0, 0.4, 0.0), 2)

class TwoHitBrick(HitBrick):
    def __init__(self, position, width, height, textures):
        # Magenta eléctrico → (1.0, 0.0, 1.0)
        super().__init__(position, width, height, textures, Color(1.0, 0.0, 1.0), 3)

class ThreeHitBrick(HitBrick):
    def __init__(self, position, width, height, textures):
        # Cian neón → (0.0, 1.0, 1.0)
        super().__init__(position, width, height, textures, Color(0.0, 1.0, 1.0), 4)
