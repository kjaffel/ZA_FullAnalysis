from bamboo import treefunctions as op

def freeze(d):
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def key_for_value(d):
    """Return a key in neseted dic `d` having a sub-key ."""
    for k, v in d.items():
        if k == "350-850" or k == "350-840":
            return k

def getBoOstedWeight(era, tagger, wp, fatjet):
    if era == '2016':
        DeepDoubleBvL= {
                "350-850":{  
                    # var: (loose, medium1, medium2, tight1, tight2)
                    "up":      (0.10, 0.11, 0.11, 0.10, 0.20),
                    "down":    (0.04, 0.04, 0.04, 0.08, 0.10),
                    "nominal": (0.95, 0.86, 0.77, 0.74, 0.68)
                    }
                }
        DoubleB= {
                "350-850":{  
                    # var: (loose, medium1, medium2, tight)
                    "up":      (0.06, 0.06, 0.07, 0.08),
                    "down":    (0.13, 0.10, 0.13, 0.14),
                    "nominal": (1.03, 1.01, 0.95, 0.90)
                    }
                }
    elif era =='2017':
        DeepDoubleBvL= {
                "250-350":{
                    # var: (loose, medium1, medium2, tight1, tight2)
                    "up":      (0.04, 0.04, 0.05, 0.04, 0.05),
                    "down":    (0.04, 0.05, 0.05, 0.05, 0.05),
                    "nominal": (0.92, 0.82, 0.72, 0.62, 0.57)
                    },
                "350-850":{  
                    "up":      (0.07, 0.06, 0.05, 0.06, 0.15),
                    "down":    (0.12, 0.10, 0.07, 0.11, 0.23),
                    "nominal": (1.01, 0.77, 0.68, 0.65, 0.54)
                    }
                }
        DoubleB = { 
                "250-350":{
                    # var: (loose, medium1, medium2, tight)
                    "up":      (0.03, 0.04, 0.04, 0.04),
                    "down":    (0.03, 0.03, 0.04, 0.04),
                    "nominal": (0.96, 0.93, 0.85, 0.78)
                    },
                "350-840":{  
                    "up":      (0.06, 0.08, 0.07, 0.04),
                    "down":    (0.04, 0.04, 0.04, 0.04),
                    "nominal": (0.95, 0.9,  0.8,  0.72)
                    }
                }
    else:
        DeepDoubleBvL= {
                "250-350":{
                    # var: (loose, medium1, medium2, tight1, tight2)
                    "up":      (0.04, 0.07, 0.06, 0.07, 0.05),
                    "down":    (0.05, 0.05, 0.05, 0.05, 0.05),
                    "nominal": (0.97, 0.81, 0.74, 0.65, 0.61)
                    },
                "350-850":{  
                    "up":      (0.07, 0.06, 0.07, 0.10, 0.07),
                    "down":    (0.06, 0.05, 0.06, 0.05, 0.09),
                    "nominal": (0.96, 0.76, 0.70, 0.67, 0.69)
                    }
                }
        DoubleB= {
                "250-350":{
                    # var: (loose, medium1, medium2, tight)
                    "up":      (0.04, 0.05, 0.08, 0.05),
                    "down":    (0.04, 0.05, 0.04, 0.07),
                    "nominal": (0.93, 0.93, 0.89, 0.82)
                    },
                "350-850":{  
                    "up":      (0.05, 0.06, 0.05, 0.05),
                    "down":    (0.04, 0.04, 0.05, 0.06),
                    "nominal": (0.98, 0.89, 0.84, 0.76)
                    }
                }

    idx = ( 0 if wp=='L' else (1 if wp=='M1' else ( 2 if wp=="M2" else( 3 if wp =="T1"else (4 if wp =="T2" else(3))))))
    dic = (DeepDoubleBvL if tagger =="DeepDoubleBvL" else (DoubleB))
    pTrange = key_for_value(dic)
    pTmax = float(key_for_value(dic).split('-')[-1])    

    if op.in_range(250., fatjet[0].pt, 350.) and era != '2016':
        nominal = dic["250-350"]["nominal"][idx]
        up = nominal + dic["250-350"]["up"][idx] 
        down = nominal - dic["250-350"]["down"][idx]     
    
    elif op.in_range(350., fatjet[0].pt, pTmax):
        nominal = dic[pTrange]["nominal"][idx] 
        up = nominal + dic[pTrange]["up"][idx]
        down = nominal - dic[pTrange]["down"][idx]
        
    wgt = op.systematic(op.c_float(nominal), name="{0}{1}".format(tagger, wp), up=op.c_float(up), down=op.c_float(down))

    return wgt 

def addBoOstedTagger(AK8jets, BoostedTopologiesWP):

    # DoubleB and DeepDoubleBvL 13 TeV data
    cleaned_AK8JetsByDDBvL = op.sort(AK8jets, lambda j: -j.btagDDBvL)
    
    bjetsBoOsted = {}
    for tagger  in BoostedTopologiesWP.keys():
        
        bJets_AK8_DeepDoubleBvL ={}
        bJets_AK8_DoubleB ={}
        for wp in sorted(safeget(BoostedTopologiesWP, tagger).keys()):           
            # FIXME not found in nanoAOD !!! 
            if tagger== 'DoubleB':
                bJets_AK8_DoubleB[wp] = None 
                #op.select(?, lambda j : j.? >= BoostedTopologiesWP['DoubleB'][wp])
                bjetsBoOsted[tagger]=bJets_AK8_DoubleB
                
            #DeepDoubleX discriminator (no mass-decorrelation) for H(Z)->bb vs QCD 
            if tagger == 'DeepDoubleBvL':
                #bJets_AK8_DeepDoubleBvL[wp] = op.select(cleaned_AK8JetsByDDBvL,
                #                                            lambda j : op.AND(j.subJet1.btagDDBvL >= BoostedTopologiesWP['DeepDoubleBvL'][wp],
                #                                                              j.subJet2.btagDDBvL >= BoostedTopologiesWP['DeepDoubleBvL'][wp]))
                bJets_AK8_DeepDoubleBvL[wp] = op.select(cleaned_AK8JetsByDDBvL, lambda j : j.btagDDBvL >= BoostedTopologiesWP['DeepDoubleBvL'][wp])
                bjetsBoOsted[tagger] = bJets_AK8_DeepDoubleBvL
        
    return bjetsBoOsted




