A data set of 15,869 distinct PBE-DFT geometry-optimised ice structures obtained from the paper
"Mapping uncharted territory in ice from zeolite networks to ice structures" 
Nature Communicationsvolume 9, Article number: 2173 (2018)

#
* step 1
gen_soap_descriptors.py -fxyz ice-dataset.xyz --rcut 4 --n 4 --l 6 --g 0.2 --periodic True

* step 2
../../asap/pca.py -fmat ASAP-n4-l6-c4.0-g0.2.desc -color ice-properties.dat --colorscolumn 3