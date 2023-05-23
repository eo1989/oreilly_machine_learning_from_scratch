import numpy as np
import pandas as pd
from scipy import special

training_data = pd.read_csv("https://tinyurl.com/y2qmhfsr")
training_data_count = len(training_data.index)

# Learning rate controls how slowly we approach a solution
# Make it too small, it will take too long to run.
# Make it too big, it will likely overshoot and miss the solution.
learning_rate = 0.01
sample_size = 10

# Extract the input columns, scale down by 255
training_inputs = (training_data.iloc[:, 0:3].values.transpose() / 255.0 * .99) + .01

# Extract output column, and generate an opposite column where 1 is 0 and 0 is 1.
training_outputs = np.vstack(
    (training_data.iloc[:, -1].values.transpose(), -1 * (training_data.iloc[:, -1].values.transpose() - 1)))

n = len(training_data.index)

# Build neural network with weights and biases
middle_weights = np.random.rand(3, 3)
output_weights = np.random.rand(2, 3)

middle_bias = np.random.rand(3, 1)
output_bias = np.random.rand(2, 1)

best_middle_weights = None
best_output_weights = None
best_middle_bias = None
best_output_bias = None

# Activation functions
softplus = lambda x: np.log(1 + np.exp(x))
logistic = lambda x: 1 / (1 + np.exp(-x))


best_loss = 10_000_000_000

# Execute training with simulated annealing
# This is similar to hill-climbing except it occasionally allows inferior moves hoping to find a better solution
# This is covered in depth in another online training "Intro to Mathematical Optimization"

epochs = 10_000_000
temperature = 120.0
decrement = temperature / epochs
new_loss = 1_000_000_000.0

for _ in range(epochs):
    temperature -= decrement
    current_loss = new_loss

    # 20 hyper-parameters to randomly select from
    # Each parameter needs to be uniformly likely to be selected
    # So we will use some random number strategies to
    random_select = np.random.randint(0, 20)
    random_adjust = np.random.normal() * learning_rate
    random_row = 0
    random_col = 0

    # Randomly adjust middle layer weight
    if random_select < 9:
        random_row = np.random.randint(0, 3)
        random_col = np.random.randint(0, 3)

        if middle_weights[random_row, random_col] + random_adjust < -1.0:
            random_adjust = -1.0 - middle_weights[random_row, random_col]
        if middle_weights[random_row, random_col] + random_adjust > 1.0:
            random_adjust = 1.0 - middle_weights[random_row, random_col]

        middle_weights[random_row, random_col] += random_adjust

    # Randomly adjust outer layer weight
    elif random_select < 15:
        random_row = np.random.randint(0, 2)
        random_col = np.random.randint(0, 3)

        if output_weights[random_row, random_col] + random_adjust < -1.0:
            random_adjust = -1.0 - output_weights[random_row, random_col]
        if output_weights[random_row, random_col] + random_adjust > 1.0:
            random_adjust = 1.0 - output_weights[random_row, random_col]

        output_weights[random_row, random_col] += random_adjust

    # Randomly adjust middle layer bias
    elif random_select < 18:
        random_row = np.random.randint(3)
        random_col = 0

        if middle_bias[random_row, random_col] + random_adjust < 0.0:
            random_adjust = 0.0 - middle_bias[random_row, random_col]
        if middle_bias[random_row, random_col] + random_adjust > 1.0:
            random_adjust = 1.0 - middle_bias[random_row, random_col]

        middle_bias[random_row, random_col] += random_adjust

    # Randomly adjust outer layer bias
    elif random_select < 20:
        random_row = np.random.randint(2)
        random_col = 0

        if output_bias[random_row, random_col] + random_adjust < 0.0:
            random_adjust = 0.0 - output_bias[random_row, random_col]
        if output_bias[random_row, random_col] + random_adjust > 1.0:
            random_adjust = 1.0 - output_bias[random_row, random_col]

        output_bias[random_row, random_col] += random_adjust


    #idx = np.random.choice(n, sample_size, replace=False)
    #input_sample = training_inputs[:, idx]
    #output_sample = training_outputs[:, idx]

    # Calculate outputs with the given weights, biases, and activation functions for all three layers
    predicted_outputs = logistic(output_bias + output_weights.dot(softplus(middle_bias + middle_weights.dot(training_inputs))))

    # Calculate the mean squared loss
    new_loss = np.sum((training_outputs - predicted_outputs) ** 2) / training_data_count

    # If the loss improves, keep the random adjustment. Otherwise revert.
    if new_loss < best_loss:
        best_loss = new_loss
        print("TEMP {0}, LOSS {1}->{2}".format(temperature,current_loss,new_loss))
        current_loss = new_loss

        # Save solution
        best_middle_weights = middle_weights.copy()
        best_output_weights = output_weights.copy()
        best_middle_bias = middle_bias.copy()
        best_output_bias = output_bias.copy()

    elif new_loss < current_loss:
        current_loss = new_loss

    # Do a weighted coin flip based on temperature to determine whether to accept inferior move
    elif np.random.uniform(0, 1) <= np.exp((-(new_loss - current_loss)) / temperature):
        current_loss = new_loss
        #print("{0}<-{1}".format(new_loss,current_loss))

    # Undo the random adjust if loss hasn't improved or coin flip fails
    elif random_select < 9:
        middle_weights[random_row, random_col] -= random_adjust

    elif random_select < 15:
        output_weights[random_row, random_col] -= random_adjust

    elif random_select < 18:
        middle_bias[random_row, random_col] -= random_adjust

    elif random_select < 20:
        output_bias[random_row, random_col] -= random_adjust


# Set best solution
middle_weights = best_middle_weights
output_weights = best_output_weights
middle_bias = best_middle_bias
output_bias = best_output_bias

# Interact and test with new colors
def predict_probability(r, g, b):
    input_colors = np.array([r, g, b]).transpose() / 255
    return logistic(
        output_bias
        + output_weights.dot(
            softplus(middle_bias + middle_weights.dot(input_colors))
        )
    )


def predict_font_shade(r, g, b):
    output_values = predict_probability(r, g, b)
    return "DARK" if output_values[0, 0] > output_values[1, 0] else "LIGHT"


while True:
    try:
        n = input("Predict light or dark font. Input values R,G,B: ")
        (r, g, b) = n.split(",")
        print(predict_font_shade(int(r), int(g), int(b)))
    except Exception as e:
        print(e)
