class Tree:
    def __init__(self, coordinates, t_planted, forest):
        self.coordinates = coordinates
        self.t_planted = t_planted
        self.t_ignited = 0
        self.forest = forest
        self.t = t_planted
        self.burning_time = 1
        self.state_history = []  # Store the state at each time step

    # def update_state(self, state):
    #     self.state_history.append(state)