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
        self.cmap = colors.ListedColormap(['#4a1e13', '#047311', '#B95900'])
        self.ims = []
        self.trees = set()
        self.burning_trees = set()
        self.burned_trees = []
        self.ignited_trees = []

        # For fire-size frequency
        self.current_fires = []
        self.fire_sizes = []

    def get_neighbors(self, coordinate):
        up = (coordinate[0], (coordinate[1] - 1) % self.L)
        down = (coordinate[0], (coordinate[1] + 1) % self.L)
        left = ((coordinate[0] - 1) % self.L, coordinate[1])
        right = ((coordinate[0] + 1) % self.L, coordinate[1])
        return [up, down, left, right]


    def do_timestep(self):

        # Plant tree
        x, y = np.random.randint(self.L, size=2)
        self.forest[x, y] = 1
        self.trees.add((x, y))

        # Dummy variable to detect extinguished fires
        keep_fire = np.repeat(False, len(self.current_fires))

        # Check all neighors of currently burning trees
        for burning_tree in self.burning_trees:
            neighbors = self.get_neighbors(burning_tree)
            for neighbor in neighbors:
                random_num = np.random.rand(1)[0]

                # If neighbor cell has tree, ignite with probability g
                if neighbor in self.trees and random_num < self.g:
                    self.trees.remove(neighbor)
                    self.ignited_trees.append(neighbor)

                    # Add new burning tree to corresponding current fire
                    for i, fire in enumerate(self.current_fires): 
                        if burning_tree in fire: 
                            fire.append(neighbor)
                            keep_fire[i] = True

            
            # Remove burning tree after it ignited others
            self.burned_trees.append(burning_tree)

        for burned_tree in self.burned_trees:
            self.burning_trees.remove(burned_tree)
            self.forest[burned_tree] = 0

        for ignited_tree in self.ignited_trees:
            self.burning_trees.add(ignited_tree)
            self.forest[ignited_tree] = 2

        self.burned_trees = []
        self.ignited_trees = []

        # Delete extinguised current fires and save their size
        fires_to_keep = []
        for i, fire in enumerate(self.current_fires):
            if keep_fire[i]:
                fires_to_keep.append(fire)
            else: 
                self.fire_sizes.append(len(fire))
        self.current_fires = fires_to_keep

        # Ignite random cell according to lightning frequency
        if self.t % self.lightning_frequency == 0:
            x, y = np.random.randint(self.L, size=2)

            # Ignite tree
            if (x, y) in self.trees:
                self.forest[x, y] = 2
                self.burning_trees.add((x, y))
                self.trees.remove((x, y))

                # Add new current fire 
                self.current_fires.append([(x,y)])

    def run(self):
        fig, ax = plt.subplots()
        for t in range(self.timesteps):
            self.do_timestep()
            self.ims.append([ax.imshow(self.forest, animated=True, cmap = self.cmap, vmin=0, vmax=2)])
            self.t += 1
        
        self.animate(fig)


    def animate(self, fig):

        ani = animation.ArtistAnimation(fig, self.ims, interval=1, blit=True,
                                        repeat_delay=1000)
        plt.show()


L = 50
g = 1
f = 50
timesteps = 50000

forest = ForestFire(L, g, f, timesteps)
forest.run()






