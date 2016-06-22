from parallel import Parallel
import os
import multiprocessing as mp
import time
from random import randint


class Custom_Parallel(Parallel):
    
    def parallel_process(self, pkg, parallel_arg):
        lock = parallel_arg
        time.sleep(float(randint(0,20))/100.)
        lock.acquire()
        print('Process # ' + str(os.getpid()) + '\tOutput: ' + str(pkg))
        lock.release()


P = Custom_Parallel(16)
P.set_work_packages(range(256))
P.set_common_args(mp.Lock())
P.begin()
P.end()
