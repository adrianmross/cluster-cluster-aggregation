import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class CCA:
    def __init__(self, L, numberOfParticles):
        self.L = L  # linear lattice dimension
        self.numberOfParticles = numberOfParticles  # number of particles in the system
        self.numberOfClusters = 0  # number of clusters in the system
        self.nnx = [1, 0, -1, 0]  # x offsets for neighbor finding
        self.nny = [0, 1, 0, -1]  # y offsets for neighbor finding
        
        # Initialize arrays
        self.site = np.full((L, L), -1)  # lattice on which clusters move
        self.x = np.zeros(numberOfParticles, dtype=int)  # x locations of particles
        self.y = np.zeros(numberOfParticles, dtype=int)  # y locations of particles
        self.firstParticle = np.zeros(numberOfParticles, dtype=int)
        self.nextParticle = np.full(numberOfParticles, -1, dtype=int)  # initially no next particle
        self.lastParticle = np.zeros(numberOfParticles, dtype=int)
        self.mass = np.zeros(numberOfParticles + 1, dtype=int)  # mass of each cluster
        self.box = np.zeros(L, dtype=int)
    
    def initialize(self):
        # Initialize particles at random locations
        for i in range(self.numberOfParticles):
            while True:
                x_i = np.random.randint(self.L)
                y_i = np.random.randint(self.L)
                if self.site[x_i, y_i] == -1:
                    self.site[x_i, y_i] = self.numberOfClusters
                    break
            
            self.x[i] = x_i
            self.y[i] = y_i
            self.firstParticle[self.numberOfClusters] = i
            self.mass[self.numberOfClusters] = 1
            self.lastParticle[self.numberOfClusters] = i
            self.numberOfClusters += 1
            self.checkNeighbors(x_i, y_i)

    def checkNeighbors(self, x_i, y_i):
        for j in range(4):
            px = (x_i + self.nnx[j]) % self.L
            py = (y_i + self.nny[j]) % self.L
            if (self.site[px, py] != -1) and (self.site[px, py] != self.site[x_i, y_i]):
                self.merge(self.site[px, py], self.site[x_i, y_i])

    
    def merge(self, c1, c2):
        if self.mass[c1] > self.mass[c2]:
            largerClusterLabel = c1
            smallerClusterLabel = c2
        else:
            largerClusterLabel = c2
            smallerClusterLabel = c1

        # Relinking particles
        self.nextParticle[self.lastParticle[largerClusterLabel]] = self.firstParticle[smallerClusterLabel]
        self.lastParticle[largerClusterLabel] = self.lastParticle[smallerClusterLabel]
        self.mass[largerClusterLabel] += self.mass[smallerClusterLabel]

        # Relabeling sites of the smaller cluster
        particle = self.firstParticle[smallerClusterLabel]
        while particle != -1:
            self.site[self.x[particle], self.y[particle]] = largerClusterLabel
            particle = self.nextParticle[particle]

        self.numberOfClusters -= 1

        # Handling last cluster relabeling
        if smallerClusterLabel != self.numberOfClusters:
            particle = self.firstParticle[self.numberOfClusters]
            while particle != -1:
                self.site[self.x[particle], self.y[particle]] = smallerClusterLabel
                particle = self.nextParticle[particle]
            self.firstParticle[smallerClusterLabel] = self.firstParticle[self.numberOfClusters]
            self.lastParticle[smallerClusterLabel] = self.lastParticle[self.numberOfClusters]
            self.mass[smallerClusterLabel] = self.mass[self.numberOfClusters]

    def step(self):
        cluster = np.random.randint(self.numberOfClusters)
        direction = np.random.randint(4)
        dx, dy = self.nnx[direction], self.nny[direction]

        # Clearing old positions
        particle = self.firstParticle[cluster]
        while particle != -1:
            self.site[self.x[particle], self.y[particle]] = -1
            self.x[particle] = (self.x[particle] + dx) % self.L
            self.y[particle] = (self.y[particle] + dy) % self.L
            particle = self.nextParticle[particle]

        # Setting new positions
        particle = self.firstParticle[cluster]
        while particle != -1:
            self.site[self.x[particle], self.y[particle]] = cluster
            self.checkNeighbors(self.x[particle], self.y[particle])
            particle = self.nextParticle[particle]

    def occupiedSiteInCell(self, cell, i, j):
        for ic in range(cell):
            for jc in range(cell):
                if self.site[i + ic, j + jc] > -1:
                    return 1
        return 0
    
    def boxCount(self):
        self.box = np.zeros(self.L, dtype=int)
        cell = 1
        while cell < self.L:
            for i in range(0, self.L - cell + 1, cell):
                for j in range(0, self.L - cell + 1, cell):
                    self.box[cell] += self.occupiedSiteInCell(cell, i, j)
            cell *= 2

    def draw(self):
        # colors = list(mcolors.TABLEAU_COLORS.values())
        # color = black

        # fig, ax = plt.subplots()
        # for i in range(self.numberOfParticles):
        #     if self.site[self.x[i], self.y[i]] != -1:
        #         # ax.add_patch(plt.Rectangle((self.x[i], self.y[i]), 1, 1, color=colors[self.site[self.x[i], self.y[i]] % len(colors)]))
        #         ax.add_patch(plt.Rectangle((self.x[i], self.y[i]), 1, 1, color='black'))
        # ax.set_aspect('equal')
        # plt.xlim(0, self.L)
        # plt.ylim(0, self.L)
        # return fig, ax
        colors = list(mcolors.TABLEAU_COLORS.values())  # or any other colormap
        fig, ax = plt.subplots()
        for i in range(self.numberOfParticles):
            if self.site[self.x[i], self.y[i]] != -1:
                ax.add_patch(plt.Rectangle((self.x[i], self.y[i]), 1, 1, color=colors[self.site[self.x[i], self.y[i]] % len(colors)]))

        ax.set_aspect('equal')
        plt.xlim(0, self.L)
        plt.ylim(0, self.L)
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)  # Close the figure to free memory
        return image

# TESTING
# import cProfile
# import pstats

# def run_simulation(steps):
#     for _ in range(steps):
#         model.step()

# model = CCA(L=50, numberOfParticles=500)
# model.initialize()

# profiler = cProfile.Profile()
# profiler.enable()

# run_simulation(1000)  # Or however many steps you want to simulate

# profiler.disable()
# stats = pstats.Stats(profiler).sort_stats('cumtime')
# stats.print_stats()