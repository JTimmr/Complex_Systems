import pandas as pd
import matplotlib.pyplot as plt
import powerlaw
from test import ForestFire


# Plotting the distribution of fires sizes for one instance
def log_log_plot(instance):
    data = pd.Series(instance.fire_sizes).value_counts()
    plt.scatter(data.index,data)
    plt.xscale('log')
    plt.yscale('log')
    plt.show()

# Function to test power law distribution
def proportion_of_power_law(instances):
    '''
    Given the frequency of fire sizes from n instances of a forest fire model,
    returns the proportion of such instances for which the fire sizes seem to 
    follow a power law distribution. We assume the distribution is power law unless 
    proven otherwise. 
    '''
    number_power_laws = len(instances)
    distributions_test = ['exponential','truncated_power_law','lognormal']
    for forest in instances: 
        result = powerlaw.Fit(forest.fire_sizes)
        for distribution in distributions_test: 
            R, p = result.distribution_compare('power_law',distribution)
            if R < 0 and p < 0.01:
                number_power_laws -= 1
                break
    proportion_power_laws = number_power_laws / len(instances)
    return proportion_power_laws


if __name__ == '__main__':

    # Sample use where n = 20, model parameters are L = 50, g = 1 and f = 5 and 
    # each model is ran 10^4 iterations
    instances = []
    n_instances = 20
    L = 50; g = 1; f = 5; timesteps = 10 ** 4

    for i in range(n_instances):
        forest = ForestFire(L, g, f, timesteps)
        forest.run()
        instances.append(forest)

    proportion = proportion_of_power_law(instances)    
    print(f'Proportion of model instances that show a power law distribution in the fire size frequency is {proportion}')





