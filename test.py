from essential import Vector
import numpy
from graphics import *

win = GraphWin("test", 1000, 800)

line = Line(Point(100,100), Point(200, 300))
line.draw(win)
line.setFill('yellow')
line.setWidth(10)

while True:
	line.move(0,0)