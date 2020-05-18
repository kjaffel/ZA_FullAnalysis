#ifndef sumWeights_h
#define sumWeights_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TH1F.h>
#include <TTreeFormula.h>
#include <vector>
#include <iostream>

class sumWeights : public TSelector {
public :
  TTree          *fChain;

  std::vector<float>* fWeights;
  double fOrigWeight;

  TBranch        *fWeightsBranch;
  TBranch        *fOrigWeightBranch;
  
  TTreeFormula   *fCutFormula;

  TH1F     *fSummedWeightsHist;

  sumWeights(TTree * /*tree*/ =0) : fChain(0), fSummedWeightsHist(0), fCutFormula(0) { }
  virtual ~sumWeights() { SafeDelete(fSummedWeightsHist); SafeDelete(fCutFormula); }
  virtual Int_t   Version() const { return 2; }
  virtual void    Begin(TTree *tree);
  virtual void    SlaveBegin(TTree *tree);
  virtual void    Init(TTree *tree);
  virtual Bool_t  Notify();
  virtual Bool_t  Process(Long64_t entry);
  virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
  virtual void    SetOption(const char *option) { fOption = option; }
  virtual void    SetObject(TObject *obj) { fObject = obj; }
  virtual void    SetInputList(TList *input) { fInput = input; }
  virtual TList  *GetOutputList() const { return fOutput; }
  virtual void    SlaveTerminate();
  virtual void    Terminate();

  ClassDef(sumWeights,0);

};

#endif

#ifdef sumWeights_cxx
void sumWeights::Init(TTree *tree)
{
  if (!tree) return;
  fChain = tree;

  fWeights = 0;
  fOrigWeight = 0;
  fChain->SetBranchAddress("LHEweights", &fWeights, &fWeightsBranch);
  fChain->SetBranchAddress("weight", &fOrigWeight, &fOrigWeightBranch);

  SafeDelete(fCutFormula);
  fCutFormula = new TTreeFormula("CutFormula", fOption, fChain);
  fCutFormula->SetQuickLoad(kTRUE);
  if (!fCutFormula->GetNdim()) { delete fCutFormula; fCutFormula = 0;}
}

Bool_t sumWeights::Notify()
{
  return kTRUE;
}

#endif // #ifdef sumWeights_cxx
