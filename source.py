import numpy as np
import pandas as pd

class Map:
    """ Map prototype, square grid with grid_size*grid_size tiles. """
    
    def __init__(self, grid_size):
        self.marks = np.linspace(0,1,grid_size)
        self.tiles = np.arange(grid_size*grid_size).reshape(grid_size,grid_size)
        self.indexes = np.arange(grid_size)
    
    def coordinate_to_tile(self, coo):
        return self.tiles[self.indexes[coo[0]>=self.marks][-1], self.indexes[coo[1]>=self.marks][-1]]

class User:
    """ User class (represents local device).
        Stores list of contacts with timestep
            [(user1, time1), (user2, time1), (user14, time5), ...] 
            
        Checks for infections in contacts given list of infected users.
        Reports to the server its infected status whenever new contacts are added.
    """
    
    def __init__(self, user_id):
        self.contacts = {}
        self.infected = 0
        self.id = user_id
        self.infected_users = {}
    
    def add_contact(self, t, user_ids, tile):
        for user in user_ids:
            if self.id != user:
                if user in self.contacts:
                    self.contacts[user].append(t)
                else:
                    self.contacts[user] = [t]
        return self.is_infected()
    
    def is_infected(self):
        if not self.infected:
            for user in self.infected_users:
                if user in self.contacts:
                    r = np.array(self.contacts[user])
                    if any(r>=self.infected_users[user]):
                        self.infected = r[r>=self.infected_users[user]][0]
                        return self.infected
            return 0
        else:
            return self.infected
        
        
class Server: 
    """ Has positional data at only 1 time step at a time in order to form collisions (multiple users in same tile).
        Sends users lists of collision groups so that the users can update their local contacts history.
        Keeps a list of infected users.
        
        Does NOT store contact history information, which are only stored locally.
    """
    def __init__(self, n_users, world_map, initial_pos):
        self.user_ids = np.arange(n_users)
        self.users = {}
        for user in self.user_ids:
            self.users[user] = User(user)
        self.map = world_map
        data = pd.DataFrame(initial_pos, columns=['x', 'y']) #pandas apply is convenient
        data['count'] = 1
        data['user_id'] = self.user_ids
        self.data = data
        self.__place_users()
        self.infected_users = {}
        self.infect_list_update = False
        
    def update_pos(self, pos):
        """ Should be done by id... """
        self.data[['x', 'y']] = pos
        self.__place_users()
        
    def __place_users(self):
        """ Assigns user coordinates to tiles. """
        
        self.data['tile'] = self.data[['x', 'y']].T.apply(self.map.coordinate_to_tile)
        
    def find_collisions(self):
        """ Groups users by tile.
            Checks which tiles have multiple users.
            
            Returns list of [int: tile_n, list: user_ids]
                [[tile1, [user1, user2]], 
                 [tile18, [user4, user98],
                 ...
                ]
            
        """
        
        tile_groups = self.data[['user_id', 'count', 'tile']].groupby(['tile'])
        user_per_tile = tile_groups['count'].sum()
        tiles_multiple_users = user_per_tile.index[user_per_tile > 1]
        contact_groups = tile_groups['user_id'].apply(list)[tiles_multiple_users]
        return contact_groups
    
    def check_infection_groups(self, collisions, time_step):
        """ Queries the users if they have been in contact with infected people.
            Sends list of contact group to users part of contact groups.
            Users answer with positive or negative infection (as a timestap).
        """
        new_infections = False
        for tile in collisions.index:
            for user_id in collisions[tile]:
                # query user
                user_infected = self.users[user_id].add_contact(t=time_step, user_ids=collisions[tile], tile=tile)
                if user_infected:
                    if self.__is_new_infection(user_id, time_step):
                        new_infections = True
        return new_infections
    
    def add_infections(self, user_id, t):
        """ Represents the user message to the server. """
        
        infect_list_update = False
        self.users[user_id].infected = t
        if self.__is_new_infection(user_id, t):
            for user in self.user_ids:
                # update user
                # ask the user on their contact sequence
                self.users[user].infected_users = self.infected_users
                if self.users[user].is_infected():
                    self.infected_users.update({user: t})
                    infect_list_update = True
        return infect_list_update
    
    
    def __is_new_infection(self, user_id, t):
        """ Checks if the infection is a new or older one. """
        
        if (user_id not in self.infected_users) or (self.infected_users[user_id] > t):
            self.infected_users.update({user_id: t})
            print(f'user {user_id} has been infected at time {t}.')
            return True
        else:
            return False