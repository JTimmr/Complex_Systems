import random
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
        self.ims = []
        self.trees = {}
        self.trees_per_timestep = []
        self.fires = {}
        self.previous_fires = {}
        self.wind = wind
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
        """
        Selects a random cell in self.forest which is not part of a lake.
        Plants a tree if it does not already contain one
        """

        # Until tree is planted
        while True:

            # Select random cell
            x, y = np.random.randint(self.L, size=2)

            # Plant tree unless cell is part of a lake
            if self.forest[x, y] != 3:
                self.forest[x, y] = 1
                tree = Tree((x, y), self.t, self)
                self.trees[(x, y)] = tree
                return


    def grow_fire(self):
        """
        Iterates over all currently burning fires.
        Calls the update function in the fire class which spreads the fire to neighbors.
        Updates the affected trees in self.forest to their current state while keeping track of the size of the fire.
        """ 
        for fire in self.fires.values():
            fire.update()

            # Iterate over trees which have just been ignited
            for ignited_tree in fire.ignited_trees:

                # Add cell to dictionary burning trees to find it quickly when it needs to be extinguished
                fire.burning_trees[ignited_tree] = self.trees[ignited_tree]

                # Set cell in grid to burning starte
                self.forest[ignited_tree] = 2
                fire.size += 1

                # Remove from dictionary containing non-burning trees
                del self.trees[ignited_tree]

            # Reset list with just ignited trees as they are now all properly burning
            fire.ignited_trees = []

    def lightning_strike(self):
        """
        Selects a random location and sets it on fire.
        If there is a tree, a new fire instance is created.
        Nothing happens if an empty cell is selected.
        """

        # Select random location on grid
        location = tuple(np.random.randint(self.L, size=2))

        # If location has tree, ignite it
        if location in self.trees:
            
            # Ensure fire has correct id for dictionary key
            id = len(self.fires) + len(self.previous_fires)
            fire = Fire(self.t, self.trees[location], id, self)
            self.fires[id] = fire

            # Set cell in grid to burning state
            self.forest[location] = 2
            self.trees[location].t_ignited = self.t
            fire.burning_trees[location] = self.trees[location]

            # Remove from dictionary containing non-burning trees
            del self.trees[location]
            
    def extinguish_trees(self):
        """
        Ensures that the cells which had a burning tree will go back to being empty once the fire stops burning.
        """

        # Iterate over fires
        for fire in self.fires.values():

            # Iterate over trees in fire which are fully burned
            for burned_tree in fire.burned_trees:

                # Remove burned tree from burning trees dictionary and set forest cell to empty
                del fire.burning_trees[burned_tree]
                self.forest[burned_tree] = 0

            # Reset list storing fully burned trees
            fire.burned_trees = []

    def update_fires(self):
        """
        Keep track of the distinction between currently and previously burning fires, as otherwise,
        computation time becomes unnecessarily large for simulations with many timesteps.
        """
        extinguished_fires = {}

        # Iterate over fires which might currently be burning
        for id, fire in self.fires.items():

            # If fire is not burning anymore, add to dictionary containing previous fires
            if not fire.burning:
                self.previous_fires[id] = fire

                # Add to dictionary with fires which are currently being extinguished
                extinguished_fires[id] = fire
    
        # Iterate over extinguished fires
        for id, fire in extinguished_fires.items():

            # If fire still contained by dictionary with burning fires but fire is not burning
            if id in self.fires and not fire.burning:
                fire.t_extinguished = self.t

                # Remove from dictionary with burning fires
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
        visited = set()  #
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while len(visited) < size:
            if 0 <= x < self.L and 0 <= y < self.L:
                if (x, y) not in visited:
                    self.forest[x, y] = 3  
                    visited.add((x, y))

            unvisited_directions = [d for d in directions if (x + d[0], y + d[1]) not in visited and 0 <= x + d[0] < self.L and 0 <= y + d[1] < self.L]
            if unvisited_directions:
                dx, dy = random.choice(unvisited_directions)
            else:
                dx, dy = random.choice(directions)

            x = max(0, min(x + dx, self.L - 1))
            y = max(0, min(y + dy, self.L - 1))

        if len(visited) < size:
            for i in range(self.L):
                for j in range(self.L):
                    if len(visited) >= size:
                        break
                    if (i, j) not in visited:
                        self.forest[i, j] = 3
                        visited.add((i,j))
            
    def record_fire_duration(self, fire_id, duration):
        self.fire_durations[fire_id] = duration


    def do_timestep(self):
        """
        Do timestep by executing all functions in order
        """

        if self.t % self.lightning_frequency == 0:
            self.lightning_strike()

        if not self.freeze_time_during_fire or len(self.fires) == 0:
            self.plant_tree()

        self.grow_fire()
        self.extinguish_trees()
        self.update_fires()
        self.trees_per_timestep.append(len(self.trees))


