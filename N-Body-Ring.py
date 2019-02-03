import math
import numpy as np
import time
from mpi4py import MPI
import sys

def calculateDistance(cosmos1, cosmos2, star1, star2):
    return math.sqrt(
        (cosmos1[star2][1] - cosmos2[star1][1]) ** 2 +
        (cosmos1[star2][2] - cosmos2[star1][2]) ** 2 +
        (cosmos1[star2][3] - cosmos2[star1][3]) ** 2
    ) ** 3


def getCosmosSlice(comm, rank, numberOfCores, numberOfStarsPerCore, cosmosSlice):
    if rank == 0:
        cosmos = np.load("cosmos.npy")

        inc = 1.0 * numberOfStars / numberOfCores
        begin = 0
        end = int(inc - 1)
        cur = inc
        cosmosSlice = np.zeros((numberOfStarsPerCore, 4), dtype=np.float64)

        for star in range(begin, end + 1):
            cosmosSlice[star][:] = cosmos[star]

        for core in range(1, numberOfCores):
            stars = np.zeros((numberOfStarsPerCore, 4), dtype=np.float64)

            for star in range(int(cur), int(cur + inc - 1) + 1):
                stars[star - int(cur)][:] = cosmos[star]

            indexes = (int(cur), int(cur + inc - 1))
            comm.send(indexes, dest=core)
            comm.Send([stars, numberOfStarsPerCore * 4, MPI.DOUBLE], dest=core)
            cur += inc
    else:
        indexes = comm.recv(source=0)
        begin = indexes[0]
        end = indexes[1]
        comm.Recv(cosmosSlice, source=0)

    return begin, end, cosmosSlice


def calculateCosmosAcceleration(cosmosSliceBuffer, cosmosSlice, indexes, cosmosAccelerationSlice):
    for star1 in range(indexes[1] - indexes[0] + 1):
        for star2 in range(indexes[1] - indexes[0] + 1):
            if star1 == star2:
                continue

            distance = calculateDistance(cosmosSliceBuffer, cosmosSlice, star1, star2)

            for dimension in range(3):
                cosmosAccelerationSlice[star1][dimension] += \
                    gravityConstant * \
                    cosmosSliceBuffer[star2][0] * \
                    (cosmosSliceBuffer[star2][dimension + 1] - cosmosSlice[star1][dimension + 1]) / distance


def calculateCosmosAccelerationWithRemaining(cosmosSliceBuffer, cosmosSlice, indexes, cosmosAccelerationSlice, numberOfStarsPerCore):
    for star1 in range(indexes[1] - indexes[0] + 1):
        for star2 in range(numberOfStarsPerCore):
            if cosmosSliceBuffer[star2][0] == 0:
                break

            distance = calculateDistance(cosmosSliceBuffer, cosmosSlice, star1, star2)

            for dimension in range(3):
                cosmosAccelerationSlice[star1][dimension] += \
                    gravityConstant * \
                    cosmosSliceBuffer[star2][0] * \
                    (cosmosSliceBuffer[star2][dimension + 1] - cosmosSlice[star1][dimension + 1]) / distance


def passBuffers(comm, rank, numberOfCores, numberOfStarsPerCore, cosmosSliceBuffer):
    comm.Send([cosmosSliceBuffer, numberOfStarsPerCore * 4, MPI.DOUBLE], dest=(rank - 1) % numberOfCores)
    comm.Recv(cosmosSliceBuffer, source=(rank + 1) % numberOfCores)



def joinAccelerationSlices(comm, rank, numberOfCores, numberOfStarsPerCore, cosmosAccelerationSlice, cosmosAcceleration):
    if rank == 0:
        starNumber = 0

        for starAcceleration in cosmosAccelerationSlice:
            if starAcceleration[0] == 0:
                break
            cosmosAcceleration[starNumber] = starAcceleration
            starNumber += 1

        for i in range(numberOfCores - 1):
            comm.Recv(cosmosAccelerationSlice, source=i + 1)

            for starAcceleration in cosmosAccelerationSlice:
                if starAcceleration[0] == 0:
                    break
                cosmosAcceleration[starNumber] = starAcceleration
                starNumber += 1
    else:
        comm.Send([cosmosAccelerationSlice, numberOfStarsPerCore * 3, MPI.DOUBLE], dest=0)


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    numberOfCores = comm.Get_size()

    if rank == 0:
        times = 0

    for _ in range(numberOfIteration):
        if rank == 0:
            start = time.time()

        numberOfStarsPerCore = min(int(numberOfStars / numberOfCores + 0.5) + 1, numberOfStars)

        cosmosSlice = np.zeros((numberOfStarsPerCore, 4), dtype=np.float64)
        cosmosSliceBuffer = np.zeros((numberOfStarsPerCore, 4), dtype=np.float64)
        cosmosAccelerationSlice = np.zeros((numberOfStarsPerCore, 3), dtype=np.float64)
        cosmosAcceleration = np.zeros((numberOfStars, 3), dtype=np.float64)

        begin, end, cosmosSlice = getCosmosSlice(comm, rank, numberOfCores, numberOfStarsPerCore, cosmosSlice)
        indexes = (begin, end)

        cosmosSliceBuffer[:] = cosmosSlice

        calculateCosmosAcceleration(cosmosSliceBuffer, cosmosSlice, indexes, cosmosAccelerationSlice)

        for i in range(numberOfCores - 1):
            passBuffers(comm, rank, numberOfCores, numberOfStarsPerCore, cosmosSliceBuffer)

            calculateCosmosAccelerationWithRemaining(cosmosSliceBuffer, cosmosSlice, indexes, cosmosAccelerationSlice,
                                                     numberOfStarsPerCore)

        joinAccelerationSlices(comm, rank, numberOfCores, numberOfStarsPerCore, cosmosAccelerationSlice, cosmosAcceleration)

        if rank == 0:
            times += time.time() - start
            # print("Took: ", time.time() - start)

    if rank == 0:
        # print(cosmosAcceleration)
        print("Average time: ", times / numberOfIteration)


if __name__ == '__main__':
    numberOfIteration = 10
    numberOfStars = int(sys.argv[1])
    gravityConstant = 0.0000000000667408

    main()
