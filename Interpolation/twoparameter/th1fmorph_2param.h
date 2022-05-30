#include "TH1.h"

TH1F *th1fmorph_2param(const char *chname, 
                const char *chtitle,
                TH1F *hist1,TH1F *hist2, TH1F *hist3,
                Double_t* par1, Double_t* par2, Double_t* par3,Double_t* parinterp,
                Double_t morphedhistnorm,
                Int_t idebug=0) ;
TH1D *th1fmorph_2param(const char *chname, 
                const char *chtitle,
                TH1D *hist1,TH1D *hist2, TH1D *hist3,
                Double_t* par1, Double_t* par2, Double_t* par3,Double_t* parinterp,
                Double_t morphedhistnorm,
                Int_t idebug=0) ;
