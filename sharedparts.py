import config
from halos import Halos, Halo, helpers
from parallel import Parallel
import multiprocessing as mp
import glob
import os
import csv
import numpy as np
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import argparse
from datetime import datetime

class SharedParticles(Parallel):

    def __init__(self, files='./', file_group_level=0, output='output_shared'+os.sep+'shared.csv',
                procs=1, _type='main'):
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
        halo_filter = self.only_fof_halos(filepath)
        H = Halos(filepath, verbose=False)
        H.read_data(level=2, sieve=halo_filter, onlyid=True)    # read all data w/ filter
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


    def only_fof_halos(self, filepath):
        """identifies which halos in a snapshot have a Friends-Of-Friends
        relationship. It does this by checking the parent_id attribute in
        halo group data. If ==-1 then FOF halo.
        """
        temp_H = Halos(filepath, verbose=False) # read only header for snapshot
        temp_H.read_data(level=1)
        fof_halos = [halo.id for halo in temp_H.h if halo.parent_id==-1]
        return fof_halos


    @staticmethod
    def visualize(data, outfile):
        """create graphs based on csv output
        """
        if type(data) is str:
            dfile = glob.glob(data)
            data = np.array([], dtype=config.SHARED_CSV_DTYPE)
            for f in dfile:
                with open(f, 'rb') as csvfile:
                    has_header = csv.Sniffer().has_header(csvfile.read(1024))
                    csvfile.seek(0)
                    r = csv.reader(csvfile)
                    if has_header:
                        r.next()
                    data = np.append(data, np.array([(float(row[0]), float(row[1])*100) for row in r], dtype=config.SHARED_CSV_DTYPE))
        else:
            data = np.array([(float(row[0]), float(row[1])*100) for row in data], dtype=config.SHARED_CSV_DTYPE)

        f = Figure(dpi=config.DPI, figsize=(config.INCHES, config.INCHES))
        canvas = FigureCanvas(f)

        # ax_scatter = f.add_subplot(211)
        ax_scatter = f.add_subplot(111)
        ax_scatter.set_xlabel('Redshift', size='small')
        ax_scatter.set_ylabel('Shared / %', size='small')
        ax_scatter.set_title('Shared particle vs. Redshift', size='medium')
        ax_scatter.set_xlim([0, max(data['redshift'])])
        ax_scatter.set_ylim([0, max(data['shared'])])
        ax_scatter.grid(True, 'both')
        ax_scatter.scatter(data['redshift'], data['shared'])

        divider = make_axes_locatable(ax_scatter)
        ax_hist = divider.append_axes('right', 0.2*config.INCHES, sharey=ax_scatter, pad=config.INCHES*0.02)
        [label.set_visible(False) for label in ax_hist.get_yticklabels()]
        ax_hist.set_xlabel('Relative frequency', size='small')
        ax_hist.set_title('Shared particle distribution', size='medium')
        ax_hist.set_ylim([0, max(data['shared'])])
        ax_hist.grid(True, 'both')
        ax_hist.hist(data['shared'], bins=50, normed=True, orientation='horizontal',
                        color='r', histtype='step')

        ax_hist = divider.append_axes('top', 0.2*config.INCHES, sharex=ax_scatter, pad=config.INCHES*0.04)
        [label.set_visible(False) for label in ax_hist.get_xticklabels()]
        ax_hist.set_ylabel('Relative frequency', size='small')
        ax_hist.set_title('Redshift distribution', size='medium')
        ax_hist.set_xlim([0, max(data['redshift'])])
        ax_hist.grid(True, 'both')
        ax_hist.hist(data['redshift'], bins=50, normed=True, orientation='vertical',
                        color='g', histtype='step')

        canvas.print_figure(outfile, dpi=config.DPI, bbox_inches='tight')


    def parallel_process(self, pkg, parallel_arg):
        """wrapper for shared_particles() and the function in Parallel class to
        be overridden.
        """
        lock = parallel_arg[0]
        results_queue = parallel_arg[1]
        try:
            ans = self.shared_particles(pkg)
            results_queue.put(ans)
            with lock:
                print(str(os.getpid()) + ' - ' + str(datetime.now()) + ': ' + 'Done - Snapshot:'+ str(ans[0]) \
                            + '\tShared '+ '{0:.3}'.format(ans[1]))
        except Exception as e:
            with lock:
                print(str(os.getpid()) + ' - ' + str(datetime.now()) + ': ' + str(e))
        return


    def post_process(self):
        """storing returned data from parallel process in a csv file
        """
        res = []
        while not self.results_queue.empty():
            res.append(self.results_queue.get())
        arr = np.array(res, dtype=np.dtype([('snapshot', np.int32), ('shared', np.float64)]))
        arr.sort(order='snapshot')
        print('\nFinal Report:')
        print('Average shared across snapshots: ' + '{0:.3f}'.format(np.mean(arr['shared'])))

        with open(self.output+'.csv', 'wb') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(['Snapshot', 'Fraction shared'])
            w.writerows(arr)

        self.visualize(arr, self.output)



if __name__=='__main__':
    a = argparse.ArgumentParser(prog="sharedparts.py",
        description='Tally the fraction of particles (by id) that occur in multiple\
                    halos in a single snapshot. Convert data to graphs.')
    a.add_argument('-n', metavar='NUMTHREAD', help='Number of processes. Default: 1.', type=int, default=1)
    a.add_argument('-p', metavar='INPUTPATH', help='Directory of input files. Either BGC2 or .csv (for visualize). Accepts wildcards. Default: ' + config.INPUT_DIR, type=str, default=config.INPUT_DIR)
    a.add_argument('-g', metavar='GROUPVERSIONS', help='Group files w/ shared subversion numbers (1=>x.y.*). Default: all files separate.', type=int, default=0)
    a.add_argument('-o', metavar='OUTPATH', help='Output file name (no ext.). Default: ' + config.OUTPUT_DIR + '/shared.[csv|png]', type=str, default=config.OUTPUT_DIR + '/shared')
    a.add_argument('--visualize', help='Visualize already stored output (.csv) as graphs.', action='store_true')
    args = a.parse_args()
    starttime = datetime.now()
    print('Started:\t' + str(starttime) + '\n')
    if args.visualize:
        SharedParticles.visualize(args.p, args.o)
    else:
        S = SharedParticles(files=args.p, output=args.o, procs=args.n, file_group_level=args.g)
        S.begin()
        S.end()
        S.post_process()
    endtime = datetime.now()
    print('\nEnded:\t\t' + str(endtime))
    print('Duration:\t' + str(endtime-starttime))
