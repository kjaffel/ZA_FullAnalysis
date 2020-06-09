import math
from bamboo import treefunctions as op
from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB

import json
import utils
from utils import *
import logging
logger = logging.getLogger("DY-Reweighting Plotter")


def computeMjjDYweight(self, polyfit, mjj, sample):
    
    DYsamples = ["DYToLL_0J", "DYToLL_1J", "DYToLL_2J"]
    if sample in DYsamples:
        if polyfit == 6: 
            mjj_weight = op.switch( mjj < 1000., (0.464072 + 0.00858327*mjj - 5.59681e-05*pow(mjj,2) + 1.84772e-07*pow(mjj,3) - 3.13559e-10*pow(mjj,4) + 2.60306e-13*pow(mjj,5) - 8.34964e-17*pow(mjj,6)) , op.c_float(1.))
        elif polyfit == 7: 
            mjj_weight = op.switch(mjj < 1000.,  (0.351096 + 0.0123158*mjj - 9.83683e-05*pow(mjj,2) + 4.09614e-07*pow(mjj,3) - 9.35209e-10*pow(mjj,4) + 1.18034e-12*pow(mjj,5) - 7.72464e-16*pow(mjj,6) + 2.04656e-19*pow(mjj,7)) , op.c_float(1.))
        elif polyfit == 8: 
            #mjj_weight = op.switch(op.AND(mjj < 1000., sample in DYsamples), (0.235811 + 0.0167315*mjj - 0.000159053*pow(mjj,2) + 8.14858e-07*pow(mjj,3) - 2.41448e-09*pow(mjj,4) + 4.27276e-12*pow(mjj,5) - 4.45537e-15*pow(mjj,6) + 2.52335e-18*pow(mjj,7) - 5.97895e-22*pow(mjj,8)) , op.c_float(1.))
            mjj_weight = op.switch(mjj < 1000., (0.235811 + 0.0167315*mjj - 0.000159053*pow(mjj,2) + 8.14858e-07*pow(mjj,3) - 2.41448e-09*pow(mjj,4) + 4.27276e-12*pow(mjj,5) - 4.45537e-15*pow(mjj,6) + 2.52335e-18*pow(mjj,7) - 5.97895e-22*pow(mjj,8)) , op.c_float(1.))
    else:
        mjj_weight = op.c_float(1.)
    return mjj_weight

def computeMlljjDYweight(self, polyfit, mlljj, sample):
    
    DYsamples = ["DYToLL_0J", "DYToLL_1J", "DYToLL_2J"]
    if sample in DYsamples:
        if polyfit == 6: 
            mlljj_weight = op.switch(mlljj < 1000., (0.95354 + (-0.0014433)*mlljj + (1.7198e-05)*pow(mlljj,2) + (-6.33959e-08)*pow(mlljj,3) + (1.06627e-10)*pow(mlljj,4) +(-8.32855e-14)*pow(mlljj,5) + 2.45032e-17*pow(mlljj,6)) , op.c_float(1.))
        elif polyfit == 7: 
            mlljj_weight = op.switch(mlljj < 1000., (0.999776 + (-0.0031661)*mlljj + 3.72034e-05*pow(mlljj,2) + (-1.65345e-07)*pow(mlljj,3) + 3.67378e-10*pow(mlljj,4) + (-4.31665e-13)*pow(mlljj,5) + 2.56178e-16*pow(mlljj,6) + (-6.04134e-20)*pow(mlljj,7)), op.c_float(1.)) 
        elif polyfit == 8: 
            mlljj_weight = op.switch(mlljj < 1000., (1.05604 - 0.00571127*mlljj + 7.40208e-05*pow(mlljj,2) - 4.06435e-07*pow(mlljj,3) + 1.19328e-09*pow(mlljj,4) - 2.00697e-12*pow(mlljj,5) + 1.93595e-15*pow(mlljj,6) - 9.9492e-19*pow(mlljj,7) +2.1092e-22*pow(mlljj,8)), op.c_float(1.))
    else:
        mlljj_weight = op.c_float(1.)
    return mlljj_weight

class DY_weightclass(object):
    def __init__(self, ij, mjj, mlljj, sample, systematic):
        
        DYsamples=["DYToLL_0J", "DYToLL_1J", "DYToLL_2J"]
        
        if systematic == "DY_weight11":
            self.DY_weight11 = op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight11up":
        #if systematic == "DY_weight11down":
        if systematic == "DY_weight12":
            self.DY_weight12 = op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)), op.c_float(1.)),  op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight12up":
        #if systematic == "DY_weight12down":
        if systematic == "DY_weight13":
            self.DY_weight13 = op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)), op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight13up":
        #if systematic == "DY_weight13down":
        if systematic == "DY_weight14":
            self.DY_weight14 = op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)), op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight14up":
        #if systematic == "DY_weight14down":
        if systematic == "DY_weight15":
            self.DY_weight15 =op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)), op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)) , op.c_float(1.)))
        #if systematic == "DY_weight15up":
        #if systematic == "DY_weight15down":
        if systematic == "DY_weight16":
            self.DY_weight16 =op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)),  op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)), op.c_float(1.)))
        #if systematic == "DY_weight16up":
        #if systematic == "DY_weight16down":
        if systematic == "DY_weight17":
            self.DY_weight17 =op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)), op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)), op.c_float(1.)))
        #if systematic == "DY_weight17up":
        #if systematic == "DY_weight17down":
        if systematic == "DY_weight18":
            self.DY_weight18 =op.product(op.switch( op.AND(op.in_range(20., mjj, 100.), sample in DYsamples), (0.989336 -0.0281512*mjj + 0.00159644*pow(mjj, 2) -3.26923e-05*pow(mjj, 3) + 2.91737e-07*pow(mjj, 4) -9.62316e-10*pow(mjj, 5)), op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight18up":
        #if systematic == "DY_weight18down":
        if systematic == "DY_weight21":
            self.DY_weight21 = op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)) , op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight21up":
        #if systematic == "DY_weight21down":
        if systematic == "DY_weight22":
            self.DY_weight22 = op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight22up":
        #if systematic == "DY_weight22down":
        if systematic == "DY_weight23":
            self.DY_weight23 = op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight23up":
        #if systematic == "DY_weight23down":
        if systematic == "DY_weight24":
            self.DY_weight24 = op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(450.,  mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight24up":
        #if systematic == "DY_weight24down":
        if systematic == "DY_weight25":
            self.DY_weight25 =op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight25up":
        #if systematic == "DY_weight25down":
        if systematic == "DY_weight26":
            self.DY_weight26 =op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight26up":
        #if systematic == "DY_weight26down":
        if systematic == "DY_weight27":
            self.DY_weight27 =op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight27up":
        #if systematic == "DY_weight27down":
        if systematic == "DY_weight28":
            self.DY_weight28 =op.product(op.switch( op.AND(op.in_range(100., mjj, 250.), sample in DYsamples), (3.11184 -0.0588639*mjj + 0.000610211*pow(mjj, 2) -2.93414e-06*pow(mjj, 3) + 6.46817e-09*pow(mjj, 4) -5.03036e-12*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight28up":
        #if systematic == "DY_weight28down":
        if systematic == "DY_weight31":
            self.DY_weight31 = op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight31up":
        #if systematic == "DY_weight31down":
        if systematic == "DY_weight32":
            self.DY_weight32 = op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight32up":
        #if systematic == "DY_weight32down":
        if systematic == "DY_weight33":
            self.DY_weight33 = op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight33up":
        #if systematic == "DY_weight33down":
        if systematic == "DY_weight34":
            self.DY_weight34 = op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight34up":
        #if systematic == "DY_weight34down":
        if systematic == "DY_weight35":
            self.DY_weight35 =op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight35up":
        #if systematic == "DY_weight35down":
        if systematic == "DY_weight36":
            self.DY_weight36 =op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight36up":
        #if systematic == "DY_weight36down":
        if systematic == "DY_weight37":
            self.DY_weight37 =op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight37up":
        #if systematic == "DY_weight37down":
        if systematic == "DY_weight38":
            self.DY_weight38 =op.product(op.switch( op.AND(op.in_range(250., mjj, 400.), sample in DYsamples), (-397.166 + 6.3012*mjj -0.0396388*pow(mjj, 2) + 0.000123884*pow(mjj, 3) -1.92345e-07*pow(mjj, 4) + 1.18686e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight38up":
        #if systematic == "DY_weight38down":
        if systematic == "DY_weight41":
            self.DY_weight41 = op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight41up":
        #if systematic == "DY_weight41down":
        if systematic == "DY_weight42":
            self.DY_weight42 = op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight42up":
        #if systematic == "DY_weight42down":
        if systematic == "DY_weight43":
            self.DY_weight43 = op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight43up":
        #if systematic == "DY_weight43down":
        if systematic == "DY_weight44":
            self.DY_weight44 = op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight44up":
        #if systematic == "DY_weight44down":
        if systematic == "DY_weight45":
            self.DY_weight45 =op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight45up":
        #if systematic == "DY_weight45down":
        if systematic == "DY_weight46":
            self.DY_weight46 =op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight46up":
        #if systematic == "DY_weight46down":
        if systematic == "DY_weight47":
            self.DY_weight47 =op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight47up":
        #if systematic == "DY_weight47down":
        if systematic == "DY_weight48":
            self.DY_weight48 =op.product(op.switch( op.AND(op.in_range(400., mjj, 550.), sample in DYsamples), (-2475.04 + 26.5107*mjj -0.11327*pow(mjj, 2) + 0.000241404*pow(mjj, 3) -2.56633e-07*pow(mjj, 4) + 1.08871e-10*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight48up":
        #if systematic == "DY_weight48down":
        if systematic == "DY_weight51":
            self.DY_weight51 = op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight51up":
        #if systematic == "DY_weight51down":
        if systematic == "DY_weight52":
            self.DY_weight52 = op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)),  op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight52up":
        #if systematic == "DY_weight52down":
        if systematic == "DY_weight53":
            self.DY_weight53 = op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight53up":
        #if systematic == "DY_weight53down":
        if systematic == "DY_weight54":
            self.DY_weight54 = op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight54up":
        #if systematic == "DY_weight54down":
        if systematic == "DY_weight55":
            self.DY_weight55 =op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight55up":
        #if systematic == "DY_weight55down":
        if systematic == "DY_weight56":
            self.DY_weight56 =op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight56up":
        #if systematic == "DY_weight56down":
        if systematic == "DY_weight57":
            self.DY_weight57 =op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight57up":
        #if systematic == "DY_weight57down":
        if systematic == "DY_weight58":
            self.DY_weight58 =op.product(op.switch( op.AND(op.in_range(550., mjj, 700.), sample in DYsamples), (-3400.2 + 28.1634*mjj -0.0929379*pow(mjj, 2) + 0.000152793*pow(mjj, 3) -1.25158e-07*pow(mjj, 4) + 4.08705e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight58up":
        #if systematic == "DY_weight58down":
        if systematic == "DY_weight61":
            self.DY_weight61 = op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight61up":
        #if systematic == "DY_weight61down":
        if systematic == "DY_weight62":
            self.DY_weight62 = op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight62up":
        #if systematic == "DY_weight62down":
        if systematic == "DY_weight63":
            self.DY_weight63 = op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight63up":
        #if systematic == "DY_weight63down":
        if systematic == "DY_weight64":
            self.DY_weight64 = op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight64up":
        #if systematic == "DY_weight64down":
        if systematic == "DY_weight65":
            self.DY_weight65 =op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight65up":
        #if systematic == "DY_weight65down":
        if systematic == "DY_weight66":
            self.DY_weight66 =op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight66up":
        #if systematic == "DY_weight66down":
        if systematic == "DY_weight67":
            self.DY_weight67 =op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight67up":
        #if systematic == "DY_weight67down":
        if systematic == "DY_weight68":
            self.DY_weight68 =op.product(op.switch( op.AND(op.in_range(700., mjj, 850.), sample in DYsamples), (-24674.3 + 159.938*mjj + -0.41424*pow(mjj, 2) + 0.000535871*pow(mjj, 3) + -3.46229e-07*pow(mjj, 4) + 8.93798e-11*pow(mjj, 5)) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight68up":
        #if systematic == "DY_weight68down":
        if systematic == "DY_weight71":
            self.DY_weight71 = op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)), op.c_float(1.)))
        #if systematic == "DY_weight71up":
        #if systematic == "DY_weight71down":
        if systematic == "DY_weight72":
            self.DY_weight72 = op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)), op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight72up":
        #if systematic == "DY_weight72down":
        if systematic == "DY_weight73":
            self.DY_weight73 = op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight73up":
        #if systematic == "DY_weight73down":
        if systematic == "DY_weight74":
            self.DY_weight74 = op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight74up":
        #if systematic == "DY_weight74down":
        if systematic == "DY_weight75":
            self.DY_weight75 =op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight75up":
        #if systematic == "DY_weight75down":
        if systematic == "DY_weight76":
            self.DY_weight76 =op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight76up":
        #if systematic == "DY_weight76down":
        if systematic == "DY_weight77":
            self.DY_weight77 =op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight77up":
        #if systematic == "DY_weight77down":
        if systematic == "DY_weight78":
            self.DY_weight78 =op.product(op.switch( op.AND(op.in_range(850., mjj, 1000.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight78up":
        #if systematic == "DY_weight78down":
        if systematic == "DY_weight81":
            self.DY_weight81 = op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(1000., mlljj, 1200.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight81up":
        #if systematic == "DY_weight81down":
        if systematic == "DY_weight82":
            self.DY_weight82 = op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(750., mlljj, 1000.), sample in DYsamples), (377.449 -2.2502*mlljj + 0.00537447*pow(mlljj, 2) -6.40903e-06*pow(mlljj, 3) + 3.81405e-09*pow(mlljj, 4) -9.05702e-13*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight82up":
        #if systematic == "DY_weight82down":
        if systematic == "DY_weight83":
            self.DY_weight83 = op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(600., mlljj, 750.), sample in DYsamples), (6693.66 -50.1891*mlljj + 0.150396*pow(mlljj, 2) -0.000225099*pow(mlljj, 3) + 1.68271e-07*pow(mlljj, 4) -5.02592e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight83up":
        #if systematic == "DY_weight83down":
        if systematic == "DY_weight84":
            self.DY_weight84 = op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(450., mlljj, 600.), sample in DYsamples), (2370.41 -23.004*mlljj + 0.089117*pow(mlljj, 2) -0.000172186*pow(mlljj, 3) + 1.65919e-07*pow(mlljj, 4) -6.37862e-11*pow(mlljj, 5)) , op.c_float(1.)))
        #if systematic == "DY_weight84up":
        #if systematic == "DY_weight84down":
        if systematic == "DY_weight85":
            self.DY_weight85 =op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(300., mlljj, 450.), sample in DYsamples), (3779.94 -62.4128*mlljj + 0.427584*pow(mlljj, 2) -0.00155538*pow(mlljj, 3) + 3.1685e-06*pow(mlljj, 4) -3.42748e-09*pow(mlljj, 5) + 1.53821e-12*pow(mlljj, 6)), op.c_float(1.)))
        #if systematic == "DY_weight85up":
        #if systematic == "DY_weight85down":
        if systematic == "DY_weight86":
            self.DY_weight86 =op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(150., mlljj, 300.), sample in DYsamples), (-235.825 + 7.86777*mlljj -0.107775*pow(mlljj, 2) + 0.00079528*pow(mlljj, 3) -3.43158e-06*pow(mlljj, 4) + 8.68816e-09*pow(mlljj, 5) -1.19786e-11*pow(mlljj, 6) + 6.94881e-15*pow(mlljj, 7)) , op.c_float(1.)))
        #if systematic == "DY_weight86up":
        #if systematic == "DY_weight86down":
        if systematic == "DY_weight87":
            self.DY_weight87 =op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(op.in_range(100., mlljj, 150.), sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight87up":
        #if systematic == "DY_weight87down":
        if systematic == "DY_weight88":
            self.DY_weight88 =op.product(op.switch( op.AND(op.in_range(1000, mjj, 1200.), sample in DYsamples), op.c_float(1.) , op.c_float(1.)), op.switch( op.AND(mlljj<100., sample in DYsamples), (op.c_float(1.)) , op.c_float(1.)))
        #if systematic == "DY_weight88up":
        #if systematic == "DY_weight88down":
        
def getWDY_acrossmassplane(self, uname, suffix, TwoLepTwoJetsSel_NoDYweight, mjj, mlljj, sample, systematic):
    mjj_BinEdges= [0., 100., 250., 400., 550.,700., 850., 1000., 1200.]
    inveretd_mlljj_BinEdges = [ 1200., 1000., 750., 600., 450., 300., 150., 100., 0. ]

    #f= open( os.path.join(".","DYweight_splitIn64regions.txt"),"a")
    for i in range(0,len(mjj_BinEdges)-1):
        for j in range(0,len(inveretd_mlljj_BinEdges)-1):
            if op.AND( op.in_range( mjj_BinEdges[i], mjj,  mjj_BinEdges[i+1]),
                        op.in_range(  inveretd_mlljj_BinEdges[j+1], mlljj,   inveretd_mlljj_BinEdges[j]) ):
                ij= str(i+1)+str(j+1)
                getfromDYclass = DY_weightclass(self, mjj, mlljj, sample, "DY_weight%s"%ij)
                if systematic == "nominal":
                    DY_weight = getattr(getfromDYclass , "DY_weight%s"%ij)
                    #with open(os.path.join(".","DYweight_%s_%s_%s.json"%(uname, suffix, systematic)), "w") as handle:
                    #    json.dump(DY_weight, handle, indent=4)
                    #f.write("%s, %s, %s, DYweight%s, %s\n"%(uname, sample, suffix, ij, DY_weight))

                elif systematic =="up_and_down":
                    DY_weight = op.systematic(op.c_float( getattr(getfromDYclass, "DY_weight%s"%ij)), 
                                                name="DY_weight%s"%ij, 
                                                up=op.c_float(getattr(getfromDYclass, "DY_weight%sup"%ij)), 
                                                down=op.c_float(getattr(getfromDYclass, "DY_weight%sdown"%ij)))
            else:
                DY_weight= op.systematic(op.c_float(1.), name="DY_noweight%s"%ij, up=op.c_float(0.), down= op.c_float(0.))
            sel = TwoLepTwoJetsSel_NoDYweight.refine("TwoLep_%s_atleastTwoJets_selection_%s_DY_weight%s_%s"%(uname, suffix, ij, systematic), weight= DY_weight)
    #f.close()
    return sel

def plotsWithDYReweightings(self, jets, dilepton, TwoLepTwoJetsSel_NoDYweight, uname, suffix, sample, splitDY_weightIn64Regions):
    # TODO up and down variations
    plots = []
    binScaling =1
    reweightDY_acrossmassplane = False # need to get the splitted plots first 
    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj = (dilepton[0].p4 +dilepton[1].p4+Jets_).M()
    mjj = op.invariant_mass(Jets_)
    
    mjj_BinEdges   = [0., 100., 250., 400., 550.,700., 850., 1000., 1200.]
    #mlljj_BinEdges = [0., 100., 150., 300., 450.,600., 750., 1000., 1200.]
    inveretd_mlljj_BinEdges = [ 1200., 1000., 750., 600., 450., 300., 150., 100., 0. ]
   
    #mass distribution plots not reweighted: needed for comaparaison later : better keep all plots with 0. to 1200. GeV bins 
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    
    plots.append(Plot.make1D("{0}_{1}_noDYweight_mjj".format(uname, suffix),
                op.invariant_mass(Jets_), TwoLepTwoJetsSel_NoDYweight,
                EqB(60 // binScaling, 0., 1200.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D("{0}_{1}_noDYweight_mlljj".format(uname, suffix), 
                (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), TwoLepTwoJetsSel_NoDYweight, EqBIns, 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make2D("{0}_{1}_noDYweight_mlljj_vs_mjj".format(uname, suffix), 
                (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), TwoLepTwoJetsSel_NoDYweight,
                (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 0., 1200.)), 
                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D(f"{uname}_{suffix}_noDYweight_Jet_mulmtiplicity".format(suffix=suffix), op.rng_len(jets), TwoLepTwoJetsSel_NoDYweight,
            EqB(7, 0., 7.), title="Jet mulmtiplicity",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
    
    
    for sys in ["nominal"]:#, "up_and_down"]:
        mjj_DYweight = 0.
        mlljj_DYweight = 0.
        NLO_DYweight = 0.
        for polyfit in [6, 7, 8]:
                
            mjj_DYweight = computeMjjDYweight(self, polyfit, mjj, sample)
            mlljj_DYweight = computeMlljjDYweight(self, polyfit, mlljj, sample) 
            NLO_DYweight = op.product(mjj_DYweight, mlljj_DYweight )
            
            logger.info(" start DY reweighting no mass range splits ** ")
            print (mjj_DYweight, mlljj_DYweight, NLO_DYweight)  
            # Assuming up and down variations of 100%
            if sys == "up_and_down":
                mjj_DYweight = op.systematic(op.c_float(mjj_DYweight), name="DY_weight_mjjployfit%s"%polyfit, up=op.c_float(2*mjj_DYweight-1), down= op.c_float(1.))
                mlljj_DYweight = op.systematic(op.c_float(mlljj_DYweight), name="DY_weight_mlljjpolyfit%s"%polyfit, up=op.c_float(2*mlljj_DYweight-1), down= op.c_float(1.))
                NLO_DYweight = op.systematic(op.c_float(NLO_DYweight), name="DY_weight_mjjmlljjpolyfit%s"%polyfit, up=op.c_float(2*NLO_DYweight-1), down= op.c_float(1.))
                
            
            for DYweight, mass_distribution in zip( [mjj_DYweight, mlljj_DYweight, NLO_DYweight ],['mjj', 'mlljj', 'mjjmlljj']):
                sel = TwoLepTwoJetsSel_NoDYweight.refine("add_%s_DYweight_%s_fitpolynomial%s_%s_%s"%(mass_distribution, sys, polyfit, suffix, uname), weight=(DYweight))  
            
                plots.append(Plot.make1D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_Jet_mulmtiplicity".format(uname, suffix, mass_distribution, sys, polyfit), 
                            op.rng_len(jets), sel,
                            EqB(7, 0., 7.), title="Jet mulmtiplicity",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))
    
                plots.append(Plot.make1D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_mjj".format(uname, suffix, mass_distribution, sys, polyfit),
                            op.invariant_mass(Jets_), sel,
                            EqB(60 // binScaling, 0., 1200.), 
                            title="mjj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": True})))
        
                plots.append(Plot.make1D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_mlljj".format(uname, suffix, mass_distribution, sys, polyfit),
                            (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), sel, EqBIns, 
                            title="mlljj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": True})))
                
                plots.append(Plot.make2D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_mlljjvsmjj".format(uname, suffix, mass_distribution, sys, polyfit),
                            (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), sel, 
                            (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 0., 1200.)), 
                            title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    if splitDY_weightIn64Regions: # split to reweight later 
        for i in range(0,len(mjj_BinEdges)-1):
            plots.append(Plot.make1D("{0}_{1}_DY_weight{2}_mjj".format(uname, suffix, i+1),
                    op.invariant_mass(Jets_), TwoLepTwoJetsSel_NoDYweight,
                    EqB(60 // binScaling, mjj_BinEdges[i], mjj_BinEdges[i+1]), 
                    title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
        for j in range(0,len(inveretd_mlljj_BinEdges)-1):
            plots.append(Plot.make1D("{0}_{1}_DY_weight{2}_mlljj".format(uname, suffix, j+1), 
                    (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), TwoLepTwoJetsSel_NoDYweight, 
                    EqB(60 // binScaling, inveretd_mlljj_BinEdges[j+1], inveretd_mlljj_BinEdges[j]), 
                    title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
        for i in range(0,len(mjj_BinEdges)-1):
            for j in range(0,len(inveretd_mlljj_BinEdges)-1):
                plots.append(Plot.make2D("{0}_{1}_DY{2}_mlljj_vs_mjj".format(uname, suffix, str(i+1)+str(j+1)), 
                        (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), TwoLepTwoJetsSel_NoDYweight,
                        (EqB(60 // binScaling, mjj_BinEdges[i], mjj_BinEdges[i+1]), EqB(60 // binScaling, inveretd_mlljj_BinEdges[j+1], inveretd_mlljj_BinEdges[j])), 
                        title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    
    if reweightDY_acrossmassplane:    
        for systematic in ["nominal"]:#, "up_and_down"]:
            selection= getWDY_acrossmassplane(self, uname, suffix, TwoLepTwoJetsSel_NoDYweight, mjj, mlljj, sample, systematic)
            plots.append(Plot.make1D("{0}_{1}_{2}_DYweightsplit64_mjj".format(uname, suffix, systematic),
                        mjj, selection,
                        EqBIns, title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
            plots.append(Plot.make1D("{0}_{1}_{2}_DYweightsplit64_mlljj".format(uname, suffix, systematic),
                        mlljj, selection, 
                        EqBIns, title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
        
            plots.append(Plot.make2D("{0}_{1}_{2}_DYweightsplit64_mlljjvsmjj".format(uname, suffix, systematic),
                        (mjj, mlljj), selection, 
                        (EqBIns, EqBIns), title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots
    
def Plots_gen(self, gen_ptll_nlo, sel, suffix, sample):
    plots =[]
    binScaling = 1
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    plots.append(Plot.make1D("{0}_genptll_nlo".format(suffix),
                    gen_ptll_nlo, sel,
                    EqBIns, title="gen pt [GeV]"))
        
    # follow xavier methods 
    return plots
def PLots_withtthDYweight(self, uname, dilepton, jets, sel, suffix, sample, era):
    plots =[]
    binScaling = 1
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    from systematics import get_tthDYreweighting
    nloDYweight= get_tthDYreweighting(self, era, sample, jets)
    sel.refine("%s_DY_reweighting_%s_fromtthanalysis"%(uname, suffix), weight= nloDYweight)
    
    plots.append(Plot.make1D("{0}_{1}_njets_tthDYnloweight".format(uname, suffix),
                        op.rng_len(jets), sel,
                        EqB(7, 0., 7.), title="Jet mulmtiplicity", plotopts=utils.getOpts(uname, **{"log-y": True})))
    
    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj = (dilepton[0].p4 +dilepton[1].p4+Jets_).M()
    mjj = op.invariant_mass(Jets_)

    plots.append(Plot.make1D("{0}_{1}_mjj_tthDYnloweight".format(uname, suffix),
                        mjj, sel,
                        EqBIns, title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D("{0}_{1}_mlljj_tthDYnloweight".format(uname, suffix),
                        mlljj, sel,
                        EqBIns, title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    return plots
