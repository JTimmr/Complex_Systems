"""Class to analyse one parameter setting of the model

The class Analyse is used to run a model with a single set of parameter values a determined
number of instances. From this, different data regarding fire sizes and trees density is 
gathered. Some plotting methods are also provided. 
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import powerlaw
from sklearn.linear_model import LinearRegression
from scipy.stats import linregress
from tree import Tree
from fire import Fire
from forest import Forest

class Analyse:
    def __init__(self, L, f, freeze_time_during_fire, remember_history, timesteps, instances, lake_proportion=0, include_lakes=None):
        self.ims = []
        self.instances = instances
        self.best_fitting_distributions = 'Not yet calculated'
        self.L = L
        self.f = f
        self.freeze_time_during_fire = freeze_time_during_fire
        self.remember_history = remember_history
        self.timesteps = timesteps
        self.include_lakes = include_lakes
        self.lake_proportion = lake_proportion
        self.cmap = colors.ListedColormap(['#4a1e13', '#047311', '#B95900', '#0000FF'])  # Blue for lakes
        self.fire_sizes = []
        self.trees_timeseries = np.zeros(shape=(self.instances,self.timesteps))
        self.all_fire_lengths = []
        self.all_fire_durations = []
        self.all_fire_durations_per_instance = []
    
        if self.remember_history:
            animation_fig, animation_ax = plt.subplots()
            self.animation_ax = animation_ax
            self.animation_fig = animation_fig

    def run_one_instance(self, instance_number=0):
        """
        Run one forest fire model for the specified parameters. Save data regarding fire sizes,
        tree time series and fire duration.
        """
        forest = Forest(self.L, self.f, self.freeze_time_during_fire, self.timesteps, include_lakes=self.include_lakes, lake_proportion=self.lake_proportion)
        while forest.t < self.timesteps:
            forest.do_timestep()
            if self.instances == 1 and self.remember_history:
                self.ims.append([self.animation_ax.imshow(forest.forest, animated=True, cmap = self.cmap, vmin=0, vmax=2)])
            forest.t += 1

        self.fire_sizes.append(np.array([forest.previous_fires[id].size for id in forest.previous_fires]))
        self.trees_timeseries[instance_number] = forest.trees_per_timestep
        self.all_fire_lengths.extend(forest.fire_lengths)
        self.collect_fire_durations(forest)

    def run_all(self):
        """
        Calls run_one_instance the specified number of times.
        """
        for instance_number in range(self.instances):
            self.run_one_instance(instance_number)
    
    def find_best_fitting_distributions(self):
        """
        Given the frequency of fire sizes from n instances of a forest fire model,
        returns the proportion of such instances for which the fire sizes seem to 
        follow a power law distribution. We assume the distribution is power law unless 
        proven otherwise. 
        """
        best_fitting_distributions = [0,0,0,0]
        distributions_test = ['exponential','truncated_power_law','lognormal']

        for distribution in self.fire_sizes: 
            result = powerlaw.Fit(distribution, verbose=False)
            best_fitting = 'power_law'
            index_best_fitting = 0
            for i, distribution in enumerate(distributions_test, start = 1): 
                R, p = result.distribution_compare(best_fitting, distribution)
                if R < 0 and p < 0.05:
                    best_fitting = distribution
                    index_best_fitting = i

            best_fitting_distributions[index_best_fitting] += 1
        
        self.best_fitting_distributions = np.array(best_fitting_distributions)/self.instances
        
    def find_linear_part(self, data, r_squared_threshold):
        """
        Given the frequency of fire sizes finds the section that would display 
        linear behavior in a log log plot. Returns, the end of this section.
        """
        x = np.log(data.index)
        y = np.log(data)

        linear_part_end = 0
        for i in range(2, len(data)):
            slope, _, r_value, _, _ = linregress(x[:i], y[:i])
            if r_value**2 >= r_squared_threshold:
                r_squared = r_value**2
                linear_part_end = i
            else:
                break

        return linear_part_end

    def log_log_plot(self, ax=None, fig=None, color='black', label='', show=False, 
                     title='Frequency fire sizes over all instances', ax_title="", 
                     scatter=True, s=3, linewidth=0.5, alpha=0.8, r_squared_threshold=0.95):
        """
        Given the frequencies of fires sizes and the end of the linear section, plots the frequencies in a log log plot 
        and fits a linear regression to the linear section. 
        """
        all_fire_sizes = []
        for sizes_list in self.fire_sizes:
            for element in sizes_list:
                all_fire_sizes.append(element)
        data = pd.Series(all_fire_sizes).value_counts().sort_index()/len(all_fire_sizes)

        if ax == None:
            fig, ax = plt.subplots()

        if scatter: 
            ax.scatter(data.index, data, color=color, s=s, label=label, alpha=alpha)
        else:
            ax.plot(data.index, data, color=color, linewidth=linewidth, label=label, alpha=alpha)

        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Fire size')
        ax.set_ylabel('Frequency')

        linear_part_end = self.find_linear_part(data, r_squared_threshold)

        # Perform linear regression on the identified linear part
        slope, intercept, _, _, _ = linregress(np.log(data.index[:linear_part_end]), np.log(data[:linear_part_end]))
        print(f"Best fitting slope: {slope}")

        ax.plot(data.index[:linear_part_end], np.exp(intercept) * data.index[:linear_part_end]**slope, color=color, linestyle='--', label=f'Linear Fit {label}', zorder=99)
        ax.axvline(data.index[linear_part_end-1], color=color, linestyle='--', linewidth=1)
        ax.legend(loc='upper right')
        ax.set_title(ax_title)

        if show:
            fig.suptitle(title)
            plt.show()


    def find_proportion_stable(self, epsilon = 0.1):
        """
        Takes the number of trees time series for each instance, fits a linear regression to the latter 50% 
        of observations and if the coefficient of t is smaller than epsilon considers it stable. Returns the 
        proportion of instances that are considered stable. 
        """

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
        """
        Give the number of trees time series produces a time series plot where each instance 
        has a line, and the average at each time step is shown in red. 
        """
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

    def calculate_average_tree_densities(self):
        """Returns the trees density at each time step averaged over all instances."""
        total_area = self.L * self.L
        sum_tree_densities = np.sum(self.trees_timeseries / total_area, axis=0)
        average_tree_densities = sum_tree_densities / self.instances
        return average_tree_densities
    
    def collect_fire_durations(self, forest):
        """Aggregates data regarding fire duration in each individual instance."""
        for fire_id, duration in forest.fire_durations.items():
            self.all_fire_durations.append(duration)

    def plot_fire_durations(self):
        """Produces a log log plot showing the frequency of each fire duration."""
        fire_duration_counts = pd.Series(self.all_fire_durations).value_counts()
        durations = fire_duration_counts.index.values
        frequencies = fire_duration_counts.values

        plt.figure(figsize=(10, 6))
        plt.scatter(durations, frequencies)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Duration of Fire (in time steps)')
        plt.ylabel('Frequency')
        plt.title('Log-Log Plot of Fire Durations')
        plt.show()
            
    def get_fire_durations(self):
        return self.all_fire_durations

    def calculate_mean_fire_sizes(self):
        """Calculate mean fire size over all instances."""
        mean_fire_sizes = []
        for sizes in self.fire_sizes:
            if len(sizes) > 0:
                mean_fire_sizes.append(np.mean(sizes))
            else:
                mean_fire_sizes.append(0)  # Append 0 if there were no fires in the instance
        return mean_fire_sizes
    
    def plot_mean_fire_sizes(self):
        """Plots the mean fire sizes as a boxplot."""
        mean_fire_sizes = self.calculate_mean_fire_sizes()
        
        plt.figure(figsize=(10, 6))
        plt.boxplot(mean_fire_sizes, patch_artist=True)
        plt.ylabel('Mean Fire Size')
        plt.title('Boxplot of Mean Fire Sizes Across Instances')
        plt.show()

    def animate(self, filename):
        """
        Produces an animation of one instance of the model in a grid. Saves it at a .gif in the specified 
        location.
        """
        if not hasattr(self, 'fig') or not hasattr(self, 'ax'):
            self.fig, self.ax = plt.subplots()
        
        ani = animation.ArtistAnimation(self.animation_fig, self.ims, interval=1, blit=True,
                                        repeat_delay=1000)
        
        ani.save(f'{filename}.gif', writer='ffmpeg', fps=30)

# Sample use of the class and useful for testing
if __name__ == '__main__':
    L = 50
    g = 1
    f = 50
    timesteps = 10**4
    instances = 10
    analysis_exp =  Analyse(L, f, True, False, timesteps, instances, 0.2, False)
    analysis_exp.run_all()   
    analysis_exp.find_best_fitting_distributions()
    analysis_exp.log_log_plot(show = True)
    analysis_exp.find_proportion_stable()
    analysis_exp.plot_number_trees_timeseries()
    analysis_exp.calculate_average_tree_densities() 
    analysis_exp.plot_fire_durations()