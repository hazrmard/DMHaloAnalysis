from halos import Halos, Halo, helpers
from parallel import Parallel
import multiprocessing as mp
import glob
import os
import csv
import numpy as np
import argparse
from datetime import datetime
import config

class SharedParticles(Parallel):

    def __init__(self, files='./', file_group_level=0, output='output_shared'+os.sep+'shared.csv',
                list_parents_path='', procs=1, _type='main'):
        super(SharedParticles, self).__init__(procs, _type)
        if os.path.isdir(files):
            files = os.path.join(files, '*.bgc2')
        if not os.path.isdir(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))
        self.results_queue = mp.Queue()
        self.set_work_packages(files, file_group_level)
        self.set_common_args((mp.Lock(), self.results_queue))
        self.output = output
        self.list_parents_path = list_parents_path

    def set_work_packages(self, pkgs, file_group_level=0):
        """
        :pkgs: wildcard file name for *.bgc2 files
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
        """This function compares the the sharing frequency of unique particles
        in distinct halos (Friends-Of-Friends halos). The frequency is:
            (total particles - unique particles) / unique particles
        """
        halo_filter = None  # initially allow all halos
        if not self.list_parents_path=='':
            temp_H = Halos(filepath, verbose=False) # read only header for snapshot
            temp_H.read_data(level=0)
            halo_filter = self.only_fof_halos(snapshot=temp_H.header[0].snapshot)   # get list of FOF halo ids
        H = Halos(filepath, verbose=False)
        H.read_data(level=2, sieve=halo_filter)    # read all data w/ filter
        s = set([])
        unique = 0.
        total = 0.
        for halo in H.halos:
            total += len(halo.particles.id)
            s.update(halo.particles.id)
        unique = len(s)
        snap = H.header[0].snapshot
        shared = (total / unique) - 1.  # fraction of particles that are shared
        return (snap, shared)

    def parallel_process(self, pkg, parallel_arg):
        lock = parallel_arg[0]
        results_queue = parallel_arg[1]
        try:
            ans = self.shared_particles(pkg)
            results_queue.put(ans)
            lock.acquire()
            print(str(os.getpid()) + ' - ' + str(datetime.now()) + ': ' + 'Done - Snapshot:'+ str(ans[0]) \
                        + '\tShared '+ '{0:.3}'.format(ans[1]))
            lock.release()
        except Exception as e:
            lock.acquire()
            print(str(os.getpid()) + ' - ' + str(datetime.now()) + ': ' + str(e))
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

    def only_fof_halos(self, snapshot):
        """identifies which halos in a snapshot have a Friends-Of-Friends
        relationship. It does this by reading 'out_SNAPSHOT.list.parent' files
        output by Rockstar's find_parents utility:
        (https://bitbucket.org/gfcstanford/rockstar#markdown-header-host-subhalo-relationships)
        """
        fof_ids = []
        fname = os.path.join(self.list_parents_path,
                config.LIST_PARENTS_BASENAME+str(snapshot)+config.LIST_PARENTS_EXT)
        data = np.genfromtxt(fname, **config.LIST_PARENTS_FORMAT)
        data = [h['ID'] for h in data if h['PID']==-1] #PID=>ParentID=-1 for FOF halos
        return data


if __name__=='__main__':
    a = argparse.ArgumentParser(prog="sharedparts.py",
        description='Tally the fraction of particles (by id) that occur in multiple\
                    halos in a single snapshot.')
    a.add_argument('-n', help='Number of processes. Default: 1.', type=int, default=1)
    a.add_argument('-p', help='Directory of BGC2 files. Accepts wildcards. Default: current directory.', type=str, default='./')
    a.add_argument('-g', help='Group files w/ shared subversion numbers. Default: all files separate.', type=int, default=0)
    a.add_argument('-o', help='Output file. Default: output_shared/shared.csv', type=str, default='output_shared/shared.csv')
    a.add_argument('-l', help='Directory of \'.list.parents\' files. Filenames should have snapshot #s. Default: empty', type=str, default='')
    args = a.parse_args()
    starttime = datetime.now()
    print('Started:\t' + str(starttime))
    S = SharedParticles(files=args.p, output=args.o, procs=args.n, file_group_level=args.g, list_parents_path=args.l)
    S.begin()
    S.end()
    S.post_process()
    endtime = datetime.now()
    print('\nEnded:\t\t' + str(endtime))
    print('Duration:\t' + str(endtime-starttime))
