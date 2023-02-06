using namespace std;
#include <TMultiLayerPerceptron.h>
#include <TTree.h>
#include <TCanvas.h>
#include <TGraph2D.h>
#include <TSystem.h>
#include <fstream>
#include <iostream>

void fit(char * wgtFile, char * rFile)
{
	if (!gROOT->GetClass("TMultiLayerPerceptron")) {
		gSystem->Load("libMLP");
	}
	// Put data in a TTree
	Double_t m,r;
	TTree* tree = new TTree("DYSF","DY scale factor");
	tree->Branch("m",&m,"m/D");
	tree->Branch("r",&r,"r/D");

	TFile *_file0 = TFile::Open(rFile);
	TH1F * mjj_data = (TH1F *) _file0->FindObjectAny("mjj_data");
	mjj_data->Draw();
	mjj_data->SetDirectory(0);
	Int_t nbins = mjj_data->GetNbinsX ();
	for(Int_t i = 0; i<nbins; i++) {
		m = mjj_data->GetBinCenter(i);
		r = mjj_data->GetBinContent(i);
		tree->Fill();
	}
	_file0->Close();
	// Instantiate a NN
	TMultiLayerPerceptron network("m:4:r",tree);
	network.Train(1000,"textgraph,update=10");
	network.Export(wgtFile); // this can be used later
	network.Export(wgtFile,"Python"); // this can be used later
	// plot and compare
	TH1F* h = (TH1F*)mjj_data->Clone("ansatz");
	Double_t in[1] = {0};
	for(Int_t i = 0; i<nbins; i++) {
		in[0] = mjj_data->GetBinCenter(i);
		h->SetBinContent(i,network.Evaluate(0,in));
		h->SetBinError(i,0);
	}
	TCanvas* t = new TCanvas();
	h->Draw();
    t->SaveAs("c.png");
}



