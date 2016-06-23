from halos import Halos
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os


plt.ioff()

def bgc_to_png(path, axes='xy', resolution=1024, outputdir='output'):
    if not os.path.isdir(outputdir):
        os.makedirs(outputdir)
    H = Halos(path)
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
    mpimg.imsave(os.path.join(outputdir, str(H.header[0].snapshot)+'.png'), hist_array)
