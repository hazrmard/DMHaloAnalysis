from halos import Halos
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os


plt.ioff()

def bgc_to_png(path, axes='xy', resolution=1024, outputdir='output'):
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
    #plt.imshow(hist_array, cmap=plt.cm.binary)
    fig = plt.figure(dpi=100, tight_layout=True, frameon=False, figsize=(resolution/100.,resolution/100.))
    #fig.imshow(hist_array)
    fig.figimage(hist_array)
    #plt.axis('off')
    #fig = plt.gcf()
    #fig.gca().set_frame_on(False)
    #fig.set_size_inches(resolution/10.,resolution/10.)
    plt.savefig(os.path.join(outputdir, str(H.header[0].snapshot)+'.png'))


def test():
    import config
    bgc_to_png(config.PATH+'*100.bgc2')


if __name__=='__main__':
    test()
