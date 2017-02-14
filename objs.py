from scene import Vector2
import numpy
from wlearn.neural import NeuralNetwork


class Algorithm():
	def __init__(self, max_x, max_y, pop_size, num_foods=10, FOOD_RESPAWN_RATE=0.01, FOOD_SUSTENANCE=5, ENERGY_DECAY_PER_20=0.001, CREATURE_LIFESPAN=10000, MUTATION_CHANCE=0.1, CREATURE_VISIBILITY=-1, MEAN_SPEED=0.5, MEAN_ENERGY=0.5):
		self.max_x = max_x
		self.max_y = max_y
		self.FOOD_RESPAWN_RATE = FOOD_RESPAWN_RATE
		self.FOOD_SUSTENANCE = FOOD_SUSTENANCE
		self.ENERGY_DECAY_PER_20 = ENERGY_DECAY_PER_20
		self.CREATURE_LIFESPAN = CREATURE_LIFESPAN
		self.MUTATION_CHANCE = MUTATION_CHANCE
		if CREATURE_VISIBILITY < 0:
			self.CREATURE_VISIBILITY = 0.4*max(self.max_x, self.max_y)
		else:
			self.CREATURE_VISIBILITY = CREATURE_VISIBILITY
		
		self.foods = []
		for i in range(0, num_foods):
			x=numpy.random.randint(0, self.max_x)
			y=numpy.random.randint(0, self.max_y)
			
			self.foods.append(Food(Vector2(x,y), self.FOOD_SUSTENANCE))
		
		#sum_means = MEAN_ENERGY + MEAN_SPEED
		#mean_speed = MEAN_SPEED/sum_means
		
		self.population = []
		#speed_vars = numpy.random.normal(mean_speed, 0.5, (1, pop_size))
		for i in range(0, pop_size):
			x=numpy.random.randint(0, self.max_x)
			y=numpy.random.randint(0, self.max_y)
			
			
			go = True
			while go:
				vars = numpy.random.randn(3)
				go = False
				for j in vars:
					if j < 0 or j > 1:
						go = True
					
			rand_speed = vars[0]
			rand_energy = vars[1]
			rand_vision = vars[2]
			
			sum = rand_energy+rand_speed+rand_vision
			
			rand_speed /= sum
			rand_energy /= sum
			rand_vision /= sum
			
			self.population.append(Creature(i, Vector2(x,y), Vector2(1,0), rand_vision, rand_speed, rand_energy, Brain([6,3,1]), self.foods, self.population, self.CREATURE_VISIBILITY))
					
	def update(self):
		if len(self.foods) == 0 or numpy.random.rand() < self.FOOD_RESPAWN_RATE:
			x=numpy.random.randint(0, self.max_x)
			y=numpy.random.randint(0, self.max_y)
			self.foods.append(Food(Vector2(x,y), self.FOOD_SUSTENANCE))
		
		if len(self.foods) > 60:
			#self.foods = self.foods[:len(self.foods)-1]
			self.foods = self.foods[2:]
		
		for c in self.population:
			count = 0
			if c.current_energy <= 0 or c.time_since_birth >= self.CREATURE_LIFESPAN+numpy.random.randint(-200,200):
				self.population.remove(c)
				for j in range(count, len(self.population)):
					if self.population[j].mate > -1:
						self.population[j].mate -= 1
					self.population[j].id -= 1
					
			count += 1
		count=0
		for c in self.population:
			c.id = count
			count += 1
			
			if abs(c.position.x-self.max_x/2) > self.max_x/2:
				c.heading = Vector2(-c.heading.x, c.heading.y)
				#c.position.x += -10*numpy.sign(c.position.x-self.max_x)
				c.position = Vector2((numpy.random.rand()*0.8+0.1)*self.max_x, (numpy.random.rand()*0.8+0.1)*self.max_y)
			if abs(c.position.y-self.max_y/2) > self.max_y/2:
				c.heading = Vector2(c.heading.x, -c.heading.y)
				#c.position.y += -10*numpy.sign(c.position.y-self.max_y)
				c.position = Vector2((numpy.random.rand()*0.8+0.1)*self.max_x, (numpy.random.rand()*0.8+0.1)*self.max_y)
			
			#UPDATING YAY!!!!!
			c.update()
			
			#takes away energy every 20 frames
			if numpy.random.rand()>0.95:
				c.current_energy -= self.ENERGY_DECAY_PER_20
				
			if c.mate >= 0:
				if c.timer == 0 and self.population[c.mate].timer == 0:
					if abs(c.position-self.population[c.mate].position)<30:
						self.population.append(self.child(c, self.population[c.mate]))
						c.timer += 300
						self.population[c.mate].timer += 300
						
						c.looking_for_mate = False
						self.population[c.mate].looking_for_mate = False
						
						c.current_energy /= 2
						self.population[c.mate].current_energy /= 2
						
						self.population[c.mate].mate = -1
						c.mate = -1		
		
			if c.timer > 0:
				c.timer -= 1
			
	def next_generation(self):
		pass
		
	def child(self, creature1, creature2):
		child = self.crossover(creature1, creature2)
		#print("CREATURE1 VIS: ", creature1.vision_range)
		#print("CREATURE2 VIS: ", creature2.vision_range)
		#print("CHILD VIS: ", child.vision_range)
		self.mutate(child)
		return child
		
	def crossover(self, creature1, creature2):
		if numpy.random.rand() > 0.5:
			speed = creature1.max_speed
		else:
			speed = creature2.max_speed
		
		if numpy.random.rand() > 0.5:
			energy = creature1.max_energy
		else:
			energy = creature2.max_energy
		
		if numpy.random.rand() > 0.5:
			vision = creature1.vision_range
		else:
			vision = creature2.vision_range
		
		sum = speed+energy+vision
		
		speed /= sum
		energy /= sum
		vision /= sum		
		
		if numpy.random.rand() > 0.5:
			syn0 = creature1.brain.syn[0]
		else:
			syn0 = creature2.brain.syn[0]
			
		if numpy.random.rand() > 0.5:
			syn1 = creature1.brain.syn[1]
		else:
			syn1 = creature2.brain.syn[1]
			
		brain = NeuralNetwork([4,3,1])
		brain.syn[0] = syn0
		brain.syn[1] = syn1
		
		vec_difference = creature2.position-creature1.position
		midpoint = creature1.position + vec_difference/2
		
		return Creature(len(self.population)-1, midpoint, Vector2(1,0), vision, speed, energy, brain, self.foods, self.population, self.CREATURE_VISIBILITY)
		
	def mutate(self, creature):
		if numpy.random.rand() < self.MUTATION_CHANCE:
			creature.max_speed *= 0.9 + numpy.random.rand()/5
		if numpy.random.rand() < self.MUTATION_CHANCE:
			creature.max_energy *= 0.9 + numpy.random.rand()/5
		if numpy.random.rand() < self.MUTATION_CHANCE:
			creature.vision_range *= 0.9 + numpy.random.rand()/5

		#creature.brain.mutate(self.MUTATION_CHANCE)
		for sy in creature.brain.syn:
			for row in sy:
				for entry in row:
					if numpy.random.rand() < self.MUTATION_CHANCE:
						entry *= 0.9 + numpy.random.rand()/5
						
		creature.normalize_attributes()
		
class Creature():
	def __init__(self, id, position, heading, max_speed, max_energy, vision_range, brain, ALL_FOODS, ALL_POPULATION, VISIBILITY, time_since_birth=0, looking_for_mate=False, mate=-1, timer=0):
		self.current_energy=max_energy/4
		self.ALL_FOODS = ALL_FOODS
		self.ALL_POPULATION = ALL_POPULATION
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
		
		self.time_since_birth = time_since_birth
		
		self.heading = heading
		self.position = position
		
		self.timer = timer
		
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
		
		if abs(self.vision_range+self.max_energy+self.max_speed-1)>0.05:
			print("ah!")
		
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
				#if self.timer == 0:
				self.turn_to_mate()
					
		if go_to_food:
			if True:#len(self.visible_foods) > 0:
				#self.turn_to_food(self.visible_foods)
				self.turn()
			else:
				self.turn_in_circles()
			
		#increases energy when creature eats a food
		for f in self.ALL_FOODS:
			if abs(f.position-self.position)<20:
				self.current_energy += 0.01*f.sustenance
				self.ALL_FOODS.remove(f)
				
		
		#updates position	
		self.position += 2*numpy.sqrt(self.max_speed)*self.heading
	
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
		food = self.get_closest_food(self.ALL_FOODS)
		food_vec = food.position-self.position
		food_angle = numpy.arctan2(food_vec.y, food_vec.x)
		food_vec = Vector2(numpy.cos(food_angle), numpy.sin(food_angle))
		
		creature = self.ALL_POPULATION[self.nearest_creature()]
		creature_vec = creature.position-self.position
		creature_angle = numpy.arctan2(creature_vec.y, creature_vec.x)
		creature_vec = Vector2(numpy.cos(creature_angle), numpy.sin(creature_angle))
		
		#print(food_vec)
		
		out = self.brain.forward([food_vec.x, food_vec.y, creature_vec.x, creature_vec.y, self.heading.x, self.heading.y])
		
		self.mean_outputs[0] += out
		self.mean_outputs[1] += 1
		
		direction = numpy.sign(out-self.mean_outputs[0]/self.mean_outputs[1])
		
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
		
	def get_closest_food(self, foods):
		try:
			food = foods[0]
			
			for f in foods:
				if abs(self.position-f.position)<abs(self.position-food.position):
					food = f
			return food
		except IndexError:
			pass
			
	def turn_to_food(self, foods):

		food = self.get_closest_food(foods)
		
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
		
class Brain(NeuralNetwork):
	def encode(self):
		pass
	def mutate(self, chance):
		pass
		'''
		for sy in self.syn:
			for row in sy:
				for entry in row:
					if numpy.random.rand() < chance:
						entry *= 0.9 + numpy.random.rand()/5
						'''
		
class Food():
	def __init__(self, position, sustenance):
		self.position = position
		self.sustenance = sustenance

