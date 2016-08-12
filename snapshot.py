from halos import Halos
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
import glob
from parallel import Parallel
import multiprocessing as mp
from datetime import datetime
import argparse


plt.ioff()  # turn interactive mode off


class BatchSnapshot(Parallel):
    '''class that takes a directory of bgc2 files and converts them to png files
        with a certain 0-padding over some number of processes'''
    def __init__(self, dirpath='./', procs=1, padding=0, resolution=1024, output='output', \
                file_group_level=0, _type='main'):
        self.dirpath = dirpath
        super(BatchSnapshot, self).__init__(procs, _type)
        if os.path.isdir(dirpath):
            dirpath = os.path.join(dirpath, '*.bgc2')
        self.set_work_packages(dirpath, file_group_level)
        self.set_common_args((mp.Lock(), padding, resolution, output))

    def set_work_packages(self, pkgs, file_group_level=0):
        """:pkgs: wildcard file name for *.bgc2 files
        :file_group_level: what subversion # to group files on i.e.1.*.* or 1.1.*,
            =0 means all files are separate."""
        if self._type == 'main':
            if file_group_level==0:
                expanded_pkgs = glob.glob(pkgs)
                if len(expanded_pkgs)==0:
                    raise IOError('No matching files found. Make sure path to files is correct')
            elif file_group_level>0:
                expanded_pkgs = helpers.generate_file_groups(pkgs, file_group_level, ignore_ext=True)
            super(BatchSnapshot, self).set_work_packages(expanded_pkgs)

    def parallel_process(self, pkg, parallel_arg):
        lock = parallel_arg[0]
        padding = parallel_arg[1]
        res = parallel_arg[2]
        output = parallel_arg[3]
        try:
            bgc_to_png(pkg, name_padding=padding, resolution=res, outputdir=output)
            lock.acquire()
            print(str(os.getpid()) + ' - ' + str(datetime.now()) + ' : ' + os.path.split(pkg)[1] + ' : Done')
            lock.release()
        except IOError as e:
            lock.acquire()
            print(str(os.getpid()) + ' - ' + str(datetime.now()) + ' : ' + os.path.split(pkg)[1] + ' : ' + str(e))
            lock.release()


# def temp_fix():
#   '''returns a list of bgc2 files not yet converted to png due to program
#        crash. Naming conventions used are specific to my case.'''
#     import config
#     import re
#     snaps = glob.glob('output/*.png')
#     snap_files = [int(os.path.split(p)[1][:-4]) for p in snaps]
#     bgc = glob.glob(config.PATH+'*.bgc2')
#     bgc_files = []
#     for f in bgc:
#       res = re.search('.*_([0-9]+)\.bgc2$', f)
#       if int(res.group(1)) not in snap_files:
#           bgc_files.append(f)
#     return bgc_files

def bgc_to_png(path, axes='xy', resolution=1024, outputdir='output', name_padding=0):
    '''converts a single bgc2 file to png. Outputs are named <snapshot #>.png
        :path: filepath to bgc2 file,
        :axes: axes to take the snapshot across, xy means looking into the page from z,
        :resolution: number of bins to use along each axis to put halos in, also res. of output pic,
        :outputdir: name of output directory
        :name_padding: number of zeroes to pad outputfiles with
    '''
    if not os.path.isdir(outputdir):
        os.makedirs(outputdir)
    H = Halos(path, verbose=False)
    H.read_data(level=1, strict=True)
    coords = []
    for c in axes:
        if c=='x':
            coords.append(np.array([halo.x for halo in H.h]))
        elif c=='y':
            coords.append(np.array([halo.y for halo in H.h]))
        elif c=='z':
            coords.append(np.array([halo.z for halo in H.g]))
    hist_array, _, _ = np.histogram2d(coords[0], coords[1], bins=resolution,
                        range=[[0,H.header[0].box_size], [0, H.header[0].box_size]])
    #mpimg.imsave(os.path.join(outputdir, str(H.header[0].snapshot)+'.png'), hist_array, cmap=plt.cm.binary)
    fig = plt.figure(dpi=100, tight_layout=True, frameon=False, figsize=(resolution/100.,resolution/100.))
    fig.figimage(hist_array, cmap=plt.cm.binary)
    fig.text(0.8,0.1,'z=%.3f' % H.header[0].redshift, size='medium', backgroundcolor='white', alpha=0.5)
    plt.savefig(os.path.join(outputdir, str(H.header[0].snapshot).zfill(name_padding)+'.png'))
    plt.close(fig)


if __name__=='__main__':
    a = argparse.ArgumentParser(prog="snapshot.py",
        description='Convert a directory of snapshots in BGC2 format to PNG \
                    over multiple processes')
    a.add_argument('-n', help='Number of processes. Default: 1.', type=int, default=1)
    a.add_argument('-r', help='Resolution of output in pixels. Default: 1024.', type=int, default=1024)
    a.add_argument('-p', help='Directory of BGC2 files. Accepts wildcards. Default: current directory.', type=str, default='./')
    a.add_argument('-z', help='Size of 0-padding out output files. Default: 0.', type=int, default=0)
    a.add_argument('-o', help='Output directory. Default: output/', type=str, default='output/')
    a.add_argument('-g', help='Group files w/ shared subversion numbers. Default: all files separate.', type=int, default=0)
    args = a.parse_args()
    starttime = datetime.now()
    print('Started:\t' + str(starttime))
    P = BatchSnapshot(dirpath=args.p, procs=args.n, resolution=args.r, output=args.o, padding=args.z, file_group_level=args.g)
    P.begin()
    P.end()
    endtime = datetime.now()
    print('\nEnded:\t\t' + str(endtime))
    print('Duration:\t' + str(endtime-starttime))
