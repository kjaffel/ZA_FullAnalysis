import sys
import logging
import os
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def PlotScans(data,path,tag):
    logging.debug('Data from csv')
    logging.debug(data)
    sns.set(rc={'figure.figsize':(16,9)})

    # Parameters barplot #
    g = sns.relplot(x="hidden_layers",
                y="val_loss",
                col="first_neuron",
                hue="activation",
                style="activation",
                data=data);
    g.set(yscale="log");
    g.set(ylim=(0.1, None))
    plt.savefig(os.path.join(path,'barplot_neuron_hidden_activation_'+tag+'.png'))

    g = sns.relplot(x="hidden_layers",
                y="val_loss",
                hue="output_activation",
                style="output_activation",
                data=data);
    g.set(yscale="log");
    g.set(ylim=(0.1, None))
    plt.savefig(os.path.join(path,'barplot_hidden_last_activation_'+tag+'.png'))
   #plt.show()

    g = sns.relplot(x="l2",
                y="val_loss",
                col='dropout',
                data=data);
    g.set(yscale="log");
    g.set(ylim=(0.1, None))
    plt.savefig(os.path.join(path,'l2_dropout_'+tag+'.png'))


    # Lr batch catplot #
    g = sns.catplot(x="lr", 
                y="val_loss",
                hue="batch_size",
                kind="swarm",
                data=data);
    g.set(ylim=(0.1, None))
    g.set(yscale="log");
    #plt.show()
    plt.savefig(os.path.join(path,'cat_plot_lr_batch_'+tag+'.png'))
    
    # Pairplot #
    sns.pairplot(data=data, 
                 hue="hidden_layers");
    plt.savefig(os.path.join(path,'pairplot_hidden_'+tag+'.png'))
    
    # LMplot # 
    sns.lmplot(x="val_loss",
               y="loss", 
               col="hidden_layers",
               hue="first_neuron",
               data=data);
    plt.savefig(os.path.join(path,'reg_loss_'+tag+'.png'))                                                                                                                                               

    sns.kdeplot(data.lr, data.batch_size , cmap="Blues", shade=True, shade_lowest=True);
    plt.savefig(os.path.join(path,'kde_lr_batch_'+tag+'.png'))                                                                                                                                               

    # joinplot eval_erro val_loss #
    g = sns.lmplot(x='val_loss', y='val_loss',
                   truncate=True, height=5, data=data)
    plt.savefig(os.path.join(path,'val_loss_vs_val_loss_'+tag+'.png'))
    


