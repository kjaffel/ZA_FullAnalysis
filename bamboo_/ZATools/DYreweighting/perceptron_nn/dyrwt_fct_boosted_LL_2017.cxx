#include "dyrwt_fct_boosted_LL_2017.h"
#include <cmath>

double dyrwt_fct_boosted_LL_2017::Value(int index,double in0) {
   input0 = (in0 - 0)/1;
   switch(index) {
     case 0:
         return neuron0x83507a0();
     default:
         return 0.;
   }
}

double dyrwt_fct_boosted_LL_2017::Value(int index, double* input) {
   input0 = (input[0] - 0)/1;
   switch(index) {
     case 0:
         return neuron0x83507a0();
     default:
         return 0.;
   }
}

double dyrwt_fct_boosted_LL_2017::neuron0x834e9c0() {
   return input0;
}

double dyrwt_fct_boosted_LL_2017::input0x834ef10() {
   double input = 0.971754;
   input += synapse0x834eed0();
   return input;
}

double dyrwt_fct_boosted_LL_2017::neuron0x834ef10() {
   double input = input0x834ef10();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_LL_2017::input0x834f250() {
   double input = -9.13383;
   input += synapse0x834f590();
   return input;
}

double dyrwt_fct_boosted_LL_2017::neuron0x834f250() {
   double input = input0x834f250();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_LL_2017::input0x834f5d0() {
   double input = 13.5155;
   input += synapse0x834f7f0();
   return input;
}

double dyrwt_fct_boosted_LL_2017::neuron0x834f5d0() {
   double input = input0x834f5d0();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_LL_2017::input0x8350420() {
   double input = -11.5184;
   input += synapse0x8350760();
   return input;
}

double dyrwt_fct_boosted_LL_2017::neuron0x8350420() {
   double input = input0x8350420();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_LL_2017::input0x83507a0() {
   double input = -1.57891;
   input += synapse0x8350ae0();
   input += synapse0x8350b20();
   input += synapse0x8350b60();
   input += synapse0x8350ba0();
   return input;
}

double dyrwt_fct_boosted_LL_2017::neuron0x83507a0() {
   double input = input0x83507a0();
   return (input * 1)+0;
}

double dyrwt_fct_boosted_LL_2017::synapse0x834eed0() {
   return (neuron0x834e9c0()*-0.168534);
}

double dyrwt_fct_boosted_LL_2017::synapse0x834f590() {
   return (neuron0x834e9c0()*0.0746603);
}

double dyrwt_fct_boosted_LL_2017::synapse0x834f7f0() {
   return (neuron0x834e9c0()*-0.111703);
}

double dyrwt_fct_boosted_LL_2017::synapse0x8350760() {
   return (neuron0x834e9c0()*0.0118134);
}

double dyrwt_fct_boosted_LL_2017::synapse0x8350ae0() {
   return (neuron0x834ef10()*-1.01337);
}

double dyrwt_fct_boosted_LL_2017::synapse0x8350b20() {
   return (neuron0x834f250()*2.95439);
}

double dyrwt_fct_boosted_LL_2017::synapse0x8350b60() {
   return (neuron0x834f5d0()*2.59041);
}

double dyrwt_fct_boosted_LL_2017::synapse0x8350ba0() {
   return (neuron0x8350420()*-4.71271);
}

