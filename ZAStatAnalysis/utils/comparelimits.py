import os
from matplotlib import pyplot as plt

logy = False
output ='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/' 

for mH in [500, 800]:
    fig = plt.figure(figsize=(8, 6))
    ax  = fig.add_subplot(111)
    
    if mH == 500:
       # ul__combinedlimits/preapproval/work__v10-ext2/work__1/
        MA=[50, 200, 400]
        #Alessia_ellipses    = [37.9, 32.0, 74.8] # observed
        Alessia_ellipses     = [27, 22.9, 62.9]   # expected
       # uniform_50bins      = [26.32141113 17.1661377  35.47668457]
       # BB_hybride          = [26.32141113 22.50671387 37.00256348]
       # BB_Sonly            = [33.95080566 19.45495605 38.52844238] 
       # MA=[50, 200, 400, 700]
       # uniform_50bins      = [133.5144043    9.53674316  10.29968262  20.98083496]
       # BB_hybride          = [208.2824707   10.29968262  14.11437988  26.32141113]
       # BB_Sonly            = [230.40771484  13.35144043  14.87731934  28.61022949]
                                
        uniform_50bins      = [27.84729004, 19.45495605, 40.05432129]
       #uniform_B_good_stat = [21.74377441, 15.64025879, 50.73547363]
        BB_Bonly            = [21.74377441, 15.64025879, 35.8581543 ]
        
        BB_Sonly           = [38.52844238, 22.50671387, 29.37316895]
        #BB_Sonly            = [40.4, 16.4, 41.6]
        
        BB_hybride          = [21.74377441, 15.64025879, 34.71374512]
        
        #BB_hybride_good_stat= [22.12524414, 15.64025879, 40.05432129]
    
    if mH == 800:
        MA=[50, 200, 400, 700]
        #Alessia_ellipses    = [95.6, 27.5, 8.96, 27.0]
        Alessia_ellipses    = [86.3, 13.2, 13.7, 26.5]
        
        uniform_50bins      = [85.44921875, 14.11437988, 13.35144043, 31.6619873 ]
       # uniform_B_good_stat = [67.5201416,  11.06262207, 11.06262207, 48.44665527]
        BB_Bonly            = [70.95336914, 11.06262207, 11.06262207, 27.84729004]
        BB_Sonly            = [72.09777832, 11.06262207, 11.82556152, 27.08435059]
        BB_hybride          = [71.33483887, 11.06262207, 11.06262207, 26.70288086]
       # BB_hybride_good_stat= [71.71630859, 11.06262207, 11.06262207, 27.84729004]

    name = 'limits_uniform_vs_bb_mH-{}'.format(mH)
    ax.plot(MA, Alessia_ellipses, "o", linestyle='solid', color='black', label="ellipses: HIG-18-012 (Expected)")
    ax.plot(MA, uniform_50bins, "o", linestyle='solid', color='red', label="uniform: 50 bins")
    #ax.plot(MA, uniform_B_good_stat, "o", linestyle='solid', color='purple', label="uniform: 50 bins + good stat.")
    ax.plot(MA, BB_Bonly, "o", linestyle='solid', color='blue', label="BB: B-Only")
    ax.plot(MA, BB_Sonly, "o", linestyle='solid', color='magenta', label="BB: S-Only")
    ax.plot(MA, BB_hybride, "o", linestyle='solid', color='aqua', label="BB: hybride")
  #  ax.plot(MA, BB_hybride_good_stat, "o", linestyle='solid', color='mediumspringgreen', label="BB: hybride + good stat.")
    
    ax.legend(prop=dict(size=12), loc='best')
    ax.set_xlabel(r'$M_{A}$ (GeV)')
    ax.set_ylabel(r'95% C.L. expected limit on $\sigma(pp \rightarrow\, H) \times\, BR(H \rightarrow\, ZA) \times\, BR(A \rightarrow\, b\bar{b})$ (fb)')
    
    plt.title('CMS Preliminary', fontsize=14., loc='left', style='italic', weight="bold")
    plt.title(r'$35.9 fb^{-1}$ (13TeV)', fontsize=14., loc='right', style='italic', weight="bold")
    if logy:
        ax.set_yscale('log')
        name += '_logy'
    fig.savefig(os.path.join(output, name+'.png'))
    #fig.savefig(os.path.join(output, name+'.pdf'))
    plt.close(fig)
    plt.gcf().clear()
