from math import exp

from math import tanh

class dyrwt_fct_boosted_ElEl_2017:
	def value(self,index,in0):
		self.input0 = (in0 - 0)/1
		if index==0: return self.neuron0x947cf10();
		return 0.
	def neuron0x94a5980(self):
		return self.input0
	def neuron0x94a5df0(self):
		input = 0.321258
		input = input + self.synapse0x94549d0()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x947c550(self):
		input = 51.5492
		input = input + self.synapse0x832ae10()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x947c890(self):
		input = -92.8147
		input = input + self.synapse0x948bf30()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x947cbd0(self):
		input = -14.2495
		input = input + self.synapse0x948a520()
		if input<-709. : return 0
		return ((1/(1+exp(-input)))*1)+0
	def neuron0x947cf10(self):
		input = -5.05179
		input = input + self.synapse0x947d250()
		input = input + self.synapse0x947d290()
		input = input + self.synapse0x947d2d0()
		input = input + self.synapse0x947d310()
		return (input*1)+0
	def synapse0x94549d0(self):
		return (self.neuron0x94a5980()*1.03686)
	def synapse0x832ae10(self):
		return (self.neuron0x94a5980()*-0.0559525)
	def synapse0x948bf30(self):
		return (self.neuron0x94a5980()*1.22449)
	def synapse0x948a520(self):
		return (self.neuron0x94a5980()*0.420608)
	def synapse0x947d250(self):
		return (self.neuron0x94a5df0()*0.812516)
	def synapse0x947d290(self):
		return (self.neuron0x947c550()*5.05179)
	def synapse0x947d2d0(self):
		return (self.neuron0x947c890()*0.153938)
	def synapse0x947d310(self):
		return (self.neuron0x947cbd0()*0.210135)
