#include "dyrwt_fct_boosted_MuMu_2017.h"
#include <cmath>

double dyrwt_fct_boosted_MuMu_2017::Value(int index,double in0) {
   input0 = (in0 - 0)/1;
   switch(index) {
     case 0:
         return neuron0x947d0d0();
     default:
         return 0.;
   }
}

double dyrwt_fct_boosted_MuMu_2017::Value(int index, double* input) {
   input0 = (input[0] - 0)/1;
   switch(index) {
     case 0:
         return neuron0x947d0d0();
     default:
         return 0.;
   }
}

double dyrwt_fct_boosted_MuMu_2017::neuron0x947cd90() {
   return input0;
}

double dyrwt_fct_boosted_MuMu_2017::input0xa45d300() {
   double input = -21.7169;
   input += synapse0x832ae10();
   return input;
}

double dyrwt_fct_boosted_MuMu_2017::neuron0xa45d300() {
   double input = input0xa45d300();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_MuMu_2017::input0xa45d5b0() {
   double input = 1.0068;
   input += synapse0x9320010();
   return input;
}

double dyrwt_fct_boosted_MuMu_2017::neuron0xa45d5b0() {
   double input = input0xa45d5b0();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_MuMu_2017::input0xa45d8f0() {
   double input = 2.3476;
   input += synapse0xa464e60();
   return input;
}

double dyrwt_fct_boosted_MuMu_2017::neuron0xa45d8f0() {
   double input = input0xa45d8f0();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_MuMu_2017::input0xa45dcd0() {
   double input = -6.29544;
   input += synapse0x94a5a90();
   return input;
}

double dyrwt_fct_boosted_MuMu_2017::neuron0xa45dcd0() {
   double input = input0xa45dcd0();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_MuMu_2017::input0x947d0d0() {
   double input = 1.07758;
   input += synapse0xa45e130();
   input += synapse0xa45e170();
   input += synapse0xa45e1b0();
   input += synapse0xa45e1f0();
   return input;
}

double dyrwt_fct_boosted_MuMu_2017::neuron0x947d0d0() {
   double input = input0x947d0d0();
   return (input * 1)+0;
}

double dyrwt_fct_boosted_MuMu_2017::synapse0x832ae10() {
   return (neuron0x947cd90()*0.0226446);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0x9320010() {
   return (neuron0x947cd90()*-0.843391);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0xa464e60() {
   return (neuron0x947cd90()*-0.301418);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0x94a5a90() {
   return (neuron0x947cd90()*0.0109543);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0xa45e130() {
   return (neuron0xa45d300()*-24.4656);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0xa45e170() {
   return (neuron0xa45d5b0()*1.19219);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0xa45e1b0() {
   return (neuron0xa45d8f0()*-2.27515);
}

double dyrwt_fct_boosted_MuMu_2017::synapse0xa45e1f0() {
   return (neuron0xa45dcd0()*4.12597);
}

