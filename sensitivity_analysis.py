import matplotlib.pyplot as plt
from analysis import Analyse
import numpy as np
import pandas as pd

class SensitivityAnal:
    """Class to analyse system sensitivity to parameters

    Specify the paramter_to_change and the range of this parameter. Over each tested parameter value the proportion 
    of models that reach a quasi equilibrium state is calculated. Also the proportion which is best fitted by each 
    of the four tested distributions is calculated. 

    One should also specify the value of the unchanged parameters as well as the number of time steps and the instances
    of the model to run for each parameter setting. 
    """

    def __init__(self, L, f, parameter_to_change, range_min, range_max, range_step, time_steps, instances, include_lakes, lake_proportion):
        self.model_parameters = {'L': L,'f':f}
        self.parameter_to_change = parameter_to_change
        self.parameter_range = np.arange(range_min, range_max + range_step, range_step)
        self.time_steps = time_steps
        self.instances = instances

        self.power_law_data = np.zeros([len(self.parameter_range),4])
        self.stability_data = []
        self.fire_durations_data = []
        self.mean_fire_sizes_data = []
        self.average_tree_densities_data = []
        self.include_lakes = include_lakes
        self.lake_proportion = lake_proportion  

    def run(self):
        for i, parameter in enumerate(self.parameter_range):
            self.model_parameters[self.parameter_to_change] = parameter
            L, f = self.model_parameters.values()

            analysis = Analyse(L, f, True, False, self.time_steps, self.instances, self.lake_proportion, self.include_lakes )
            analysis.run_all()
            analysis.find_best_fitting_distributions()
            
            self.power_law_data[i,:] = analysis.best_fitting_distributions
            self.stability_data.append(analysis.find_proportion_stable())  
            self.fire_durations_data.append(analysis.get_fire_durations())
            self.mean_fire_sizes_data.append(analysis.calculate_mean_fire_sizes())
            self.average_tree_densities_data.append(analysis.calculate_average_tree_densities())
    
    def make_distributions_plots(self):
        distribution_names = ['power law','exponential','truncated_power_law','lognormal']
        for col in range(self.power_law_data.shape[1]):
            distribution_data = self.power_law_data[:,col]
            if sum(distribution_data) != 0:
                plt.plot(sensitivity_analysis.parameter_range, distribution_data, label = distribution_names[col])
        plt.legend(loc = 'lower right')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.xlabel(self.parameter_to_change)
        plt.ylabel('Proportion of model instances')
        plt.title('Best fitting distribution at different parameter levels')
        plt.show()

    def make_stability_plot(self):
        plt.plot(self.parameter_range, self.stability_data)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.xlabel(self.parameter_to_change)
        plt.ylabel('Proportion of model instances')
        plt.title('Proportion of stable systems at different parameter levels')
        plt.show()  

    def make_fire_duration_log_log_plot(self):
        plt.figure(figsize=(10, 6))

        for i, parameter in enumerate(self.parameter_range):
            fire_durations = self.fire_durations_data[i]
            fire_duration_counts = pd.Series(fire_durations).value_counts()
            durations = fire_duration_counts.index.values
            frequencies = fire_duration_counts.values

            plt.scatter(durations, frequencies, label=f'{self.parameter_to_change} = {parameter}')

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Duration of Fire (in time steps)')
        plt.ylabel('Frequency')
        plt.title('Log-Log Plot of Fire Durations for Different Parameter Values')
        plt.legend()
        plt.show()

    def make_mean_fire_size_boxplot(self):
        plt.figure(figsize=(10, 6))
        plt.boxplot(self.mean_fire_sizes_data, patch_artist=True)
        plt.xticks(ticks=np.arange(1, len(self.parameter_range) + 1), labels=self.parameter_range)
        plt.xlabel(self.parameter_to_change)
        plt.ylabel('Mean Fire Size')
        plt.title('Boxplot of Mean Fire Sizes for Different Parameter Values')
        plt.show()

    def plot_average_tree_densities(self):
        plt.figure(figsize=(10, 6))

        for i, parameter in enumerate(self.parameter_range):
            average_tree_densities = self.average_tree_densities_data[i]
            plt.plot(range(self.time_steps), average_tree_densities, label=f'{self.parameter_to_change} = {parameter}')

        plt.xlabel('Time Step')
        plt.ylabel('Average Tree Density')
        plt.title('Average Tree Density over Time for Different Parameter Values')
        plt.legend()
        plt.show()

if __name__ == '__main__':
    sensitivity_analysis = SensitivityAnal(50, 1, 50, 'g', 0.5, 2, 0.5, 10**5, 10, True, 0.2)
    sensitivity_analysis.run()
    sensitivity_analysis.make_distributions_plots()
    sensitivity_analysis.make_stability_plot()
    sensitivity_analysis.make_fire_duration_log_log_plot()
    sensitivity_analysis.make_mean_fire_size_boxplot()
    sensitivity_analysis.plot_average_tree_densities()

