import math
import gym
import random
from gym import spaces
import numpy as np
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

class Env(gym.Env):
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self, size, num_players = 0, debug = False):
        super(Env, self).__init__()
        
        self.size = size
        self.current_step = 0
        self.bingo = np.array(random.sample(range(1,self.size*self.size+1), self.size*self.size))
        self.original_bingo_start_list = self.bingo.tolist()
        self.bingo = self.bingo.reshape(self.size,self.size)
        self.original_bingo_start = self.bingo
        self.bingo_state = np.zeros(self.size*self.size).reshape(self.size,self.size).astype('int32')
        self.bingo_selection_count = np.zeros(self.size*self.size).reshape(self.size,self.size).astype('int32')
        self.latest_number_cut = 0
        self.strikes = 0
        self.num_players = num_players
        self.action_space = spaces.Discrete(self.size*self.size)
        #self.action_space = spaces.Box(low=[0] , high=[size*size], dtype=np.int32)
        self.observation_space = spaces.Box(
          low=np.zeros(self.size*self.size).reshape(self.size,self.size), 
            high=np.ones(self.size*self.size).reshape(self.size,self.size), dtype=np.int32)
        self.debug = debug
        
    def reset(self):
               
        self.current_step = 0
        self.bingo = np.array(random.sample(range(1,self.size*self.size+1), self.size*self.size))
        self.original_bingo_start_list = self.bingo.tolist()
        self.bingo = self.bingo.reshape(self.size,self.size)
        self.original_bingo_start = self.bingo
        self.bingo_state = np.zeros(self.size*self.size).reshape(self.size,self.size).astype('int32')
        self.bingo_selection_count = np.zeros(self.size*self.size).reshape(self.size,self.size).astype('int32')
        self.strikes = 0
        #print(self.bingo)
        
        return self._next_observation()
    
    def _next_observation(self):

        current_bingo_state = self.bingo_state   
        

        return np.array(current_bingo_state)
  
    def _take_action(self, action):
        
        self.current_step+=1
        self.latest_number_cut = self.bingo[math.floor(action/self.size),(action)%self.size]           
        is_number_cut = self.bingo_selection_count[math.floor(action/self.size),action%self.size]
    
        already_cut_reward = 0
        if(is_number_cut == 0):
            self.bingo[math.floor(action/self.size),(action)%self.size] = 0
            self.bingo_state[math.floor(action/self.size),action%self.size] = 1
            self.bingo_selection_count[math.floor(action/self.size),action%self.size] = 1
        else:
            self.bingo_selection_count[math.floor(action/self.size),action%self.size] += 1
            already_cut_reward = -self.bingo_selection_count[math.floor(action/self.size),action%self.size]          
        
        #For cuts
        cuts = 0
        for i in range(self.size):
            if(self.bingo_state[i,:].sum() == self.size):
                cuts+=1
            if(self.bingo_state[:,i].sum() == self.size):
                cuts+=1
        
        diag1_sum = 0
        diag2_sum = 0
        
        for i in range(self.size):
            diag1_sum+= self.bingo_state[i,i]
            diag2_sum+= self.bingo_state[i,self.size-i-1]
            
        if(diag1_sum == self.size):            
            cuts+=1
        if(diag2_sum == self.size):            
            cuts+=1
    
        #bingo_dict = {0: "No_cut", 1: "B", 2: "BI", 3: "BIN", 4: "BING", 5: "BINGO", 6: "BINGO", 7: "BINGO"}
        
        reward_for_multiple_cuts = 0
        
        reward_for_multiple_cuts = cuts - self.strikes # +1 reward for a cut, + 2 reward for 2 cuts at the same time
        
        self.strikes = cuts
        
        total_add_reward = already_cut_reward + reward_for_multiple_cuts
                        
        return cuts, total_add_reward
    
    def step(self,action, mode = 'no_play'):
        
        reward = -1
        add_reward = 0
        
        if(mode == 'no_play'): # my turn i.e no players
            total_cuts,add_reward = self._take_action(action)
        else: # opponent's turn
            #tmp_list = list(self.original_bingo_start.reshape(self.size*self.size))
            #Using original because if player says the say number again there is an error
            player_cut_index = self.original_bingo_start_list.index(action)
            #print("player_cut_index ", player_cut_index)
            total_cuts,add_reward = self._take_action(player_cut_index)
        
        reward+= add_reward
        
        if (total_cuts >= self.size):
            done = True
        else:
            done = False
        
        return self._next_observation(), reward, done, self.latest_number_cut, self.bingo, self.strikes
    
    def render(self, mode='train', close=False):
        # Render the environment to the screen
        
        if(mode=='train'):
            if(self.current_step > 500): #Just for check
                print(self.current_step)
            train_list.append([self.bingo, self.bingo_state, self.bingo_selection_count, "BINGO", self.strikes])
           # if (len(train_list) > 510):
            #    train_list = train_list[len(train_list) - 100 :]
        elif(mode == 'test'):
            test_list.append([self.bingo, self.bingo_state, self.bingo_selection_count, "BINGO", self.strikes])                
            #if (len(test_list) > 510):
             #   test_list = test_list[len(test_list) - 100 :]
            
        return
        


if __name__=="__main__":

    size = 5
    model = PPO2.load("deep_bingo_5lakh")
    num_players_playing = int(input("Enter number of players "))
    bingo_env_play = Env(size, num_players = num_players_playing, debug = True)
    obs = bingo_env_play.reset()
    done = False
    player_win = False
    counter = 0
    strike_counter = 0
    while(done ==False and player_win == False):
        #bingo_env_play.render(mode='play')
        for i in range(num_players_playing + 1):
            if(i != num_players_playing):
                msg = "Player " + str(i+1) + " Enter number you are cutting (Enter won/w if you have won): "
                pl_num = input(msg)
                if(pl_num == "won" or pl_num == "w"):
                    print("Congrats! End of game")
                    player_win = True
                    break
                else:
                    pl_num = int(pl_num)
                    obs, rewards, done, num_cut, bingo_curr, curr_strike = bingo_env_play.step(pl_num,"play")
                    
            else:
                action, _states = model.predict(obs)
                obs, rewards, done, info, curr_bingo, comp_strikes = bingo_env_play.step(action, "no_play")
                if(done == True):
                    print("I won. Game over")
                else:
                    print("Number I am striking is ", info)
                    print(curr_bingo)
                    print("")
                    if(strike_counter != comp_strikes):
                        print("I have ", comp_strikes, "strike(s)")
                    strike_counter = comp_strikes
        