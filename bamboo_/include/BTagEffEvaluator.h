//from Sebastien Wertz
#pragma once

#include <string>
#include <map>
#include <vector>
#include <memory>

#include "TFile.h"
#include "TH2D.h"

std::map<int, std::string> flavMap { {5, "b"}, {4, "c"}, {0, "light"}};

class BTagEffEvaluator {
    public:

        BTagEffEvaluator(std::string path, std::string WP, std::string REG, std::string TAGGER, std::vector<double> thresholds, std::string PROCESS) {
            _thresholds = thresholds;
            TFile* file = TFile::Open(path.c_str());
            for (auto flav: flavMap) {
                //flavEffsL.emplace(flav.first, static_cast<TH2D*>(file->Get("1lep_4j_jet_pt_eta_" + flav.second + "_wpL_eff")));
                //flavEffsM.emplace(flav.first, static_cast<TH2D*>(file->Get(("1lep_4j_jet_pt_eta_" + flav.second + "_wpM_eff").c_str())));
                //                                          pair_lept_2j_jet_pt_vs_eta_cflav_deepflavour_wpM__mc_eff
                TH2D* hist = dynamic_cast<TH2D*>(file->Get(("pair_lept_2j_jet_pt_vs_eta_"+ flav.second + "flav_"+ REG +"_"+ TAGGER + "_wp"+ WP + "_" + PROCESS +"__mc_eff").c_str()));
                hist->SetDirectory(0);
                std::cout << "Loaded " << hist->GetName() << std::endl;
                flavEffsM.emplace(flav.first, hist);
                //flavEffsT.emplace(flav.first, static_cast<TH2D*>(file->Get("1lep_4j_jet_pt_eta_" + flav.second + "_wpT_eff")));
            }
            file->Close();
        }
        virtual ~BTagEffEvaluator() {}

        //float evaluate(int flavour, float bTag, float pT, float eta, float SFL, float SFM, float SFT) {
        //    float effL = flavEffsL.at(flavour)->GetBinContent(flavEffsL.at(flavour)->FindBin(pT, eta));
        //    float effM = flavEffsM.at(flavour)->GetBinContent(flavEffsM.at(flavour)->FindBin(pT, eta));
        //    float effT = flavEffsT.at(flavour)->GetBinContent(flavEffsT.at(flavour)->FindBin(pT, eta));
        //    if (bTag <= _thresholds.at(0)) {
        //        return (1 - SFL * effL) / (1 - effL);
        //    } else if (bTag <= _thresholds.at(1)) {
        //        return (SFL * effL - SFM * effM) / (effL - effM);
        //    } else if (bTag <= _thresholds.at(2)) {
        //        return (SFM * effM - SFT * effT) / (effM - effT);
        //    } else {
        //        return SFT;
        //    }
        float evaluate(int flavour, float bTag, float pT, float eta, float SFM) const {
            std::shared_ptr<TH2D> hist = flavEffsM.at(flavour);
            // take value from previous bin if we are above the pT range
            if (pT >= hist->GetXaxis()->GetXmax())
                pT = hist->GetXaxis()->GetBinLowEdge(hist->GetXaxis()->GetLast());
            float effM = flavEffsM.at(flavour)->GetBinContent(flavEffsM.at(flavour)->FindBin(pT, eta));
            if ( effM < 0. || effM > 1. ) {
                std::cout<< effM << " found in the eff map, will be skipped "<< SFM <<  " is used instead !" <<std::endl;
                return SFM;
            } else if (bTag <= _thresholds.at(0)) {
                return (1 - SFM * effM) / (1 - effM);
            } else {
                return SFM;
            }
        }

    private:

        std::map<int, std::shared_ptr<TH2D>> flavEffsL;
        std::map<int, std::shared_ptr<TH2D>> flavEffsM;
        std::map<int, std::shared_ptr<TH2D>> flavEffsT;
        std::vector<double> _thresholds;
};
