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

    def get_neighbors(self, coordinate):
        up = (coordinate[0], (coordinate[1] - 1) % self.forest.L)
        down = (coordinate[0], (coordinate[1] + 1) % self.forest.L)
        left = ((coordinate[0] - 1) % self.forest.L, coordinate[1])
        right = ((coordinate[0] + 1) % self.forest.L, coordinate[1])
        return [up, down, left, right]

    def update(self):
        """
        Burn neighbors of trees
        """
        for burning_tree in self.burning_trees:
            neighbors = self.get_neighbors(burning_tree)
            for neighbor in neighbors:
                random_num = np.random.rand(1)[0]

                # If neighbor cell has tree, ignite with probability g
                if neighbor in self.forest.trees and random_num < self.forest.g and neighbor not in self.ignited_trees:
                    self.ignited_trees.append(neighbor)
                    self.forest.trees[neighbor].t_ignited = self.forest.t
            
            # Remove burning tree after it ignited others
            if self.burning_trees[burning_tree].t_ignited + self.burning_trees[burning_tree].burning_time == self.forest.t:
                self.burned_trees.append(burning_tree)
        
        if len(self.burning_trees) == 0:
            self.burning = False
