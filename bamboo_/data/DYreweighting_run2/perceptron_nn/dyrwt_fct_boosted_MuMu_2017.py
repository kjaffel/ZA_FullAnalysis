from math import exp

from math import tanh

class dyrwt_fct_boosted_MuMu_2017:
	def value(self,index,in0):
		self.input0 = (in0 - 0)/1
		if index==0: return self.neuron0x947d0d0();
		return 0.
	def neuron0x947cd90(self):
		return self.input0
	def neuron0xa45d300(self):
		input = -21.7169
		input = input + self.synapse0x832ae10()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0xa45d5b0(self):
		input = 1.0068
		input = input + self.synapse0x9320010()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0xa45d8f0(self):
		input = 2.3476
		input = input + self.synapse0xa464e60()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0xa45dcd0(self):
		input = -6.29544
		input = input + self.synapse0x94a5a90()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x947d0d0(self):
		input = 1.07758
		input = input + self.synapse0xa45e130()
		input = input + self.synapse0xa45e170()
		input = input + self.synapse0xa45e1b0()
		input = input + self.synapse0xa45e1f0()
		return (input*1)+0
	def synapse0x832ae10(self):
		return (self.neuron0x947cd90()*0.0226446)
	def synapse0x9320010(self):
		return (self.neuron0x947cd90()*-0.843391)
	def synapse0xa464e60(self):
		return (self.neuron0x947cd90()*-0.301418)
	def synapse0x94a5a90(self):
		return (self.neuron0x947cd90()*0.0109543)
	def synapse0xa45e130(self):
		return (self.neuron0xa45d300()*-24.4656)
	def synapse0xa45e170(self):
		return (self.neuron0xa45d5b0()*1.19219)
	def synapse0xa45e1b0(self):
		return (self.neuron0xa45d8f0()*-2.27515)
	def synapse0xa45e1f0(self):
		return (self.neuron0xa45dcd0()*4.12597)
