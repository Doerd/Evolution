from scene import *
import sound
import random
import math
import numpy

from objs import *

A = Action
SPEED = 1
MINUTES_ELAPSED = 1

class MyScene (Scene):
	def setup(self):
		self.algorithm = Algorithm(self.size.w, self.size.h, 10, num_foods=10, FOOD_RESPAWN_RATE=0.01, FOOD_SUSTENANCE=15, ENERGY_DECAY_PER_20=0.0005, CREATURE_LIFESPAN=20000, MUTATION_CHANCE=0.1)
		self.init_sped = sum([m.max_speed for m in self.algorithm.population])/len(self.algorithm.population)
		self.init_eng = sum([m.max_energy for m in self.algorithm.population])/len(self.algorithm.population)
		self.init_vis = sum([m.vision_range for m in self.algorithm.population])/len(self.algorithm.population)
		self.init_pop = len(self.algorithm.population)
		
		for i in range(int(3600*MINUTES_ELAPSED)):
			self.algorithm.update()
			
		self.X_FACTOR = self.size.w/self.algorithm.max_x
		self.Y_FACTOR = self.size.h/self.algorithm.max_y
	
	def did_change_size(self):
		pass
	
	def draw(self):
		
		for c in self.algorithm.population:
			fill('white')
			stroke_weight(2)
			stroke('white')
			if c.looking_for_mate:
				fill('#00ff16')
				stroke('#00ff16')
			ellipse(self.X_FACTOR*(c.position.x-10), self.Y_FACTOR*(c.position.y-10), self.X_FACTOR*20, self.Y_FACTOR*20)
			#current energy percent indicator
			text(str((c.current_energy/c.max_energy)*100)[:5]+"%", font_size=10, x=self.X_FACTOR*(c.position.x+10), y=self.Y_FACTOR*(c.position.y+6), alignment=9)
			
		fill('red')
		stroke('red')
		stroke_weight(3)
		for f in self.algorithm.foods:
			ellipse(self.X_FACTOR*(f.position.x-5), self.Y_FACTOR*(f.position.y-5), self.X_FACTOR*10, self.Y_FACTOR*10)
			
		
		for c in self.algorithm.population:
		#line(c.position.x, c.position.y, c.get_closest_food(self.algorithm.foods).position.x, c.get_closest_food(self.algorithm.foods).position.y)
			line(self.X_FACTOR*c.position.x, self.Y_FACTOR*c.position.y, self.X_FACTOR*(c.position.x + 20*c.heading.x), self.Y_FACTOR*(c.position.y + 20*c.heading.y))
		
		#vision range
		fill(.97, 1.0, .33, 0.2)
		#fill('yellow')
		stroke_weight(0)
		for c in self.algorithm.population[:10]:
			var = 2*self.algorithm.CREATURE_VISIBILITY*c.vision_range
			pass#ellipse(self.X_FACTOR*(c.position.x-var/2), self.Y_FACTOR*(c.position.y-var/2), self.X_FACTOR*var, self.Y_FACTOR*var)
			
		#lifespan bar
		'''
		fill(0,0,0,0)
		stroke_weight(1)
		rect(c.position.x-18, c.position.y-20, 36, 6)
		stroke_weight(0)
		fill('#0bff60')
		rect(c.position.x-17, c.position.y-19, 36*(1-(c.time_since_birth/self.algorithm.CREATURE_LIFESPAN))-2, 4)
		'''
	
		sped = sum([m.max_speed for m in self.algorithm.population])/len(self.algorithm.population)
		eng = sum([m.max_energy for m in self.algorithm.population])/len(self.algorithm.population)
		vis = sum([m.vision_range for m in self.algorithm.population])/len(self.algorithm.population)
		
		text("POPULATION \t\tcurrent: "+str(len(self.algorithm.population))+"\t\tinitial: "+str(self.init_pop), font_name='Helvetica', font_size=20.0, x=10, y=70, alignment=9)
		text("SPEED average \tcurrent: "+str(sped)[:5]+"\tinitial: "+str(self.init_sped)[:5], font_name='Helvetica', font_size=20.0, x=10, y=50, alignment=9)
		text("ENERGY average \tcurrent: "+str(eng)[:5]+"\tinitial: "+str(self.init_eng)[:5], font_name='Helvetica', font_size=20.0, x=10, y=30, alignment=9)
		text("VISION average \tcurrent: "+str(vis)[:5]+"\tinitial: "+str(self.init_vis)[:5], font_name='Helvetica', font_size=20.0, x=10, y=10, alignment=9)
		
	def update(self):
		for i in range(SPEED):
			self.algorithm.update()
		
	
	def touch_began(self, touch):
		pass
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		pass

if __name__ == '__main__':
	run(MyScene(), orientation=LANDSCAPE, show_fps=True)
