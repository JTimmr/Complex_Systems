import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import powerlaw
from sklearn.linear_model import LinearRegression
from tree import Tree
from fire import Fire
from forest import Forest

class Analyse:
    def __init__(self, L, g, f, freeze_time_during_fire, remember_history, timesteps, instances):
        self.ims = []
        self.instances = instances
        self.proportion_power_law = 'Not yet calculated'
        self.L = L
        self.g = g
        self.f = f
        self.freeze_time_during_fire = freeze_time_during_fire
        self.remember_history = remember_history
        self.timesteps = timesteps
        self.cmap = colors.ListedColormap(['#4a1e13', '#047311', '#B95900'])
        self.fire_sizes = []
        self.trees_timeseries = np.zeros(shape=(self.instances,self.timesteps))
        if self.remember_history:
            fig, ax = plt.subplots()
            self.ax = ax
            self.fig = fig


    def run_one_instance(self, instance_number):
        forest = Forest(self.L, self.g, self.f, self.freeze_time_during_fire, self.timesteps)
        while forest.t < self.timesteps:
            forest.do_timestep()
            if self.instances == 1 and self.remember_history:
                self.ims.append([self.ax.imshow(forest.forest, animated=True, cmap = self.cmap, vmin=0, vmax=2)])
            forest.t += 1

        self.fire_sizes.append(np.array([forest.previous_fires[id].size for id in forest.previous_fires]))
        self.trees_timeseries[instance_number] = forest.trees_per_timestep


    def run_all(self):
        for instance_number in range(self.instances):
            self.run_one_instance(instance_number)
    
    def find_proportion_power_law(self):
        '''
        Given the frequency of fire sizes from n instances of a forest fire model,
        returns the proportion of such instances for which the fire sizes seem to 
        follow a power law distribution. We assume the distribution is power law unless 
        proven otherwise. 
        '''
        number_power_laws = len(self.fire_sizes)
        distributions_test = ['exponential','truncated_power_law','lognormal']
        for distribution in self.fire_sizes: 
            result = powerlaw.Fit(distribution)
            for distribution in distributions_test: 
                R, p = result.distribution_compare('power_law',distribution)
                if R < 0 and p < 0.01:
                    number_power_laws -= 1
                    break
    
        self.proportion_power_law = number_power_laws / len(self.fire_sizes)
        
    def log_log_plot(self):
               
        all_fire_sizes = []
        for sizes_list in self.fire_sizes:
            for element in sizes_list:
                all_fire_sizes.append(element)
        data = pd.Series(all_fire_sizes).value_counts()/len(all_fire_sizes)

        plt.scatter(data.index, data, color='black', s=3)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        plt.xscale('log')
        plt.yscale('log')

        plt.xlabel('Fire size')
        plt.ylabel('Frequency')
        plt.title('Frequency fire sizes over all instances')
        plt.show()

    def find_proportion_stable(self, epsilon = 0.1):

        stable_counter = 0

        # fit linear regression to last 50% of points 
        cut_off_point = int(self.timesteps / 2)
        linear_regression = LinearRegression()

        for instance in range(self.instances):
            Y = self.trees_timeseries[instance,cut_off_point:]
            X = [[i] for i in range(len(Y))]
            linear_regression.fit(X,Y)

            # count as stable if slope is smaller than epsilon
            stable_counter += linear_regression.coef_[0] < epsilon

        return stable_counter/self.instances
    
    def plot_number_trees_timeseries(self):

        single_time_step_value = [self.trees_timeseries[:,i] for i in range(self.timesteps)]
        plt.plot(range(self.timesteps),single_time_step_value, color = 'black', 
                 alpha = 0.4)

        average_value = [np.mean(self.trees_timeseries[:,i]) for i in range(self.timesteps)]
        plt.plot(range(self.timesteps),average_value, color = 'red', label = 'Average')

        plt.grid(True)
        plt.title(f'Number of trees per timestep for {self.instances} instances of model')
        plt.legend()
        plt.xlabel('t')
        plt.ylabel('Number of trees')

        plt.show()
    
    def animate(self, filename):

        ani = animation.ArtistAnimation(self.fig, self.ims, interval=1, blit=True,
                                        repeat_delay=1000)
        
        ani.save(f'{filename}.gif', writer='ffmpeg', fps=30)

if __name__ == '__main__':
    L = 10
    g = 1
    f = 50
    timesteps = 10**3
    instances = 10
    analysis_exp =  Analyse(L, g, f, timesteps, instances)
    analysis_exp.run_all()
    print(analysis_exp.find_proportion_power_law())
    analysis_exp.log_log_plot(3)