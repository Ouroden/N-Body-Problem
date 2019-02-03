import math
import numpy as np
import time
import sys

def calculateDistance(cosmos, star1, star2):
    return math.sqrt(
        (cosmos[star2][1] - cosmos[star1][1]) ** 2 +
        (cosmos[star2][2] - cosmos[star1][2]) ** 2 +
        (cosmos[star2][3] - cosmos[star1][3]) ** 2
    ) ** 3


def calculateCosmosAcceleration(cosmos):
    cosmosAcceleration = np.zeros((numberOfStars, 3), dtype=np.float64)

    for star1 in range(numberOfStars):
        for star2 in range(numberOfStars):
            if star1 == star2:
                continue

            distance = calculateDistance(cosmos, star1, star2)

            for dimension in range(3):
                cosmosAcceleration[star1][dimension] +=\
                    gravityConstant *\
                    cosmos[star2][0] *\
                    (cosmos[star2][dimension + 1] - cosmos[star1][dimension + 1]) / distance

    return cosmosAcceleration


def main():
    for _ in range(numberOfIterations):

        cosmos = np.load("cosmos.npy")

        cosmosAcceleration = calculateCosmosAcceleration(cosmos)

        # print("cosmosAcceleration:\n", cosmosAcceleration)


if __name__ == '__main__':
    start = time.time()

    numberOfStars = int(sys.argv[1])
    numberOfIterations = 10
    gravityConstant = 0.0000000000667408

    main()
    print("Average time: ", (time.time() - start) / numberOfIterations)
