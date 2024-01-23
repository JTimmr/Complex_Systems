import time
from matplotlib import animation, colors
import numpy as np
import matplotlib.pyplot as plt
# import numba as nb
# from numba import njit, prange
EMPTY, TREE, BURNING, BOUDARY = 0, 1, 2, 3

def initialize_forest(size: tuple, tree_density:float) -> np.ndarray:
    return np.pad(array=np.random.choice([EMPTY, TREE], size=size, p=[1 - tree_density, tree_density]), pad_width=1, mode='constant', constant_values=BOUDARY)

def plant_tree(forest: np.ndarray) -> np.ndarray:
    empty_indices = np.argwhere(forest == EMPTY)
    if empty_indices.size == 0:
        return forest
    random_index: int = np.random.choice(empty_indices.shape[0])
    x, y = empty_indices[random_index]
    forest[x, y] = TREE
    return forest

def strike_tree(forest: np.ndarray) -> np.ndarray:
    empty_indices = np.argwhere(a=forest == TREE)
    if empty_indices.size == 0:
        return forest
    random_index: int = np.random.choice(empty_indices.shape[0])
    x, y = empty_indices[random_index]
    forest[x, y] = BURNING
    return forest

def update_forest(forest: np.ndarray , growth_prob: float, lightning_prob: float, ortho_burn_prob: float, diag_burn_prob: float, mode = "parallel") -> np.ndarray:
  new_forest = forest.copy()
  # orthogonal neighbors
  up = np.roll(a=forest, shift=-1, axis=0)
  down = np.roll(a=forest, shift=1, axis=0)
  left = np.roll(a=forest, shift=-1, axis=1)
  right = np.roll(a=forest, shift=1, axis=1)
  # diagonal neighbors
  up_left = np.roll(a=up, shift=-1, axis=1)
  up_right = np.roll(a=up, shift=1, axis=1)
  down_left = np.roll(a=down, shift=-1, axis=1)
  down_right = np.roll(a=down, shift=1, axis=1)
  ortho_burning_neighbors = (up == BURNING) | (down == BURNING) | (left == BURNING) | (right == BURNING)
  diag_burning_neighbors = (up_left == BURNING) | (up_right == BURNING) | (down_left == BURNING) | (down_right == BURNING)
  burn_from_ortho = (np.random.rand(*forest.shape) < ortho_burn_prob) & ortho_burning_neighbors
  burn_from_diag = (np.random.rand(*forest.shape) < diag_burn_prob) & diag_burning_neighbors
  new_forest[(forest == TREE) & (burn_from_ortho | burn_from_diag)] = BURNING
  new_forest[forest == BURNING] = EMPTY
    # mode where evey cell has a probability to catch fire and grow
  if mode == "parallel":
    growth = (np.random.rand(*forest.shape) < growth_prob) & (forest == EMPTY)
    new_forest[growth] = TREE
    # Lightning strikes
    lightning = (np.random.rand(*forest.shape) < lightning_prob) & (forest == TREE)
    new_forest[lightning] = BURNING
    # Mode where only one cell can catch fire and grow
  if mode == "sequential":
    new_forest = plant_tree(forest=new_forest)
    # growth = (np.random.rand(*forest.shape) < growth_prob) & (forest == EMPTY)
    # new_forest[growth] = TREE
    prob_of_lightning = np.random.random()
    fire_counts = np.argwhere(a=forest ==  BURNING)
    if (fire_counts.size == 0) & (prob_of_lightning < 0.1):
            x, y = np.random.randint(low=new_forest.shape[0], size=2)
            new_forest[x, y] = BURNING
  return new_forest

# @njit(parallel=True)
# def update_forest_parallel(forest, growth_prob, lightning_prob, ortho_burn_prob=0.69, diag_burn_prob=0.42):
#     new_forest = np.copy(forest)
#     rows, cols = forest.shape

#     for i in prange(rows):
#         for j in prange(cols):
#             if forest[i, j] == TREE:
#                 # Checking and updating based on the state of neighboring cells
#                 # Using modulo operation for periodic boundary conditions
#                 for di in range(-1, 2):
#                     for dj in range(-1, 2):
#                         if di == 0 and dj == 0:
#                             continue
#                         ni, nj = (i + di) % rows, (j + dj) % cols
#                         if forest[ni, nj] == BURNING:
#                             burn_prob = diag_burn_prob if di != 0 and dj != 0 else ortho_burn_prob
#                             if np.random.rand() < burn_prob:
#                                 new_forest[i, j] = BURNING
#                                 break

#                 if new_forest[i, j] == TREE and np.random.rand() < lightning_prob:
#                     new_forest[i, j] = BURNING

#             elif forest[i, j] == BURNING:
#                 new_forest[i, j] = EMPTY
#             elif forest[i, j] == EMPTY:
#                 if np.random.rand() < growth_prob:
#                     new_forest[i, j] = TREE

#     return new_forest

def run_simulation(size: tuple, tree_density: float, iterations: int, fire_start, growth_prob: float, lightning_prob: float, ortho_burn_prob: float, diag_burn_prob: float) -> None:
    forest = initialize_forest(size=size, tree_density=tree_density)
    fig, ax = plt.subplots(figsize=(10, 10))
    taken = 0
    imgs = []
    for _ in range(iterations):
        start_time = time.time()
        forest = update_forest(forest=forest, growth_prob=growth_prob, lightning_prob=lightning_prob, ortho_burn_prob=ortho_burn_prob, diag_burn_prob=diag_burn_prob)
        taken += time.time() - start_time
        imgs.append([ax.imshow(forest, animated=True, cmap=colors.ListedColormap(colors=['brown', 'green', 'orange']), vmin=0, vmax=2)])
    print("Total time taken: {:.2f} seconds".format(taken))
    ani = animation.ArtistAnimation(fig=fig, artists=imgs, interval=0.01, blit=True, repeat_delay=1000)
    plt.show()

# Parameters
size = (200, 200) 
tree_density = 0.99 
iterations = 5000   
fire_start = (250, 250)
growth_prob = 0.0001
ortho_burn_prob = 0.99
diag_burn_prob = 0.8
lightning_prob = 0.0001 

run_simulation(size=size, tree_density=tree_density, iterations=iterations, fire_start=fire_start, growth_prob=growth_prob, lightning_prob=lightning_prob, ortho_burn_prob=ortho_burn_prob, diag_burn_prob=diag_burn_prob)