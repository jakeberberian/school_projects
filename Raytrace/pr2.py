#!/bin/python
# MATH 465/665 Fall 2020 Project 2 - Dr. Dietz
#
# Copyright (c) 2016 by Michael Robinson <michaelr@american.edu>
# Permission is granted to copy and modify for educational use, provided that this notice is retained
# Permission is NOT granted for all other uses -- please contact the author for details

# Load the necessary modules
from math import *
import numpy as np

## REMOVE THE FOLLOWING LINE ONCE YOU'RE DONE WRITING YOUR ANSWERS!
# import pr2_key

# Problem 2

def evalpoly(a,x):
    """Evaluate a polynomial at x given a list of coefficients (highest degree first)"""

    total, pow = 0, 0

    for i in reversed(a):
        total += (x ** pow) * i
        pow += 1

    return total

#    return pr2_key.evalpoly(a,x)


def polyder(a):
    """Compute the derivative of a polynomial, represented as a list of coefficients (highest degree first)"""
    total = 1
    poly = a[:-1]
    n = len(poly) - 1

    for i in range(len(poly)):
        poly[n - i] *= total
        total = total * (i + 2) // (i + 1)
    return poly

#    return pr2_key.polyder(a)

# Problem 3
def rayangle(x_,y_,a,x):
    """Compute angle of incidence or reflection
    angle=rayangle(x_,y_,a,x)

    Input: x_,y_ = location of source or camera
        a     = list of coefficients of polynomial mirror
                (highest degree first)
        x     = location along the mirror (in x-axis) to
                compute angle
    Output: angle = angle of incidence/reflection (in radians)"""

    x1, y1 = x, evalpoly(a, x)

    normal = atan2(1, -evalpoly(polyder(a), x))

    theta1 = atan2(y1 - y_, x1 - x_)

    if abs(normal - theta1) <= pi:
        return abs(normal - theta1)
    else:
        return abs((2 * pi + theta1) - normal)

#    return pr2_key.rayangle(x_,y_,a,x)

# Problem 4

def angleBetween(xs,ys,xc,yc,a,x):
    # Optional helper function. You are not required to use this.

    theta_source = rayangle(xs, ys, a, x)
    theta_camera = rayangle(xc, yc, a, x)

    return theta_source - theta_camera

def findRoot(x0,y0,x1,y1):
    # Optional helper function. You are not required to use this.
    if x1 == x0:
        return NaN

    m = (y0 - y1) / (x0 - x1)
    x = (-y1 / m) + x1

    return x

def raytrace(x_s,y_s,x_c,y_c,a,x_guess):
    """Compute reflection location on polynomially-curved mirror

    x,y = raytrace(x_s,y_s,x_c,y_c,a,x_guess)

    Input:
       x_s,y_s = is the location of the source
       x_c,y_c = is the location of the camera
       a       = is a vector of length N (1xN matrix),
                 listing the an N-1 degree polynomial mirror
       x_guess = is the initial guess for a reflection point
    Output:
       x,y = a tuple specifying the location where angle of incidence == reflection"""

    f0 = angleBetween(x_s, y_s, x_c, y_c, a, x_guess)
    f1 = angleBetween(x_s, y_s, x_c, y_c, a, x_guess + 0.1)

    x = findRoot(x_guess, f0, x_guess + 0.1, f1)
    f = [f0, f1]
    x = [x_guess, x_guess + 0.1, x]

    for i in range(5):
#        print(x, f)
        f.append(angleBetween(x_s, y_s, x_c, y_c, a, x[-1]))
        x.append(findRoot(x[-2], f[-2], x[-1], f[-1]))

    return (x[-1], evalpoly(a, x[-1]))
#    return pr2_key.raytrace(x_s,y_s,x_c,y_c,a,x_guess)
