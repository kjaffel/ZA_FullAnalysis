#define sumWeights_cxx

#include "sumWeights.h"
#include <iostream>

void sumWeights::Begin(TTree * /*tree*/)
{
}

void sumWeights::SlaveBegin(TTree * /*tree*/)
{
  fSummedWeightsHist = new TH1F("summedWeights", "sum of weights", 1000, 0, 1000);
  fOutput->Add(fSummedWeightsHist);
}

Bool_t sumWeights::Process(Long64_t entry)
{
  if ( fCutFormula && fCutFormula->EvalInstance() != 1. )
  {
    return kFALSE;
  }
  fWeightsBranch->GetEntry(entry);
  fOrigWeightBranch->GetEntry(entry);
  //std:cout << "Original weight is" << fOrigWeight << std::endl;
  for (size_t i = 0; i < fWeights->size(); i++) {
    fSummedWeightsHist->Fill(i, fWeights->at(i));//*fOrigWeight);
  }
  if (fWeights->size() == 0)
    fSummedWeightsHist->Fill(0.0, fOrigWeight);
  return kTRUE;
}

void sumWeights::SlaveTerminate()
{
  // Pointer is owned by fOutput, dereference
  fSummedWeightsHist = nullptr;
}

void sumWeights::Terminate()
{
}
