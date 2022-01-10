import csv
import os

base = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/data/Inputs/'
for tagger_f in ['2016UL/Btag/DeepJet_106XUL16preVFPSF_v1.csv', 
                 '2016UL/Btag/DeepJet_106XUL16postVFPSF_v2.csv', 
                 '2016UL/Btag/DeepCSV_106XUL16preVFPSF_v1.csv', 
                 '2016UL/Btag/DeepCSV_106XUL16postVFPSF_v2.csv']:
    with open(os.path.join(base, tagger_f)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open(os.path.join(base, tagger_f.replace('.csv', '__prelegacyformat.csv')), 'w+') as outf:
            for i, line in enumerate(csv_reader):
                if i == 0: 
                    outf.write(f"{', '.join(line)}\n")
                else:
                    formula = '"'+f"{line[-1].replace('pow(x,','(x**')}"+'"' # without "" you will run into error when compiling 
                    OP = line[0]
                    idx = '0' if OP =='L' else( '1' if OP =='M' else( 3))
                    flavor = 0 if line[3]==5 else(1 if line[3]==4 else(2))
                    outf.write(f"{idx}, {', '.join(line[1:3])}, {flavor}, {', '.join(line[4:-1])}, {formula}\n")
        print(f"file succesfully saved in :: {os.path.join(base, tagger_f.replace('.csv', '__prelegacyformat.csv'))}")
