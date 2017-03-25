import numpy
from copy import copy

class Brain():
	def __init__(self, genome, inputs, outputs, neuron_count=0):
		#  genome attribute is a list of BrainGenes (see class below)
		self.genome = genome
		self.inputs = inputs
		self.outputs = outputs
		
		self.neuron_count = neuron_count
		if self.neuron_count==0:
			self.neuron_count += len(self.inputs)+len(self.outputs)
			for gene in self.genome:
				if gene.output_neuron > self.neuron_count:
					self.neuron_count += 1
		 
	def forward(self, X):
		out = [0]*100
		for i in range(len(self.inputs)):
			out[self.inputs[i]] = X[i]
		for gene in self.genome:
			#this does all the moving numbers around
			if gene.enabled and not gene.output_neuron in self.outputs:
				out[gene.output_neuron] += out[gene.input_neuron]*gene.weight
		for gene in self.genome:
			if gene.enabled and gene.output_neuron in self.outputs:
				out[gene.output_neuron] += out[gene.input_neuron]*gene.weight
		
		#print(out)
		
		out = numpy.trim_zeros(out, 'f')
		
		ret_array = []
		
		#gets the correct neurons for output
		for o in self.outputs:
			ret_array.append(out[o])
		
		return ret_array
		
	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
		ret = []
		for g in self.genome:
			ret.append([g.input_neuron, g.output_neuron])
		
		string = str(ret)
		
		#translation_table = dict.fromkeys(map(ord, '\"\''), None)
		#string = string.translate(translation_table)
		
		return string
		
	def encode(self, final_length):
		genome_encoding = self.pad_genome_with_zeros([g.encode() for g in self.genome], final_length)
		return self.inputs, self.outputs, self.neuron_count, genome_encoding
	
	def pad_genome_with_zeros(self, genome, final_length):
		arr = copy(genome)
		for i in range(final_length-len(genome)):
			arr.append([0,0,0,0,False])
		
		return arr
		
class BrainGene():
	def __init__(self, input_neuron, output_neuron, weight, innovation_number, enabled=True):
		self.enabled = enabled
		self.innovation_number = innovation_number
		self.input_neuron = input_neuron
		self.output_neuron = output_neuron
		self.weight = weight
	
	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
		return str([str(self.input_neuron), str(self.output_neuron), "w: "+str(self.weight), "inum: "+str(self.innovation_number)])
	
	def encode(self):
		return [self.input_neuron, self.output_neuron, self.weight, self.innovation_number, self.enabled]
		
