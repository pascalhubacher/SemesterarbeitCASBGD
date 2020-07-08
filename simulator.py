#
import time
import math
import itertools

from multiprocessing import Pool

# 2 x 11 players and the ball
NUM_PROCESSES = 23

def calc(num_elements):
    res = 0
    for i in range(num_elements):
        res += math.sqrt(i)
    print(res)

def main():
    start_time = time.perf_counter()

    with Pool(processes=NUM_PROCESSES) as pool:
        pool.map(calc, itertools.repeat(8_000_000, NUM_PROCESSES))

    end_time = time.perf_counter()
    print("Took: {} s".format(end_time - start_time))

if __name__ == "__main__":
    main()