import ROOT
import UserInput

class Ntuple(object):
    def __init__(self, weights_branch):
        self.lhe_weights_branch = weights_branch
        self.proof_path = ''
        self.chain = ''
    def setInitSumWeights(self, sum_weights):
        self.init_sum_weights = sum_weights
    def setChain(self, chain):
        self.chain = chain
    def setProofPath(self, proof_path):
        self.proof_path = proof_path
    def getBranchSum(self, branch_name):
        hist_name = "_".join(["sumhist", branch_name])
        if self.proof_path != '':
            proof = ROOT.gProof
            proof.DrawSelect(self.proof_path, 
                "1>>%s(1, 0, 2)" % hist_name, 
                "Sum$(%s)" % branch_name, "goff")
            hist = proof.GetOutputList().FindObject(hist_name)
        else:
            self.chain.Draw("1>>%s(1, 0, 2)" % hist_name, 
                    "Sum$(%s)" % branch_name)
            hist = ROOT.gROOT.FindObject(hist_name)
        return hist.GetBinContent(1)
    def getSumWeights(self, cut_string):
        if self.proof_path != '':
            return self.getSumWeightsProof(cut_string)
        else:
            return []
    def getSumWeightsProof(self, cut_string):
        proof = ROOT.gProof
        proof.Load("sumWeights.C+")
        sumWeights = ROOT.sumWeights()
        proof.Process(self.proof_path, sumWeights, cut_string)
        summedWeightsHist = sumWeights.GetOutputList().FindObject('summedWeights')
        summedWeightsHist.Draw("hist")
        sums = []
        for i in xrange(1, summedWeightsHist.GetSize() + 1):
            sums.append(summedWeightsHist.GetBinContent(i))
        sums = sums[:sums.index(0.0)]
        return sums
