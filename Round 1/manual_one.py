# Define the objective function
def objective_function(x, y):
    return (y) - (x**2)/100 - ((y - x) * y)/100

# Initialize variables to store optimal values
optimal_x = 0
optimal_y = 0
optimal_value = float('-inf')  # Initialize with negative infinity

# Iterate over all possible combinations of x and y
x = 0
while x <= 100:
    y = 0
    while y <= 100:
        # Calculate objective value for current x and y
        current_value = objective_function(x, y)
        # Check if the current value is greater than the current optimal value
        if current_value > optimal_value:
            optimal_value = current_value
            optimal_x = x
            optimal_y = y
        y += 1
    x += 1

# Print the optimal values
print("Optimal x:", optimal_x + 900)
print("Optimal y:", optimal_y + 900)
print("Optimal value of the objective function:", optimal_value)
