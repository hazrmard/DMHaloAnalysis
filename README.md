# DMHaloAnalysis
Analysis of dark matter simulation data generated by [Rockstar Halo Finder](https://bitbucket.org/gfcstanford/rockstar). This repository contains some tools developed to analyze halo files in `bgc2` format. All tools are designed to run on multiple cores.  

## Tools  
The following tools have been developed thus far:  
* `snapshot`: convert a set of `bgc2` files into `png` files. They can be later converted into a video using ffmpeg.  
* `sharedparts`: get the proportion of particles in halos that are shared with other halos.
  

## Dependencies
* Numpy
* Matplotlib
* [DarkMatterHalos](https://github.com/hazrmard/DarkMatterHalos) (for i/o)

## Usage

#### Snapshot  
`snapshot.py` plots the positions of all halos on an area corresponding to the simulation box size. Output is a png file with the redshift number superimposed on the image.
```
> python snapshot.py -h     # gives list of arguments and defaults
> python snapshot.py -p DIRPATH -n NPROCS -o OUTDIR -r RESOLUTION -z 0-padding
```
  
The output when stitched together with `ffmpeg` looks like this (youtube link): [![Youtube](http://img.youtube.com/vi/kF8a1zNXSQk/0.jpg)](http://www.youtube.com/watch?v=kF8a1zNXSQk)
#### Sharedparts  
`sharedparts.py` counts the frequency with which particles are shared between Friends-of-Friends halos as determined by the [Rockstar Halo Finder application](https://bitbucket.org/gfcstanford/rockstar). Output is stored in a csv file containing snapshot # and frequency: `(total particles - unique particles) / unique particles`.
```
> python shardparts.py -h     # gives list of arguments and defaults
> python sharedparts.py -p DIRPATH -n NPROCS -o OUTFILE -g GROUPING    # generates .csv and .png files
> python sharedparts.py -p DIRPATH -o OUTFILE --visualize              # converts existing csv to png
```
  
Output of this script looks like this:  
<img src="https://raw.githubusercontent.com/hazrmard/DMHaloAnalysis/master/shared_output_sample.png" width="480"/>
