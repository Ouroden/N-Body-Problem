import numpy as np
import sys

def generateCosmosData(numberOfStars):
    cosmos = np.random.random((numberOfStars, 4))
    np.save("cosmos", cosmos)


def main():
    numberOfStars = int(sys.argv[1])
    generateCosmosData(numberOfStars)


if __name__ == '__main__':
    main()
