from math import exp

from math import tanh

class dyrwt_fct_boosted_LL_2017:
	def value(self,index,in0):
		self.input0 = (in0 - 0)/1
		if index==0: return self.neuron0x83507a0();
		return 0.
	def neuron0x834e9c0(self):
		return self.input0
	def neuron0x834ef10(self):
		input = 0.971754
		input = input + self.synapse0x834eed0()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x834f250(self):
		input = -9.13383
		input = input + self.synapse0x834f590()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x834f5d0(self):
		input = 13.5155
		input = input + self.synapse0x834f7f0()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x8350420(self):
		input = -11.5184
		input = input + self.synapse0x8350760()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x83507a0(self):
		input = -1.57891
		input = input + self.synapse0x8350ae0()
		input = input + self.synapse0x8350b20()
		input = input + self.synapse0x8350b60()
		input = input + self.synapse0x8350ba0()
		return (input*1)+0
	def synapse0x834eed0(self):
		return (self.neuron0x834e9c0()*-0.168534)
	def synapse0x834f590(self):
		return (self.neuron0x834e9c0()*0.0746603)
	def synapse0x834f7f0(self):
		return (self.neuron0x834e9c0()*-0.111703)
	def synapse0x8350760(self):
		return (self.neuron0x834e9c0()*0.0118134)
	def synapse0x8350ae0(self):
		return (self.neuron0x834ef10()*-1.01337)
	def synapse0x8350b20(self):
		return (self.neuron0x834f250()*2.95439)
	def synapse0x8350b60(self):
		return (self.neuron0x834f5d0()*2.59041)
	def synapse0x8350ba0(self):
		return (self.neuron0x8350420()*-4.71271)
