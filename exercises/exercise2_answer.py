"""
Complete the code below to accuractely prescribe a light (0) or dark (1) font respectively
for a given background color (specified as three R,G, B values).

Test with the interactive shell at the end, where black (0,0,0) should prescribe a LIGHT font
and white (255,255,255) should prescribe a dark font.
"""

import random

import math
import pandas as pd
import numpy as np
from numpy import log, exp


class LabeledColor:
    def __init__(self, red, green, blue, dark_font_ind):
        self.red = (red / 255.0)
        self.green = (green / 255.0)
        self.blue = (blue / 255.0)
        self.dark_font_ind = dark_font_ind

    def __str__(self):
        return "{0},{1},{2}: {3}".format(self.red, self.green, self.blue, self.dark_font_ind)


training_colors = [(LabeledColor(row[0], row[1], row[2], row[3])) for index, row in
                   pd.read_csv("https://tinyurl.com/y2qmhfsr").iterrows()]

training_dark_colors = [c for c in training_colors if c.dark_font_ind == 1.0]
training_light_colors = [c for c in training_colors if c.dark_font_ind == 0.0]

best_likelihood = -100_000_000_000.0
b0 = 1.0  # constant
b1 = 1.0  # red beta
b2 = 1.0  # green beta
b3 = 1.0  # blue beta

iterations = 1_000


# calculate maximum likelihood

# Closer to true (1.0) recommends dark font, closer to false (0.0) recommends light font
def predict_probability(red, green, blue):
    x = -(b0 + (b1 * red) + (b2 * green) + (b3 * blue))
    odds = exp(x)
    return 1.0 / (1.0 + odds)


for _ in range(iterations):
    # Select b0, b1, b2, or b3 randomly, and adjust it by a random amount
    random_b = random.choice(range(4))

    random_adjust = np.random.standard_normal()

    if random_b == 0:
        b0 += random_adjust
    elif random_b == 1:
        b1 += random_adjust
    elif random_b == 2:
        b2 += random_adjust
    elif random_b == 3:
        b3 += random_adjust

    # calculate new likelihood
    # Use logarithmic addition to avoid multiplication and decimal underflow
    new_likelihood = 0.0

    for c in training_colors:

        probability = predict_probability(c.red, c.green, c.blue)

        new_likelihood += (
            log(probability)
            if c.dark_font_ind == 1
            else log(1.0 - probability)
        )
    # If solution improves, keep it and make it new best likelihood. Otherwise undo the adjustment
    if best_likelihood < new_likelihood:
        best_likelihood = new_likelihood
    elif random_b == 0:
        b0 -= random_adjust
    elif random_b == 1:
        b1 -= random_adjust
    elif random_b == 2:
        b2 -= random_adjust
    elif random_b == 3:
        b3 -= random_adjust

# Print best result
print("1.0 / (1 + exp(-({0} + {1}*r + {2}*g + {3}*b))".format(b0, b1, b2, b3))
print("BEST LIKELIHOOD: {0}".format(math.exp(best_likelihood)))


# Interact and test with new colors
def predict_font_shade(r, g, b):
    return "DARK" if predict_probability(r, g, b) >= .5 else "LIGHT"


while True:
    n = input("Predict light or dark font. Input values R,G,B: ")
    (r, g, b) = n.split(",")
    print(predict_font_shade(int(r), int(g), int(b)))
