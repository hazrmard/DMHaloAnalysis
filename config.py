from __future__ import division
import matplotlib
matplotlib.use('Agg')
import numpy as np

# for personal convenience, not used anywhere in code
PATH = "/fs2/shared/new_130_mpc_box/hires/5045/rockstar_halos/so_m200b/full_res/bgc2_halocats/" # w/o particle data
HI_RES_PATH = "/fs1/sinham/new_130_mpc_box/midres/5045/so_mvir/"    # w/ particle data


LIST_PARENTS_BASENAME = 'out_'
LIST_PARENTS_EXT = '.list.parents'
LIST_PARENTS_FORMAT = { 'names': True,
                        'usecols': (0, -1),
                        'comments': '#',
                        'delimiter': None,
                        'replace_space': '_',
                        'dtype': int,
                        }

SHARED_CSV_DTYPE = np.dtype([('redshift', float), ('shared', float)])


DPI = 100
RESOLUTION = 1366
INCHES = RESOLUTION / DPI
INPUT_DIR = './'
OUTPUT_DIR = 'output'
