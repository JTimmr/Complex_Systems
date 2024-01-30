import numpy as np

class Fire:
    def __init__(self, t_ignited, origin, id, forest):
        self.t_ignited = t_ignited
        self.origin = origin
        self.forest = forest
        self.id = id
        self.burning_trees = {origin.coordinates: origin}
        self.burned_trees = []
        self.ignited_trees = []
        self.size = 1
        self.burning = True
        self.t_ignited = t_ignited
        self.t_extinguished = None
        self.spread_steps = 0

    def get_neighbors(self, coordinate):
        up = (coordinate[0], (coordinate[1] - 1) % self.forest.L)
        down = (coordinate[0], (coordinate[1] + 1) % self.forest.L)
        left = ((coordinate[0] - 1) % self.forest.L, coordinate[1])
        right = ((coordinate[0] + 1) % self.forest.L, coordinate[1])
        return [up, down, left, right]

    def update(self):
        """
        Burn neighbors of trees, ensuring fire doesn't spread over lakes.
        """
        new_trees_ignited = False
        for burning_tree in list(self.burning_trees):
            neighbors = self.get_neighbors(burning_tree)
            for neighbor in neighbors:
                # Skip the neighbor if it's a lake and lakes are included
                if self.forest.include_lakes and self.forest.forest[neighbor] == 3:
                    continue

                random_num = np.random.rand(1)[0]
                
                # Apply wind effect if enabled
                if self.forest.wind_effects_enabled:
                    wind_effect = self.calculate_wind_effect(burning_tree, neighbor)
                    ignition_probability = self.forest.g * wind_effect
                else:
                    ignition_probability = self.forest.g

                # If neighbor cell has tree, ignite with probability g
                if neighbor in self.forest.trees and random_num < ignition_probability and neighbor not in self.ignited_trees:
                    self.ignited_trees.append(neighbor)
                    self.forest.trees[neighbor].t_ignited = self.forest.t
                    new_trees_ignited = True
            
            # Remove burning tree after it ignited others
            if self.burning_trees[burning_tree].t_ignited + self.burning_trees[burning_tree].burning_time == self.forest.t:
                self.burned_trees.append(burning_tree)
        if new_trees_ignited:
            self.spread_steps += 1
        
        if len(self.burning_trees) == 0:
            self.burning = False
            self.forest.record_fire_duration(self.id, self.spread_steps)
    
    def get_trees_in_radius(self, center, radius):
            """
            Find all trees within a specified radius of a center point.
            
            """
            trees_in_radius = []
            for tree_coord, tree in self.forest.trees.items():
                if self.distance(center, tree_coord) <= radius:
                    trees_in_radius.append(tree_coord)
            return trees_in_radius

    def distance(self, point1, point2):
            """
            Calculate the Euclidean distance between two points.
            """
            return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        
    def calculate_wind_effect(self, source, target):
        """
        Calculate the effect of wind on fire spread probability.
        
        Args:
        source (tuple): The coordinates of the source tree.
        target (tuple): The coordinates of the target tree.

        Returns:
        float: A multiplier for the ignition probability.
        """
        wind = self.forest.wind
        direction = (target[0] - source[0], target[1] - source[1])
        
        # Dot product to determine if target is downwind or upwind
        dot_product = wind[0] * direction[0] + wind[1] * direction[1]
        
        # Adjust ignition probability based on wind direction
        if dot_product > 0:  # Target is downwind
            return 1 + min(dot_product * 0.1, 0.5)  # Increase probability, max 50% increase
        elif dot_product < 0:  # Target is upwind
            return max(1 - abs(dot_product) * 0.1, 0.5)  # Decrease probability, min 50% of original
        else:
            return 1  # No effect if wind is perpendicular
 
    
