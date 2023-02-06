#include "dyrwt_fct_boosted_ElEl_2017.h"
#include <cmath>

double dyrwt_fct_boosted_ElEl_2017::Value(int index,double in0) {
   input0 = (in0 - 0)/1;
   switch(index) {
     case 0:
         return neuron0x947cf10();
     default:
         return 0.;
   }
}

double dyrwt_fct_boosted_ElEl_2017::Value(int index, double* input) {
   input0 = (input[0] - 0)/1;
   switch(index) {
     case 0:
         return neuron0x947cf10();
     default:
         return 0.;
   }
}

double dyrwt_fct_boosted_ElEl_2017::neuron0x94a5980() {
   return input0;
}

double dyrwt_fct_boosted_ElEl_2017::input0x94a5df0() {
   double input = 0.321258;
   input += synapse0x94549d0();
   return input;
}

double dyrwt_fct_boosted_ElEl_2017::neuron0x94a5df0() {
   double input = input0x94a5df0();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_ElEl_2017::input0x947c550() {
   double input = 51.5492;
   input += synapse0x832ae10();
   return input;
}

double dyrwt_fct_boosted_ElEl_2017::neuron0x947c550() {
   double input = input0x947c550();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_ElEl_2017::input0x947c890() {
   double input = -92.8147;
   input += synapse0x948bf30();
   return input;
}

double dyrwt_fct_boosted_ElEl_2017::neuron0x947c890() {
   double input = input0x947c890();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_ElEl_2017::input0x947cbd0() {
   double input = -14.2495;
   input += synapse0x948a520();
   return input;
}

double dyrwt_fct_boosted_ElEl_2017::neuron0x947cbd0() {
   double input = input0x947cbd0();
   return ((input < -709. ? 0. : (1/(1+exp(-input)))) * 1)+0;
}

double dyrwt_fct_boosted_ElEl_2017::input0x947cf10() {
   double input = -5.05179;
   input += synapse0x947d250();
   input += synapse0x947d290();
   input += synapse0x947d2d0();
   input += synapse0x947d310();
   return input;
}

double dyrwt_fct_boosted_ElEl_2017::neuron0x947cf10() {
   double input = input0x947cf10();
   return (input * 1)+0;
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x94549d0() {
   return (neuron0x94a5980()*1.03686);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x832ae10() {
   return (neuron0x94a5980()*-0.0559525);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x948bf30() {
   return (neuron0x94a5980()*1.22449);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x948a520() {
   return (neuron0x94a5980()*0.420608);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x947d250() {
   return (neuron0x94a5df0()*0.812516);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x947d290() {
   return (neuron0x947c550()*5.05179);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x947d2d0() {
   return (neuron0x947c890()*0.153938);
}

double dyrwt_fct_boosted_ElEl_2017::synapse0x947d310() {
   return (neuron0x947cbd0()*0.210135);
}

