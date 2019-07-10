#!/usr/bin/python3

import random

days = 1

start_mu = 9 * 60
start_sigma = 120

work_mu = 3 * 60
work_sigma = 120

hole_mu = 2 * 60
hole_sigma = 120

sets_a_day = 3


def make_hour(e, v, add=0):
    t = -5
    while t < 0:
        t = random.normalvariate(e, v)
    return add+t

def print_time(t):
    # print(t)
    print("{}:{:02d}".format(int(t//60), int(t%60)), end="")


for i in range(days):
    now = make_hour(start_mu, start_sigma)
    s = 0
    for j in range(sets_a_day):
        print_time(now)
        b = now
        now = make_hour(work_mu, work_sigma, now)
        s += now-b
        print(" - ", end="")
        print_time(now)
        print()
        now = make_hour(hole_mu, hole_sigma, now)
    print_time(s)
