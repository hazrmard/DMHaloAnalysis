import multiprocessing as mp


class Parallel:

    
    def __init__(self, procs=1):
        self.queue = mp.Queue()
        self.workers = []
        self.procs = procs
        self.parallel_arg = None

    
    def set_work_packages(self, pkgs):
        for pkg in pkgs:
            self.queue.put(pkg)

    
    def set_common_args(self, parallel):
        self.parallel_arg = parallel


    def worker(self, queue, parallel_arg):
        while not queue.empty():
            pkg = queue.get()
            self.parallel_process(pkg, parallel_arg)
        return


    def parallel_process(self, pkg, parallel_arg):
        pass


    def begin(self):
        for i in range(self.procs):
            p = mp.Process(target=self.__class__().worker, args=(self.queue, self.parallel_arg))
            self.workers.append(p)
            p.start()


    def end(self):
        for w in self.workers:
            w.join()
        
