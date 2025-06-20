from Objects.Base3DObjects import *

# Plays the intro animation when starting the game, it is defaulted at 20 seconds
class Intro():
    def __init__(self):
        self.animationEnd = 2.0
        self.animationTime = 0.0
        self.animationFinished = False

    def bezierMotionAnimation(self, delta_time, pointArray):
        self.animationTime += delta_time
        # Do not need currtime - starttime and endtime - startime because for this class 
        # the animation will always start at time 0
        t = min(self.animationTime / self.animationEnd, 1.0)

        tempArray = pointArray[:]  # Avoid modifying the original array
        while(len(tempArray) > 1):
            tmp = []
            for i in range(len(tempArray) - 1):
                tmp.append(self.lerp(tempArray[i], tempArray[i + 1], t))  # Corrected here
            tempArray = tmp

        if self.animationTime >= self.animationEnd:
            self.animationFinished = True

        return tempArray[0]

    def lerp(self, p1, p2, t):
        return (p1 * (1 - t)) + (p2 * t)

# The Motion class can be used to do bezier motion where you can put in the time you want the anomation to be
# You can resuse the Motion class by reseting the animationTime to zero and turn animationFinished back to True
class Motion(Intro):
    def __init__(self, animationDuration):
        super().__init__()
        self.animationEnd = animationDuration
