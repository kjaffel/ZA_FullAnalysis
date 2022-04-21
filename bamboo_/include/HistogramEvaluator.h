#include <string>
#include <memory>

#include "TFile.h"
#include "TH1.h"

template<typename... Args>
class HistogramEvaluator {
    public:

        HistogramEvaluator(std::string path, std::string histName) {
            TFile* file = TFile::Open(path.c_str());
            TH1* hist = dynamic_cast<TH1*>(file->Get(histName.c_str()));
            hist->SetDirectory(0);
            _hist = std::shared_ptr<TH1>(hist);
            file->Close();
        }
        virtual ~HistogramEvaluator() {}

        float evaluate(Args... args) const {
            return _hist->GetBinContent(_hist->FindBin(args...));
        }

    private:

        std::shared_ptr<TH1> _hist;
};
