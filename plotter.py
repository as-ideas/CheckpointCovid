import numpy as np
import matplotlib.patches as patches
from matplotlib import pyplot as plt

class Plotter:
    """ Only for plotting, can be safely ignored. """
    
    def __init__(self, world_map):
        self.map = world_map
        
    def plot_mgrid(self):
        plt.xticks(self.map.marks)
        plt.yticks(self.map.marks)
        plt.grid()
    def plot_pos(self, pos, color):
        plt.scatter(pos[:,0], pos[:,1], color=color)
        
    def plot_data_in_mgrid(self, server, sample_user_id):
        self.plot_mgrid()
        inf_pos = server.data[server.data['user_id'].isin(server.infected_users)][['x', 'y']]
        healthy_pos = server.data[~server.data['user_id'].isin(server.infected_users)][['x', 'y']]
        sample_user = server.data[server.data['user_id']==sample_user_id][['x','y']]
        self.plot_pos(np.array(inf_pos), color='red')
        self.plot_pos(np.array(healthy_pos), color='blue')
        self.plot_pos(np.array(sample_user), color='green')
        plt.show()
        
    def plot_with_patches(self, collisions, server, sample_user_id):
        fig,ax = plt.subplots(1)
        loc = np.where(np.sum(np.array([self.map.tiles==i for i in collisions.index]), axis = 0) ==1)
        patch_coord= [np.array(loc)[:,i]*self.map.marks[1] for i in range(len(loc[1]))]
        for coo in patch_coord:
            patch = patches.Rectangle(coo, self.map.marks[1],self.map.marks[1])
            patch.set_alpha(0.1)
            ax.add_patch(patch)
        self.plot_data_in_mgrid(server, sample_user_id)