import multiprocessing as mp


class Parallel(object):
    '''Wrapper class for SIMD parallelism. The class runs parallel_process which
    work on a single work package taken from a queue until the queue runs out
    of packages. Each process also has access to a set of common arguments shared
    across all processes.
    '''


    def __init__(self, procs=1):
        self.queue = mp.Queue()     # accessed by each process
        self.workers = []           # list of active processes
        self.procs = procs          # number of processes
        self.parallel_arg = None    # args shared between processes


    def set_work_packages(self, pkgs):
        '''get a list/set of objects that each process takes individually'''
        for pkg in pkgs:
            self.queue.put(pkg)


    def set_common_args(self, parallel):
        '''set the common parameter shared between processes'''
        self.parallel_arg = parallel


    def worker(self, queue, parallel_arg):
        '''internal function run by each process that keeps accepting packages
        until the queue runs out'''
        while not queue.empty():
            pkg = queue.get()
            self.parallel_process(pkg, parallel_arg)
        return


    def parallel_process(self, pkg, parallel_arg):
        '''this function is overridden with the custom computations to be
         performed.
         :pkg: single package to work on
         :parallel_arg: common argument shared by all processes'''
        pass


    def begin(self):
        '''starts processing after all parameters have been set'''
        for i in range(self.procs):
            p = mp.Process(target=self.__class__().worker, args=(self.queue, self.parallel_arg))
            self.workers.append(p)
            p.start()


    def end(self):
        '''waits for all processes to finish and terminates them'''
        for w in self.workers:
            w.join()
