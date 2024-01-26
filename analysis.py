import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import powerlaw
from test2 import Forest

class Analyse:
    def __init__(self, L, g, f, timesteps, instances, fig=None, ax=None):
        self.ims = []
        self.instances = instances
        self.proportion_power_law = 'Not yet calculated'
        self.L = L
        self.g = g
        self.f = f
        self.timesteps = timesteps
        self.cmap = colors.ListedColormap(['#4a1e13', '#047311', '#B95900'])
        self.ax = ax
        self.fig = fig
        self.fire_sizes = []

    def run_one_instance(self):
        forest = Forest(self.L, self.g, self.f, self.timesteps)

        for t in range(self.timesteps):
            forest.do_timestep()
            if self.instances == 1:
                self.ims.append([self.ax.imshow(self.forest.forest, animated=True, cmap = self.cmap, vmin=0, vmax=2)])
            forest.t += 1

        self.fire_sizes.append(np.array([forest.fires[id].size for id in range(len(forest.fires))]))

    def run_all(self):
        for instance in range(self.instances):
            self.run_one_instance()
    
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

    def log_log_plot(self, instance):
        
        data = pd.Series(self.fire_sizes[instance]).value_counts()
        
        plt.scatter(data.index,data)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Fire size')
        plt.ylabel('Frequency')
        plt.show()

    def animate(self, filename):

        ani = animation.ArtistAnimation(self.fig, self.ims, interval=1, blit=True,
                                        repeat_delay=1000)
        
        ani.save(f'{filename}.gif', writer='ffmpeg', fps=30)
    

    def plot_firesizes(self):
        plt.hist(self.fire_sizes)
        plt.show()

