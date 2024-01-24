import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np


class ForestFire:

    def __init__(self, L, g, f, timesteps) -> None:
        self.L = L
        self.g = g
        self.lightning_frequency = f
        self.timesteps = timesteps
        self.t = 0
        self.forest = np.zeros(shape=[L, L])
        self.cmap = colors.ListedColormap(colors=['brown', 'green', 'orange', "black"])
        self.ims = []
        self.trees = set()
        self.burning_trees = set()
        self.burned_trees = []
        self.ignited_trees = []
        self.age = np.zeros(shape=[L, L])
        # For fire-size frequency
        self.current_fires = []
        self.fire_sizes = []

    def get_neighbors(self, coordinate):# -> list[tuple[Any, Any]]:
        up = (coordinate[0], coordinate[1] - 1)
        down = (coordinate[0], coordinate[1] + 1)
        left = (coordinate[0] - 1, coordinate[1])
        right = (coordinate[0] + 1, coordinate[1])
        return [up, down, left, right]
    
    def add_obstacles(self, obstacles: int) -> None:
        for i in range(obstacles):
            x , y = np.random.randint(low=self.L, size=2)
            self.forest[x, y] = 3


    def do_timestep(self) -> None:
        while True:
            x, y = np.random.randint(low=self.L, size=2)
            if self.forest[x, y] == 0:  
                self.forest[x, y] = 1  
                self.trees.add((x, y))
                break

        # Dummy variable to detect extinguished fires
        keep_fire = np.repeat(False, len(self.current_fires))

        # Check all neighors of currently burning trees
        for burning_tree in self.burning_trees:
            neighbors = self.get_neighbors(coordinate=burning_tree)
            for neighbor in neighbors:
                random_num = np.random.rand(1)[0]

                # If neighbor cell has tree, ignite with probability g
                if neighbor in self.trees and random_num < self.g:
                    self.trees.remove(neighbor)
                    self.ignited_trees.append(neighbor)

                    # Add new burning tree to corresponding current fire
                    for i, fire in enumerate(iterable=self.current_fires): 
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
        for i, fire in enumerate(iterable=self.current_fires):
            if keep_fire[i]:
                fires_to_keep.append(fire)
            else: 
                self.fire_sizes.append(len(fire))
        self.current_fires = fires_to_keep

        # Ignite random cell according to lightning frequency
        if self.t % self.lightning_frequency == 0:
            x, y = np.random.randint(low=self.L, size=2)
            # Ignite tree
            if (x, y) in self.trees:
                self.forest[x, y] = 2
                self.burning_trees.add((x, y))
                self.trees.remove((x, y))

                # Add new current fire 
                self.current_fires.append([(x,y)])

    def run(self) -> None:
        fig, ax = plt.subplots()
        for t in range(self.timesteps):
            self.add_obstacles(20)
            self.do_timestep()
            self.ims.append([ax.imshow(self.forest, animated=True, cmap = self.cmap, vmin=0, vmax=2)])
            self.t+= 1
        
        self.animate(fig)


    def animate(self, fig) -> None:
        ani = animation.ArtistAnimation(fig=fig, artists=self.ims, interval=1, blit=True,
                                        repeat_delay=1)
        plt.show()


L = 50
g = 0.99
f = 15
timesteps = 5000

forest = ForestFire(L, g, f, timesteps)
forest.run()






