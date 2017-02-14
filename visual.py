from graphics import *
import numpy
from objs import *
import sys, pygame

SPEED = 5
MINUTES_ELAPSED = 0

pygame.init()

size = width, height = 1000, 800



screen = pygame.display.set_mode(size)

algorithm = Algorithm(size[0], size[1], 10, num_foods=10, FOOD_RESPAWN_RATE=0.05, FOOD_SUSTENANCE=15, ENERGY_DECAY_PER_20=0.0005, CREATURE_LIFESPAN=20000, MUTATION_CHANCE=0.1)

init_sped = sum([m.max_speed for m in algorithm.population])/len(algorithm.population)
init_eng = sum([m.max_energy for m in algorithm.population])/len(algorithm.population)
init_vis = sum([m.vision_range for m in algorithm.population])/len(algorithm.population)
init_pop = len(algorithm.population)

for i in range(int(3600*MINUTES_ELAPSED)):
	algorithm.update()

X_FACTOR = size[0]/algorithm.max_x
Y_FACTOR = size[1]/algorithm.max_y
TOTAL_FACTOR = numpy.sqrt(X_FACTOR**2 + Y_FACTOR**2)

black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0

clock = pygame.time.Clock()
while 1:
	clock.tick(60)
	pygame.display.set_caption("fps: " + str(clock.get_fps()))
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
	screen.fill(white)
	for i in range(SPEED):
		algorithm.update()
	for c in algorithm.population:
		rect_c = pygame.Rect(c.position.x-15, c.position.y-15, 30, 30)
		surf_c = pygame.Surface((30,30))
		pygame.draw.ellipse(surf_c, black, rect_c)
		screen.blit(surf_c, rect_c)
	for f in algorithm.foods:
		rect_f = pygame.Rect(f.position.x-15, f.position.y-15, 30, 30)
		surf_f = pygame.Surface((10,10))
		surf_f.fill(red)
		screen.blit(surf_f, rect_f)
	
	
	pygame.display.flip()

'''
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    #screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()'''