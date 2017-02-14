import numpy as np

class NeuralNetwork():
	#Note: if a callable is used as the activation function, its "__call__" function needs to take one argument -- "0" for the function itself, "1" for its derivative
	def __init__(self, layers, activation='logistic'):
		self.data = layers
		self.activ_function = activation
		self.l = [None]*len(layers)
		self.syn = []
		for i in range(len(layers)-1):
			self.syn.append(np.random.randn(layers[i], layers[i+1]))
	
	def activation(self, X):
		#clip is used to prevent over/underflow
		X = np.clip(X, -500, 500)
		if self.activ_function == 'step':
			return np.sign(X)+1
		elif self.activ_function == 'tanh':
			return np.tanh(X)
		elif self.activ_function == 'logistic':
			return 1/(1+np.exp(-X))
		elif callable(self.activ_function):
			return self.activ_function.__call__(0)
		else:
			return 1/(1+np.exp(-X))
			
	def activation_deriv(self, X):
		if self.activ_function == 'step':
			return np.zeros(np.ma.shape())
		elif self.activ_function == 'tanh':
			return 1-np.power(self.activation(X), 2)
		elif self.activ_function == 'logistic':
			return self.activation(X)*(1-self.activation(X))
		elif callable(self.activ_function):
			return self.activ_function.__call__(1)
		else:
			return self.activation(X)*(1-self.activation(X))
	
	def error(self, y):
		#is this the error function or the derivative of the error function??? something to think about
		return y - self.l[len(self.l)-1]
	
	#forward propagation										
	def forward(self, X):
		self.l[0] = np.array(X)
		for i in range(1, len(self.l)):
			self.l[i] = np.array(self.activation(np.dot(self.l[i-1], self.syn[i-1])))
		
		return self.l[len(self.l)-1]
	
	#backward propagation
	def backward(self, X, y, iter=6000):
		for i in range(iter):	
			self.forward(X)
			
			l_errors = [None]*len(self.l)
			l_deltas = [None]*len(self.l)
			
			l_errors[len(l_errors)-1] = self.error(y)
			l_deltas[len(l_deltas)-1] = np.multiply(l_errors[len(l_errors)-1], self.activation_deriv(self.l[len(self.l)-1]))
			
			#sets the errors and corresponding changes for each layer of the network
			for j in range(len(self.l)-1-1,0,-1):
				l_errors[j] = np.dot(l_deltas[j+1], self.syn[j].T)
				l_deltas[j] = np.multiply(l_errors[j], self.activation_deriv(self.l[j]))
				
			
			for k in range(len(self.syn)):
				self.syn[k]  += np.dot(self.l[k].T, l_deltas[k+1])
