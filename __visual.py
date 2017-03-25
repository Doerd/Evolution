import sys
import time
from matplotlib import pyplot

from Algorithm import *
from Brain import *

load_population = False
save_population = False

SPEED = 1
MINUTES_ELAPSED = 90
print("we starting")

if load_population:
	alg_c = numpy.load("alg_constants.npy")
	decay_c = numpy.load("decay_constants.npy")
	FOOD_RATE_TARGET = decay_c[0]
	ENERGY_RATE_TARGET = decay_c[1]
	INVERSE_DECAY = decay_c[2]
	food_decay = decay_c[3]
	energy_decay = decay_c[4]
	#[FOOD_RATE_TARGET, ENERGY_RATE_TARGET, INVERSE_DECAY, food_decay, energy_decay]
	alg = Algorithm(int(alg_c[0]), int(alg_c[1]), int(alg_c[2]), int(alg_c[3]), alg_c[4], alg_c[5], alg_c[6], alg_c[7], alg_c[8], alg_c[9], alg_c[10])
	#[alg.max_x, alg.max_y, alg.pop_size, alg.MAX_FOODS, alg.FOOD_RESPAWN_RATE, alg.AVG_FOOD_SUSTENANCE, alg.FOOD_SPREAD, alg.ENERGY_DECAY_PER_20, alg.CREATURE_LIFESPAN, alg.MUTATION_CHANCE, alg.CREATURE_VISIBILITY]
	
	brain_file = numpy.load('brain_file.npz')
	print(brain_file['inputs'])
	inputs = brain_file['inputs']
	outputs = brain_file['outputs']
	neuron_counts = brain_file['neuron_counts']
	genomes = brain_file['genomes']
	
	for i in range(len(alg.population)):
		genome = []
		for g in genomes[i]:
			if not (g[0] == 0 and g[1] == 0 and g[2] == 0 and g[3] == 0):
				genome.append(BrainGene(int(g[0]), int(g[1]), g[2], int(g[3]), g[4]))
		alg.population[i].brain = Brain(genome, inputs[i], outputs[i], neuron_counts[i])
		
else:
	FOOD_RATE_TARGET = 0.003
	ENERGY_RATE_TARGET = 0.001
	width = 1024*1
	height = 768*1
	INVERSE_DECAY = 5000
	food_decay = 0.998
	energy_decay = 0.998
	alg = Algorithm(max_x=width, max_y=height, pop_size=14, MAX_FOODS=70, FOOD_RESPAWN_RATE=0.016, AVG_FOOD_SUSTENANCE=15, FOOD_SPREAD=0.4, ENERGY_DECAY_PER_20=1/INVERSE_DECAY, CREATURE_LIFESPAN=5000, MUTATION_CHANCE=0.1)	
	
init_sped = sum([m.max_speed for m in alg.population])/len(alg.population)
init_eng = sum([m.max_energy for m in alg.population])/len(alg.population)
init_vis = sum([m.vision_range for m in alg.population])/len(alg.population)
init_pop = len(alg.population)

x_plot = []
y_plot = []

def eugenics(portion_moved_to_better_life):
	for i in range(int(portion_moved_to_better_life*len(alg.population))):
		alg.population[i].current_energy = 0

def cows(portion_to_have_children):
	var = int(portion_to_have_children*len(alg.population))
	for i in range(var):
		rand = numpy.random.randint(len(alg.population))
		while rand != i:
			 rand = numpy.random.randint(len(alg.population))
		alg.population.append(alg.child(alg.population[i], alg.population[rand]))
	
	for i in range(len(alg.population)-var, len(alg.population)):
		alg.population[i].position = Vector2(numpy.random.randint(alg.max_x), numpy.random.randint(alg.max_y))

def xinfusion(portion):
	alg.FOOD_RESPAWN_RATE *= portion
	INVERSE_DECAY *= portion

num_prints = MINUTES_ELAPSED*3 
count = 0
t0 = time.time()
for i in range(int(3600*MINUTES_ELAPSED)):
	if i % 1200 == 0:
		print(len(alg.population), ", ", str(alg.FOOD_RESPAWN_RATE)[:6], ", ", int(i/1200), "/", num_prints, sep="")
		count += 1
		
		x_plot.append(int(i/1200))
		y_plot.append(len(alg.population))
		
		alg.FOOD_RESPAWN_RATE *= food_decay
		if alg.FOOD_RESPAWN_RATE < FOOD_RATE_TARGET:
			alg.FOOD_RESPAWN_RATE = FOOD_RATE_TARGET
		
		INVERSE_DECAY *= energy_decay
		alg.ENERGY_DECAY_PER_20 = 1/INVERSE_DECAY
		if alg.ENERGY_DECAY_PER_20 > ENERGY_RATE_TARGET:
			alg.ENERGY_DECAY_PER_20 = ENERGY_RATE_TARGET
			
		if len(alg.population) < 2:
			sys.exit(0)
	
	try:
		if len(alg.population) < 10:
			print("reproduction and infusion enabled")
			cows(0.8)
			portion = 1.01
			alg.FOOD_RESPAWN_RATE *= portion
			INVERSE_DECAY *= portion
		else:
			alg.update()
	except KeyboardInterrupt:
		cont = input("Program was stopped....Continue?   ")
		if cont=='eugenics':
			eugenics(0.5)
		elif cont=='reproduce':
			cows(0.5)
		elif cont=='infusion':
			portion = 1.03
			alg.FOOD_RESPAWN_RATE *= portion
			INVERSE_DECAY *= portion
			alg.ENERGY_DECAY_PER_20 = 1/INVERSE_DECAY
		elif cont=='defusion':
			portion = 0.97
			alg.FOOD_RESPAWN_RATE *= portion
			INVERSE_DECAY *= portion
			alg.ENERGY_DECAY_PER_20 = 1/INVERSE_DECAY
		elif len(cont) < 5:
			break
			
if save_population:	
	inputs = []
	outputs = []
	neuron_counts = []
	genomes = []
	max_brain_length = max([len(c.brain.genome) for c in alg.population]) 
	for c in alg.population:
		set = c.brain.encode(max_brain_length)
		inputs.append(set[0])
		outputs.append(set[1])
		neuron_counts.append(set[2])
		genomes.append(set[3])
	numpy.savez("brain_file", inputs=inputs, outputs=outputs, neuron_counts=neuron_counts, genomes=genomes)
	numpy.save("decay_constants", [FOOD_RATE_TARGET, ENERGY_RATE_TARGET, INVERSE_DECAY, food_decay, energy_decay])
	numpy.save("alg_constants", [alg.max_x, alg.max_y, len(alg.population), alg.MAX_FOODS, alg.FOOD_RESPAWN_RATE, alg.AVG_FOOD_SUSTENANCE, alg.FOOD_SPREAD, alg.ENERGY_DECAY_PER_20, alg.CREATURE_LIFESPAN, alg.MUTATION_CHANCE, alg.CREATURE_VISIBILITY])
	
t1 = time.time()
mins = str(int(t1-t0)//60)
secs = str(int(t1-t0)%60)
if len(secs) == 1:
	secs = "0"+secs
'''	
pyplot.plot(x_plot,y_plot)
pyplot.xlabel("time")
pyplot.ylabel("population")
pyplot.title("Creatures population over time")
pyplot.show()
'''
print("Time taken for ", str(count/3)[:3], " minutes of running: ", mins, ":", secs, sep="")
