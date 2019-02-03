#!/bin/bash

for stars in 10 20 30 40 50 100 150 200 300 400 500; do
	printf "#####################################################\n"
	printf "Number of stars: $stars\n"
	printf "#####################################################\n\n"
	python CosmosGenerator.py $stars

	printf "python N-Body-Sequential.py $stars\n"
	python N-Body-Sequential.py $stars

	for number_of_cores in {1..4}; do
		printf "\nmpiexec -np $number_of_cores python N-Body-Ring.py $stars\n"
		mpiexec -np $number_of_cores python N-Body-Ring.py $stars
	done
	printf "\n"
done
