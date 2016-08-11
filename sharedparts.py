from halos import Halos, Halo, helpers
from parallel import Parallel
import multiprocessing as mp
import glob
import os
import csv
import numpy as np
import argparse
import time

class SharedParticles(Parallel):

    def __init__(self, files='./', file_group_level=0, output='output'+os.sep+'shared.csv',
                procs=1, _req_file_check=True, _type='main'):
        super(SharedParticles, self).__init__(procs, _type)
        if os.path.isdir(files):
            files = os.path.join(files, '*.bgc2')
        if not os.path.isdir(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))
        self.results_queue = mp.Queue()
        self.set_work_packages(files, file_group_level)
        self.set_common_args((mp.Lock(), self.results_queue))
        self.output = output

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
            super(SharedParticles, self).set_work_packages(expanded_pkgs)

    def shared_particles(self, filepath):
        H = Halos(filepath, verbose=False)
        H.read_data(level=2)
        s = set([])
        unique = 0.
        total = 0.
        for halo in H.halos:
            total += len(halo.particles.id)
            s.update(halo.particles.id)
        unique = len(s)
        snap = H.header[0].snapshot
        shared = 1. - (unique/total)  # fraction of particles that are shared
        return (snap, shared)

    def parallel_process(self, pkg, parallel_arg):
        lock = parallel_arg[0]
        results_queue = parallel_arg[1]
        try:
            ans = self.shared_particles(pkg)
            results_queue.put(ans)
            lock.acquire()
            print(str(os.getpid()) + ' - ' + time.ctime() + ': ' + 'Done - Snapshot:'+ str(ans[0]) \
                        + '\tShared '+ '{0:.3}'.format(ans[1]))
            lock.release()
        except Exception as e:
            lock.acquire()
            print(str(os.getpid()) + ' - ' + time.ctime() + ': ' + str(e))
            lock.release()
        return

    def post_process(self):
        res = []
        while not self.results_queue.empty():
            res.append(self.results_queue.get())
        arr = np.array(res, dtype=np.dtype([('snapshot', np.int32), ('shared', np.float64)]))
        arr.sort(order='snapshot')
        print('\nFinal Report:')
        print('Average shared across snapshots: ' + '{0:.3f}'.format(np.mean(arr['shared'])))

        with open(self.output, 'wb') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(['Snapshot', 'Fraction shared'])
            w.writerows(arr)


if __name__=='__main__':
    a = argparse.ArgumentParser(prog="Calculate shared particles in halos",
        description='Tally the fraction of particles (by id) that occur in multiple\
                    halos in a single snapshot.')
    a.add_argument('-n', help='Number of processes. Default: 1.', type=int, default=1)
    a.add_argument('-p', help='Directory of BGC2 files. Accepts wildcards. Default: current directory.', type=str, default='./')
    a.add_argument('-o', help='Output file. Default: output/shared.csv', type=str, default='output/shared.csv')
    a.add_argument('-g', help='Group files w/ shared subversion numbers. Default: all files separate.', type=int, default=0)
    args = a.parse_args()
    S = SharedParticles(files=args.p, output=args.o, procs=args.n, file_group_level=args.g)
    S.begin()
    S.end()
    S.post_process()