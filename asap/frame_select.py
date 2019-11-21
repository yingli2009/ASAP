#!/usr/bin/python3
"""
TODO: Module-level description
"""

import argparse

from ase.io import read, write
from asaplib.compressor import fps
import numpy as np


def main(fxyz, fy, prefix, nkeep, algorithm, fmat):
    """

    Parameters
    ----------
    fxyz: Path to xyz file.
    fy: Path to the list of properties (N floats) or name of the tags in ase xyz file
    prefix: Filename prefix, default is ASAP
    nkeep: The number of representative samples to select
    algorithm: 'the algorithm for selecting frames ([random], [fps], [sort])')
    fmat: Location of descriptor or kernel matrix file. Needed if you select [fps].
    You can use gen_kmat.py to compute it.

    Returns
    -------

    """

    # read frames
    frames = read(fxyz, ':')
    nframes = len(frames)
    print("read xyz file:", fxyz, ", a total of", nframes, "frames")

    if nkeep == 0:
        nkeep = nframes

    if algorithm == 'random' or algorithm == 'RANDOM':
        idx = np.asarray(range(nframes))
        sbs = np.random.choice(idx, nkeep, replace=False)

    elif algorithm == 'sort' or algorithm == 'SORT':
        if fy == 'none':
            raise ValueError('must supply the vector of properties for sorting')
        y_all = []
        try:
            y_all = np.genfromtxt(fy, dtype=float)
        except:
            try:
                for frame in frames:
                    if fy == 'volume' or fy == 'Volume':
                        y_all.append(frame.get_volume()/len(frame.get_positions()))
                    elif fy == 'size' or fy == 'Size':
                        y_all.append(len(frame.get_positions()))
                    else:
                        y_all.append(frame.info[fy]/len(frame.get_positions()))
            except: raise ValueError('Cannot load the property vector')
        if len(y_all) != nframes:
            raise ValueError('Length of the vector of properties is not the same as number of samples')
        
        idx = np.asarray(range(nframes))
        sbs = [x for _, x in sorted(zip(y_all, idx))][0:nkeep]

    elif algorithm == 'fps' or algorithm == 'FPS':
        try:
            kNN = np.genfromtxt(fmat, dtype=float)
        except: raise ValueError('Cannot load the kernel matrix')
        sbs, _ = fps(kNN, nkeep, 0)

    # save
    selection = np.zeros(nframes, dtype=int)
    for i in sbs:
        write(prefix+"-"+algorithm+"-n-"+str(nkeep)+'.xyz', frames[i], append=True)
        selection[i] = 1
    np.savetxt(prefix+"-"+algorithm+"-n-"+str(nkeep)+'.index', selection, fmt='%d')
    #np.savetxt(prefix+"-"+algorithm+"-n-"+str(nkeep)+'.index', sbs, fmt='%d')
    if fy != 'none':
        np.savetxt(prefix+"-"+algorithm+"-n-"+str(nkeep)+'-'+fy, np.asarray(y_all)[sbs], fmt='%4.8f')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-fxyz', type=str, required=True, help='Location of xyz file')
    parser.add_argument('-y', type=str, default='none', help='Location of the list of properties (N floats) or name of the tags in ase xyz file')
    parser.add_argument('--prefix', type=str, default='ASAP', help='Filename prefix')
    parser.add_argument('--n', type=int, default=0, help='number of the representative samples to select')
    parser.add_argument('--algo', type=str, default='random', help='the algorithm for selecting frames ([random], [fps], [sort])')
    parser.add_argument('-mat', type=str, required=False, help='Location of descriptor or kernel matrix file. Needed if you select [fps]. You can use gen_kmat.py to compute it.')
    args = parser.parse_args()

    main(args.fxyz, args.y, args.prefix, args.n, args.algo, args.mat)
