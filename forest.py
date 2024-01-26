import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
from tree import Tree
from fire import Fire


class Forest:

    def __init__(self, L, g, f, timesteps):
        self.L = L
        self.g = g
        self.lightning_frequency = f
        self.timesteps = timesteps
        self.t = 0
        self.forest = np.zeros([L, L])
        self.cmap = colors.ListedColormap(['#4a1e13', '#047311', '#B95900'])
        self.ims = []
        self.trees = {}
        self.fires = {}
        self.previous_fires = {}

        # For fire-size frequency
        self.current_fires = []
        self.fire_sizes = []


    def plant_tree(self):
        x, y = np.random.randint(self.L, size=2)
        self.forest[x, y] = 1
        tree = Tree((x, y), self.t, self)
        self.trees[(x, y)] = tree


    def grow_fire(self):
        for fire in self.fires.values():
            fire.update()

            for ignited_tree in fire.ignited_trees:
                fire.burning_trees[ignited_tree] = self.trees[ignited_tree]
                self.forest[ignited_tree] = 2
                fire.size += 1
                del self.trees[ignited_tree]

            fire.ignited_trees = []

    def lightning_strike(self):
        
        location = tuple(np.random.randint(self.L, size=2))

        # Ignite tree
        if location in self.trees:
            
            id = len(self.fires)
            fire = Fire(self.t, self.trees[location], id, self)
            self.fires[id] = fire
            self.forest[location] = 2
            self.trees[location].t_ignited = self.t
            fire.burning_trees[location] = self.trees[location]
            del self.trees[location]

    def extinguish_trees(self):
        for fire in self.fires.values():

            # Extinguish trees
            for burned_tree in fire.burned_trees:
                del fire.burning_trees[burned_tree]
                self.forest[burned_tree] = 0

            fire.burned_trees = []

    def update_fires(self):
        """
        Keep track of the fires.
        """
        for id, fire in self.fires.items():
            if not fire.burning:
                del self.fires[id]
                self.previous_fires[id] = fire


    def do_timestep(self):
        self.plant_tree()
        self.grow_fire()
        self.extinguish_trees()
        self.update_fires()

        if self.t % self.lightning_frequency == 0:
            self.lightning_strike()


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
