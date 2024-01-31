import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
from tree import Tree
from fire import Fire


class Forest:


    def __init__(self, L, f, freeze_time_during_fire, timesteps, include_lakes, lake_proportion,  wind=(0, 0), wind_effects_enabled=False,):
        self.L = L
        self.lightning_frequency = f
        self.freeze_time_during_fire = freeze_time_during_fire
        self.timesteps = timesteps
        self.t = 0
        self.forest = np.zeros([L, L])
        self.cmap = colors.ListedColormap(['#4a1e13', '#047311', '#B95900', '#0000FF'])  # Blue for lakes
        self.ims = []
        self.trees = {}
        self.trees_per_timestep = []
        self.fires = {}
        self.previous_fires = {}
        self.wind = wind  # Wind vector (dx, dy)
        self.wind_effects_enabled = wind_effects_enabled
        self.include_lakes = include_lakes
        self.lake_proportion = lake_proportion
        self.fire_lengths = []
        self.fire_durations = {}
        if self.include_lakes:
            self.initialize_lakes()

        # For fire-size frequency
        self.current_fires = []
        self.fire_sizes = []


    def plant_tree(self):
        while True:
            x, y = np.random.randint(self.L, size=2)
            if self.forest[x, y] != 3:  # lake check
                self.forest[x, y] = 1
                tree = Tree((x, y), self.t, self)
                self.trees[(x, y)] = tree
                break


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
            
            id = len(self.fires) + len(self.previous_fires)
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
        extinguished_fires = {}
        for id, fire in self.fires.items():
            if not fire.burning:
                self.previous_fires[id] = fire
                extinguished_fires[id] = fire
    
        for id, fire in extinguished_fires.items():
            if id in self.fires and not fire.burning:
                fire.t_extinguished = self.t  # Set the extinguish time
                del self.fires[id]
                # Record fire length and timestep
                self.fire_lengths.append((fire.t_extinguished, fire.size))

    def initialize_lakes(self):
        if not self.include_lakes:
            return

        lake_cells = int(self.L * self.L * self.lake_proportion)
        lakes_to_create = int(5)  # Adjust this for the number of lakes

        for _ in range(lakes_to_create):
            # Select a random starting point for the lake
            x, y = np.random.randint(self.L, size=2)
            self.expand_lake(x, y, lake_cells // lakes_to_create)

    def expand_lake(self, x, y, size):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  
        for _ in range(size):
            if 0 <= x < self.L and 0 <= y < self.L:
                self.forest[x, y] = 3  # Mark as lake
            # Direction to expand
            dx, dy = random.choice(directions)
            x += dx
            y += dy
            # Ensure bounds
            x = max(0, min(x, self.L - 1))
            y = max(0, min(y, self.L - 1))
            
    def record_fire_duration(self, fire_id, duration):
        self.fire_durations[fire_id] = duration
            
    
    


    def do_timestep(self):
        if not self.freeze_time_during_fire or len(self.fires) == 0:
            self.plant_tree()

        self.grow_fire()
        self.extinguish_trees()
        self.update_fires()
        self.trees_per_timestep.append(len(self.trees))

        if self.t % self.lightning_frequency == 0:
            self.lightning_strike()


