from Object import *

class Food(Object):
	def __init__(self, position, sustenance, network_value):
		self.position = position
		self.sustenance = sustenance
		self.network_value = network_value
