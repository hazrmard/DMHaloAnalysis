from halos import Halos
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
import glob
from parallel import Parallel
import multiprocessing as mp
import time


plt.ioff()


class BatchSnapshot(Parallel):

    def __init__(self, dirpath='./', procs=1, padding=0):
        self.dirpath = dirpath
        super(BatchSnapshot, self).__init__(procs)
        if os.path.isdir(dirpath):
            dirpath = os.path.join(dirpath, '*.bgc2')
        files = glob.glob(dirpath)
        #r = temp_fix()
        self.set_work_packages(files)
        self.set_common_args((mp.Lock(), padding))

    
    def parallel_process(self, pkg, parallel_arg):
        lock = parallel_arg[0]
        padding = parallel_arg[1]
        try:
            bgc_to_png(pkg, name_padding=padding)
            lock.acquire()
            print(str(os.getpid()) + ' - ' + time.ctime() + ' : ' + os.path.split(pkg)[1] + ' : Done')
            lock.release()
        except IOError as e:
            lock.acquire()
            print(str(os.getpid()) + ' - ' + time.ctime() + ' : ' + os.path.split(pkg)[1] + ' : ' + str(e))
            lock.release()

def temp_fix():
    import config
    import re
    snaps = glob.glob('output/*.png')
    snap_files = [int(os.path.split(p)[1][:-4]) for p in snaps]
    bgc = glob.glob(config.PATH+'*.bgc2')
    bgc_files = []
    for f in bgc:
      res = re.search('.*_([0-9]+)\.bgc2$', f)
      if int(res.group(1)) not in snap_files:
          bgc_files.append(f)
    return bgc_files

def bgc_to_png(path, axes='xy', resolution=1024, outputdir='output', name_padding=0):
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


def job():
    import config
    print('Instantiating BatchSnapshot')
    B = BatchSnapshot(config.PATH+'*.bgc2', 8, 5)
    B.begin()
    B.end()


if __name__=='__main__':
    job()
