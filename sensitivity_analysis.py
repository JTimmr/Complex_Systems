import matplotlib.pyplot as plt
from analysis import Analyse
import numpy as np

class SensitivityAnal:
    """Class to analyse system sensitivity to parameters

    Specify the paramter_to_change and the range of this parameter. Over each tested parameter value the proportion 
    of models that reach a quasi equilibrium state is calculated. Also the proportion which is best fitted by each 
    of the four tested distributions is calculated. 

    One should also specify the value of the unchanged parameters as well as the number of time steps and the instances
    of the model to run for each parameter setting. 
    """

    def __init__(self, L, g, f, parameter_to_change, range_min, range_max, range_step, time_steps, instances):
        self.model_parameters = {'L': L, 'g': g, 'f':f}
        self.parameter_to_change = parameter_to_change
        self.parameter_range = np.arange(range_min, range_max + range_step, range_step)
        self.time_steps = time_steps
        self.instances = instances

        self.power_law_data = np.zeros([len(self.parameter_range),4])
        self.stability_data = []

    def run(self):
        for i, parameter in enumerate(self.parameter_range):
            self.model_parameters[self.parameter_to_change] = parameter
            L, g, f = self.model_parameters.values()

            analysis = Analyse(L, g, f, True, False, self.time_steps, self.instances )
            analysis.run_all()
            analysis.find_best_fitting_distributions()
            
            self.power_law_data[i,:] = analysis.best_fitting_distributions
            self.stability_data.append(analysis.find_proportion_stable())  
    
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

if __name__ == '__main__':
    sensitivity_analysis = SensitivityAnal(50, 1, 50, 'L', 50, 100, 10, 10**4, 2)
    sensitivity_analysis.run()
    sensitivity_analysis.make_distributions_plots()
    sensitivity_analysis.make_stability_plot()
