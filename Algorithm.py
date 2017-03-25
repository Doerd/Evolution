from essential import Vector2
import numpy

from Creature import *
from Brain import *
from Food import *
from Spike import *

class Algorithm():
	def __init__(self, max_x, max_y, pop_size, MAX_FOODS=10, FOOD_RESPAWN_RATE=0.01, AVG_FOOD_SUSTENANCE=5, FOOD_SPREAD=0.2, ENERGY_DECAY_PER_20=0.001, CREATURE_LIFESPAN=10000, MUTATION_CHANCE=0.1, CREATURE_VISIBILITY=-1, MEAN_SPEED=0.5, MEAN_ENERGY=0.5):
		self.max_x = max_x
		self.max_y = max_y
		self.MAX_FOODS = MAX_FOODS
		self.FOOD_RESPAWN_RATE = FOOD_RESPAWN_RATE
		self.AVG_FOOD_SUSTENANCE = AVG_FOOD_SUSTENANCE
		self.ENERGY_DECAY_PER_20 = ENERGY_DECAY_PER_20
		self.CREATURE_LIFESPAN = CREATURE_LIFESPAN
		self.MUTATION_CHANCE = MUTATION_CHANCE
		self.FOOD_SPREAD = FOOD_SPREAD
		self.time = 0 
		
		if CREATURE_VISIBILITY < 0:
			self.CREATURE_VISIBILITY = 0.3*max(self.max_x, self.max_y)
		else:
			self.CREATURE_VISIBILITY = CREATURE_VISIBILITY
		
		self.spikes = []
		for i in range(0, 12):
			x=numpy.random.randint(0, self.max_x)
			y=numpy.random.randint(0, self.max_y)
			
			self.spikes.append(Spike(Vector2(x,y), diameter=32, energy_loss=0.3))
		
		self.foods = []
		for i in range(0, 10):
			x=numpy.random.randint(0, self.max_x)
			y=numpy.random.randint(0, self.max_y)
			
			self.append_food(x,y)
		
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
			
			self.INNOVATION_NUMBER = 0
			genome = []
			layer_1_size = 8
			layer_2_size = 1
			for j in range(layer_1_size):
				for i in range(layer_2_size):
					genome.append(BrainGene(j, i+layer_1_size, numpy.random.randn(), self.INNOVATION_NUMBER))
					self.INNOVATION_NUMBER += 1
			
			for q in range(layer_2_size):
				genome.append(BrainGene(q+layer_1_size, layer_1_size+layer_2_size, numpy.random.randn(), self.INNOVATION_NUMBER))
				self.INNOVATION_NUMBER += 1
				
			brain = Brain(genome, list(range(layer_1_size)), [layer_1_size+layer_2_size])
			
			self.population.append(Creature(i, Vector2(x,y), Vector2(1,0), rand_vision, rand_speed, rand_energy, brain, 0, self.foods, self.population, self.spikes, self.CREATURE_VISIBILITY))
	
	def append_food(self, x, y):
		sust = self.AVG_FOOD_SUSTENANCE+(numpy.random.rand()-0.5)*2*self.FOOD_SPREAD*self.AVG_FOOD_SUSTENANCE
		self.foods.append(Food(Vector2(x,y), sust, sust/(self.AVG_FOOD_SUSTENANCE*(1+self.FOOD_SPREAD))))
					
	def update(self):
		self.time += 1
		if len(self.foods) < 3 or numpy.random.rand() < self.FOOD_RESPAWN_RATE:
			x=numpy.random.randint(0, self.max_x)
			y=numpy.random.randint(0, self.max_y)
			
			self.append_food(x,y)
		
		if len(self.foods) > self.MAX_FOODS:
			#self.foods = self.foods[:len(self.foods)-1]
			self.foods = self.foods[1:]
		
		for c in self.population:
			count = 0
			if c.current_energy <= 0 or c.time_since_birth >= self.CREATURE_LIFESPAN and numpy.random.rand() < 0.0001:
				sust = self.AVG_FOOD_SUSTENANCE*4
				self.foods.append(Food(Vector2(c.position.x, c.position.y), sust, sust/(self.AVG_FOOD_SUSTENANCE*(1+self.FOOD_SPREAD))))
				self.population.remove(c)				
				for j in range(count, len(self.population)):
					if self.population[j].mate > -1:
						self.population[j].mate -= 1
					self.population[j].id -= 1
					
			count += 1
		count=0
		
		#increases energy when creature eats a food
		for c in self.population:
			for f in self.foods:
				if abs(f.position-c.position)<20:
					c.current_energy += 0.01*f.sustenance
					self.foods.remove(f)
				
		for c in self.population:
			c.id = count
			count += 1
			
			if c.position.x < 0:
				c.position.x  = self.max_x - 10
			if c.position.x > self.max_x:
				c.position.x = 10
			if c.position.y < 0:
				c.position.y  = self.max_y - 10
			if c.position.y > self.max_y:
				c.position.y = 10
			
			for s in self.spikes:
				if c.damaged_timer <= 0:
					if abs(c.position-s.position) < s.diameter/2:
						c.current_energy *= 1-s.energy_loss
						c.damaged_timer += 250
				else:
					c.damaged_timer -= 1
			
			#UPDATING YAY!!!!!
			c.update()
			
			#takes away energy every 20 frames
			if c.is_favored_timer <= 0:
				if numpy.random.rand()>0.95:
					c.current_energy -= self.ENERGY_DECAY_PER_20
			else:
				c.is_favored_timer -= 1
				
			if c.mate >= 0:
				if c.mating_timer == 0 and self.population[c.mate].mating_timer == 0:
					if abs(c.position-self.population[c.mate].position)<30:
						self.population.append(self.child(c, self.population[c.mate]))
						c.mating_timer += 300
						self.population[c.mate].mating_timer += 300
						
			if c.mating_timer > 0:
				c.mating_timer -= 1
		
	def child(self, creature1, creature2):
		
		creature1.looking_for_mate = False
		creature2.looking_for_mate = False
		
		creature1.current_energy /= 2
		creature2.current_energy /= 2
		
		creature2.mate = -1
		creature1.mate = -1
		
		child = self.crossover(creature1, creature2)
		
		if self.mutate(child):
			child.is_favored_timer += int(1200*(min(1, 25/len(child.brain.genome))))
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
		
		child_brain = self.brain_crossover(creature1.brain, creature2.brain)
		
		vec_difference = creature2.position-creature1.position
		midpoint = creature1.position + vec_difference/2
		
		return Creature(len(self.population)-1, midpoint, Vector2(1,0), vision, speed, energy, child_brain, 0, self.foods, self.population, self.spikes, self.CREATURE_VISIBILITY)
		
	def mutate(self, creature):
		if numpy.random.rand() < self.MUTATION_CHANCE:
			creature.max_speed *= 0.9 + numpy.random.rand()/5
		if numpy.random.rand() < self.MUTATION_CHANCE:
			creature.max_energy *= 0.9 + numpy.random.rand()/5
		if numpy.random.rand() < self.MUTATION_CHANCE:
			creature.vision_range *= 0.9 + numpy.random.rand()/5

		self.brain_mutate(creature.brain, self.MUTATION_CHANCE)
						
		creature.normalize_attributes()
		
	def brain_crossover(self, b1, b2):
		child_genes = []
		innovations_b1 = [g.innovation_number for g in b1.genome]
		innovations_b2 = [g.innovation_number for g in b2.genome]
		max_innovation = max(max(innovations_b1), max(innovations_b2))
		
		for i in range(max_innovation+1):
			in_b1 = i in innovations_b1
			in_b2 = i in innovations_b2
			if in_b1 and in_b2:
				if numpy.random.rand() > 0.5:
					child_genes.append(b1.genome[innovations_b1.index(i)])
				else:
					child_genes.append(b2.genome[innovations_b2.index(i)])
			elif in_b1:
				child_genes.append(b1.genome[innovations_b1.index(i)])
			# ---------POTENTIAL PROBLEM AQUÍ-----------------
			elif in_b2:
				child_genes.append(b2.genome[innovations_b2.index(i)])
				
		for gene in child_genes:
			if numpy.random.rand() > 0.75 and not gene.enabled:
				gene.enabled = not gene.enabled
		
		return Brain(child_genes, b1.inputs, b1.outputs)			
				
	def brain_mutate(self, brain, chance):
		did_mutate = False
		if numpy.random.rand() < chance/max(len(brain.genome)/20,1):
			if numpy.random.rand() < 0.5:
				gene = numpy.random.choice(brain.genome)
				#adding a new neuron
				gene.enabled = False
				brain.neuron_count += 1
				self.INNOVATION_NUMBER += 1
				brain.genome.append(BrainGene(gene.input_neuron, brain.neuron_count, numpy.random.randn(), self.INNOVATION_NUMBER))
				self.INNOVATION_NUMBER += 1
				brain.genome.append(BrainGene(brain.neuron_count, gene.output_neuron, numpy.random.randn(), self.INNOVATION_NUMBER))
				
				did_mutate = True
			
			else:
				gene = numpy.random.choice(brain.genome)
				#adding a connection
				input_n = gene.input_neuron
				output_n = 0
				
				#This fat line makes sure the output neuron isn't one of the inputs and that the
				#connection doesn't already exist
				count = 0
				liszt = [1,11,1,1,1,1,1,1,1,1]	
				#print(brain.genome)		
				while (output_n in brain.inputs or len(liszt) > 0 or output_n == input_n) and count < 300:
					liszt = []
					for g in brain.genome:
						if g.input_neuron == gene.input_neuron and g.output_neuron == output_n:
							liszt.append(1)
					#print(liszt)
					output_n = numpy.random.randint(brain.neuron_count)
					count += 1
				
				if count < 98:	
					self.INNOVATION_NUMBER += 1
					brain.genome.append(BrainGene(input_n, output_n, numpy.random.randn(), self.INNOVATION_NUMBER))
					did_mutate = True
				else:
					did_mutate = False
			
		for gene in brain.genome:
			if numpy.random.rand() < chance:
				gene.weight *= 0.9+numpy.random.rand()/5
		
		#print("Mutation occurred: ", did_mutate)
		
		return did_mutate
		
	def _____UNUSED_____brain_crossover(self, parent1_brain, parent2_brain):
		parent1_reshaped = []
		parent2_reshaped = []
		
		for syn in parent1_brain.syn:
			parent1_reshaped.append(numpy.reshape(syn, len(syn)*len(syn[0])))
		
		for syn in parent2_brain.syn:
			parent2_reshaped.append(numpy.reshape(syn, len(syn)*len(syn[0])))
		
		child_reshaped = []
		
		for sy in zip(parent1_reshaped, parent2_reshaped):
			temp_syn = []
			for var in range(len(sy[0])):
				if numpy.random.rand() > 0.5:
					temp_syn.append(sy[0][var])
				else:
					temp_syn.append(sy[1][var])
			child_reshaped.append(temp_syn)
		
		child_syn = []
		for i in range(len(child_reshaped)):	
			child_syn.append(numpy.reshape(child_reshaped[i], numpy.shape(parent1_brain.syn[i])))
		
		return child_syn

	def save_array(self):
		creatures = []
		foods = []
		
		for c in self.population:
			creature = []
			creature.append([c.current_energy, c.id, int(c.looking_for_mate), c.mate, c.max_speed, c.max_energy, c.vision_range, c.mouth, c.time_since_birth, c.heading.x, c.heading.y, c.position.x, c.position.y, c.mating_timer, c.is_favored_timer])
			
			creature.append([])
			creature[1].append([c.brain.inputs, c.brain.outputs, c.brain.neuron_count])
			for g in c.brain.genome:
				creature[1].append([int(g.enabled), g.innovation_number, g.input_neuron, g.output_neuron, g.weight])
			
			creatures.append(creature)
		
		for f in self.foods:
			foods.append([f.position.x, f.position.y, f.sustenance, f.network_value])
		
		return creatures, foods
		
