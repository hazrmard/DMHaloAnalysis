# DMHaloAnalysis
Analysis of dark matter simulation data. This repository contains some tools
developed to analyze halo files in `bgc2` format.  

## Tools  
The following tools have been developed thus far:  
* `snapshot`: convert a set of `bgc2` files into `png` files. They can be later
converted into a video using ffmpeg.  

## Dependencies
* Numpy
* Matplotlib
* (DarkMatterHalos)[https://github.com/hazrmard/DarkMatterHalos] (for i/o)

## Usage

#### Snapshot  
```
> python snapshot.py -h     # gives list of arguments and defaults
> python snapshot.py -d DIRPATH -n NPROCS -o OUTDIR -r RESOLUTION -p 0-padding
```
