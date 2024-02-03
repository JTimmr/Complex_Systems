class Tree:
    def __init__(self, coordinates, t_planted, forest):
        self.coordinates = coordinates
        self.t_planted = t_planted
        self.t_ignited = 0
        self.forest = forest
        self.t = t_planted

        # Number of timesteps the tree will burn. Currently always set to 1
        self.burning_time = 1
        self.state_history = []