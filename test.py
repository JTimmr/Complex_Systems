import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np


class ForestFire:

    def __init__(self, L, g, f, timesteps):
        self.L = L
        self.g = g
        self.lightning_frequency = f
        self.timesteps = timesteps
        self.t = 0
        self.forest = np.zeros([L, L])
        self.cmap = colors.ListedColormap(['brown', 'green', 'orange'])
        self.ims = []
        self.trees = set()
        self.burning_trees = set()

    def get_neighbors(self, coordinate):
        up = (coordinate[0], coordinate[1] - 1)
        down = (coordinate[0], coordinate[1] + 1)
        left = (coordinate[0] - 1, coordinate[1])
        right = (coordinate[0] + 1, coordinate[1])
        return [up, down, left, right]


    def do_timestep(self):

        # Plant tree
        x, y = np.random.randint(self.L, size=2)
        self.forest[x, y] = 1
        self.trees.add((x, y))

        # Ignite random cell according to lightning frequency
        if self.t % self.lightning_frequency == 0:
            x, y = np.random.randint(self.L, size=2)

            if (x, y) in self.trees:
                self.forest[x, y] = 2
                self.burning_trees.add((x, y))
                self.trees.remove((x, y))
        
        # Check all neighors of currently burning trees
        for burning_tree in self.burning_trees:
            neighbors = self.get_neighbors(burning_tree)
            for neighbor in neighbors:

                # If neighbor cell has tree, ignite with probability g
                if neighbor in self.trees and np.random.random() < self.g:
                    self.trees.remove(neighbor)
                    self.burning_trees.add(neighbor)

    def run(self):
        fig, ax = plt.subplots()
        for t in range(self.timesteps):
            self.do_timestep()
            self.ims.append([ax.imshow(self.forest, animated=True, cmap=self.cmap)])
            self.t+= 1
        
        self.animate(fig)


    def animate(self, fig):

        ani = animation.ArtistAnimation(fig, self.ims, interval=50, blit=True,
                                        repeat_delay=1000)
        plt.show()


L = 10
g = 0
f = 5
timesteps = 100

forest = ForestFire(L, g, f, timesteps)
forest.run()