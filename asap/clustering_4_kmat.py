#!/usr/bin/python3

import numpy as np
import argparse
import matplotlib.pyplot as plt
from matplotlib import cm
from lib import kpca, kerneltorho, kerneltodis
from lib import get_cluster_size, get_cluster_properties
from sklearn.cluster import DBSCAN

def main(fkmat, ftags, fcolor, prefix, kpca_d, pc1, pc2):

    # if it has been computed before we can simply load it
    try:
        eva = np.genfromtxt(fkmat, dtype=float)
    except: raise ValueError('Cannot load the kernel matrix')

    print("loaded",fkmat)
    if (ftags != 'none'): 
        tags = np.loadtxt(ftags, dtype="str")
        ndict = len(tags)

    # charecteristic difference in k_ij
    sigma_kij = np.std(eva[:,:])

    # do a low dimensional projection to visualize the data
    proj = kpca(eva,kpca_d)

    # #############################################################################
    # simple clustering schemes using DBSCAN

    # Generate sample data
    X = proj
    # Compute DBSCAN
    veps = sigma_kij
    vminsamples = 5
    db = DBSCAN(eps=veps, min_samples=vminsamples).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels_db = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels_db)) - (1 if -1 in labels_db else 0)
    n_noise_ = list(labels_db).count(-1)

    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)
    #############################################################################

    # save
    #np.savetxt(prefix+"-kpca-d"+str(kpca_d)+".coord", proj, fmt='%4.8f')

    [ unique_labels, cluster_size ]  = get_cluster_size(labels_db[ndict:])
    # center of each cluster
    [ unique_labels, cluster_x ]  = get_cluster_properties(labels_db[:],proj[:,pc1],'mean')
    [ unique_labels, cluster_y ]  = get_cluster_properties(labels_db[:],proj[:,pc2],'mean')

    # color scheme
    if (fcolor != 'none'):
        try:
            plotcolor = np.genfromtxt(fcolor, dtype=float)
        except: raise ValueError('Cannot load the vector of properties')
        if (len(plotcolor) != len(eva)): 
            raise ValueError('Length of the vector of properties is not the same as number of samples')
        colorlabel = 'use '+fcolor+' for coloring the data points'
    else: # we use the local density as the color scheme
        plotcolor = kerneltorho(eva, sigma_kij)
        colorlabel = 'local density of each data point ($\sigma(k_{ij})$ ='+"{:4.0e}".format(sigma_kij)+' )'
    [ plotcolormin, plotcolormax ] = [ np.min(plotcolor),np.max(plotcolor) ]

    # make plot
    fig, ax = plt.subplots()
    pcaplot = ax.scatter(proj[:,pc1],proj[:,pc2],c=plotcolor[:],
                    cmap=cm.summer,vmin=plotcolormin, vmax=plotcolormax)
    cbar = fig.colorbar(pcaplot, ax=ax)
    cbar.ax.set_ylabel(colorlabel)

    # plot the clusters with size propotional to population
    for k in unique_labels:
        if (k >=0):
            ax.plot(cluster_x[k],cluster_y[k], 'o', markerfacecolor='none',
                markeredgecolor='gray', markersize=10.0*(np.log(cluster_size[k])))


    # the noisy points
    if k == -1:
        # Black removed and is used for noise instead.
        # Black used for noise.
        col = [0, 0, 0, 1]
        class_member_mask = (labels_db == k)
        xy = X[class_member_mask & ~core_samples_mask]
        ax.plot(xy[:, pc1], xy[:, pc2], 'o', markerfacecolor='gray',
             markeredgecolor='k', markersize=1.5)

    # project the known structures
    if (ftags != 'none'):
        for i in range(ndict):
            ax.scatter(proj[i,pc1],proj[i,pc2],marker='^',c='black')
            ax.annotate(tags[i], (proj[i,pc1], proj[i,pc2]))

    plt.title('KPCA and clustering for: '+prefix)
    plt.xlabel('pc1')
    plt.ylabel('pc2')
    fig.set_size_inches(18.5, 10.5)
    plt.show()
    fig.savefig('Clustering_4_'+prefix+'.png')
##########################################################################################
##########################################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-kmat', type=str, required=True, help='Location of kernel matrix file. You can use gen_kmat.py to compute it.')
    parser.add_argument('-tags', type=str, default='none', help='Location of tags for the first M samples')
    parser.add_argument('-colors', type=str, default='none', help='Properties for all samples (N floats) used to color the scatter plot')
    parser.add_argument('--prefix', type=str, default='', help='Filename prefix')
    parser.add_argument('--d', type=int, default=10, help='number of the principle components to keep')
    parser.add_argument('--pc1', type=int, default=0, help='Plot the projection along which principle axes')
    parser.add_argument('--pc2', type=int, default=1, help='Plot the projection along which principle axes')
    args = parser.parse_args()

    main(args.kmat, args.tags, args.colors, args.prefix, args.d, args.pc1, args.pc2)

