#!/usr/bin/python3

'''
This script will print the 12 scales of western music in various permutations.

This could be used to help in training on playing pieces in all these scales
and avoiding going through them always in the same cycle of fifths.
'''

###########
# imports #
###########
import random  # for seed, shuffle

#############
# functions #
#############

########
# code #
########
# for deterministic behaviour
#random.seed(7)
l = [ 'C', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb/F#', 'B', 'E', 'A', 'D', 'G']
random.shuffle(l)
print(l)
