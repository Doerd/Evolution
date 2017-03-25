from Brain import *
from Food import *
from Object import *

from essential import Vector2
import numpy

class Creature(Object):
	def __init__(self, id, position, heading, max_speed, max_energy, vision_range, brain, mouth, ALL_FOODS, ALL_POPULATION, ALL_SPIKES, VISIBILITY, time_since_birth=0, looking_for_mate=False, mate=-1, mating_timer=0, is_favored_timer=0, damaged_timer=0):
		self.current_energy=max_energy/4
		self.ALL_FOODS = ALL_FOODS
		self.ALL_POPULATION = ALL_POPULATION
		self.ALL_SPIKES = ALL_SPIKES
		self.VISIBILITY = VISIBILITY
		
		self.visible_foods = []
		self.visible_creatures = []
		
		self.id = id	
		self.looking_for_mate = looking_for_mate
		self.mate = mate
					
		self.max_speed = max_speed
		self.max_energy = max_energy
		self.vision_range = vision_range
		self.brain = brain
		self.mouth = mouth
		
		self.time_since_birth = time_since_birth
		
		self.heading = heading
		self.position = position
		
		self.mating_timer = mating_timer
		self.is_favored_timer = is_favored_timer
		self.damaged_timer = damaged_timer
		
		self.mean_outputs = [0, 0]
	
	def set_visibles(self):
		self.visible_foods = []
		self.visible_creatures = []
		for f in self.ALL_FOODS:
			if abs(f.position-self.position) < self.VISIBILITY*self.vision_range:
				self.visible_foods.append(f)
		for c in self.ALL_POPULATION:
			if abs(c.position-self.position) < self.VISIBILITY*self.vision_range:
				self.visible_creatures.append(c)
	
	def normalize_attributes(self):
		sum_attr = self.max_speed + self.max_energy + self.vision_range
		self.max_speed /= sum_attr
		self.max_energy /= sum_attr
		self.vision_range /= sum_attr
		
	def update(self):
		#age
		self.time_since_birth += 1
		
		self.set_visibles()
			
		if self.current_energy > self.max_energy:
			self.current_energy = self.max_energy
			
		if self.current_energy > 0.8*self.max_energy:
			self.looking_for_mate = True
		else:
			self.looking_for_mate = False
			
		if not self.looking_for_mate:
			if self.mate > -1:
				self.ALL_POPULATION[self.mate].mate = -1
			self.mate = -1
			
		go_to_food = True
		if self.looking_for_mate:
			#if there's another mate around, then go to it, otherwise just get food
			for c in self.visible_creatures:
				if c != self and c.looking_for_mate and c.mate < 0:
					go_to_food = False
					#ALL population vs. self.visible_creatures
					self.mate = self.get_closest_mate(self.ALL_POPULATION)
					self.ALL_POPULATION[self.mate].mate = self.id
					break
		if self.mate > -1:
			if not self.ALL_POPULATION[self.mate].looking_for_mate:
				self.mate = -1
			else:
				go_to_food = False
				self.ALL_POPULATION[self.mate].mate = self.id
				#if self.mating_timer == 0:
				self.turn_to_mate()
					
		if go_to_food:
			if True:#len(self.visible_foods) > 0:
				#self.turn_to_food(self.visible_foods)
				self.turn()
			else:
				self.turn_in_circles()
					
		#updates position	
		self.position += 2*numpy.sqrt(self.max_speed)*self.heading
	
	def nearest_food(self, foods):
		try:
			food = foods[0]		
			for f in foods:
				if abs(self.position-f.position)<abs(self.position-food.position):
					food = f
			return food
		except IndexError:
			pass
	
	def nearest_spike(self, spikes):
		try:
			spike = spikes[0]
			for s in spikes:
				if abs(self.position-s.position)<abs(self.position-spike.position):
					spike = s
			return spike
		except IndexError:
			pass
	
	def nearest_creature(self):
		index = -1
		for c in self.ALL_POPULATION:
			if index == -1:
				dist = 99999
			else:
				dist = abs(c.position-self.ALL_POPULATION[index].position)
			if c != self and abs(c.position-self.position) < dist:
				index = self.ALL_POPULATION.index(c)
		
		return index
			
	def turn(self):
		food = self.nearest_food(self.ALL_FOODS)
		food_vec = food.position-self.position
		food_vec /= abs(food_vec)
		
		creature = self.ALL_POPULATION[self.nearest_creature()]
		creature_vec = creature.position-self.position
		creature_vec /= abs(creature_vec)
		
		spike = self.nearest_spike(self.ALL_SPIKES)
		#spike_angle = numpy.arctan2(spike.position.y, spike.position.x)/(2*numpy.pi)
		#spike_distance = abs(spike.position-self.position)/???
		spike_vec = spike.position-self.position
		spike_vec /= abs(spike_vec)
		
		
		out_array = [food_vec.x, food_vec.y, self.heading.x, self.heading.y, creature_vec.x, creature_vec.y, spike_vec.x, spike_vec.y]#, food.network_value, creature.current_energy/creature.max_energy, creature.mouth]
		
		if self.time_since_birth % 1000 == 0:
			pass#print(out_array)
		
		out = self.brain.forward(out_array)
		
		self.mean_outputs[0] += out[0]
		self.mean_outputs[1] += 1
		
		self.out = out[0]
		
		#direction = numpy.sign(out-0.5)
		direction = numpy.sign(out[0])#-self.mean_outputs[0]/self.mean_outputs[1])
		#self.mouth = out[1]
		
		heading_angle = numpy.arctan2(self.heading.y, self.heading.x)	
		heading_angle += 0.05*direction
		self.heading = Vector2(numpy.cos(heading_angle), numpy.sin(heading_angle))	
		
	def get_closest_mate(self, pop):
		mates = []
		#length of mates is always guaranteed to be at least one, because this method is only called
		#if there is another matable creature
		for m in pop:
			if m != self and m.looking_for_mate:
				mates.append(m.id)

		#print(mates)
		closest_mate = mates[0]
		for m in mates:
			dist=abs(self.ALL_POPULATION[closest_mate].position-self.position)
			if abs(self.position-self.ALL_POPULATION[m].position)<dist:
				closest_mate = m
		#print(closest_mate)
		return closest_mate
			
	def turn_to_food(self, foods):

		food = self.nearest_food(foods)
		
		if abs(food.position-self.position)<30:
			pass#self.max_speed=0
	
		food_vec = self.position-food.position	
		food_angle = numpy.arctan2(food_vec.y, food_vec.x)
		
		if food_angle<0:
			food_angle+=2*numpy.pi
		if heading_angle<0:
			heading_angle+=2*numpy.pi
		
		diff = food_angle-heading_angle
		direction = -numpy.sign(diff)
		
		if abs(diff) > numpy.pi:
			direction *= -1
		
		
		heading_angle = numpy.arctan2(self.heading.y, self.heading.x)	
		heading_angle += 0.05*direction
		self.heading = Vector2(numpy.cos(heading_angle), numpy.sin(heading_angle))	
		
	def turn_to_mate(self):
		mate_vec = self.position-self.ALL_POPULATION[self.mate].position
		mate_angle = numpy.arctan2(mate_vec.y, mate_vec.x)
		
		heading_angle = numpy.arctan2(self.heading.y, self.heading.x)
		
		if mate_angle<0:
			mate_angle+=2*numpy.pi
		if heading_angle<0:
			heading_angle+=2*numpy.pi
		
		diff = mate_angle-heading_angle
		direction = -numpy.sign(diff)
		
		if abs(diff) > numpy.pi:
			direction *= -1
			
		heading_angle += 0.05*direction
		self.heading = Vector2(numpy.cos(heading_angle), numpy.sin(heading_angle))

	def turn_in_circles(self):
		heading_angle = numpy.arctan2(self.heading.y, self.heading.x)
		heading_angle += 0.05
		self.heading = Vector2(numpy.cos(heading_angle), numpy.sin(heading_angle))
				

