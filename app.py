import math
import gym
import random
from gym import spaces
import numpy as np
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from environment import Env


if __name__=="__main__":

    size = int(input("Enter bingo size "))
    model_name = "deep_bingo_" + str(size) + "_final"
    model = PPO2.load(model_name)
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
                    obs, rewards, done, num_cut, bingo_curr, curr_strike = bingo_env_play.step(pl_num,"player_turn")
                    
            else:
                action, _states = model.predict(obs)
                obs, rewards, done, info, curr_bingo, comp_strikes = bingo_env_play.step(action, "comp_turn")
                if(done == True):
                    print("I won. Game over")
                else:
                    print("Number I am striking is ", info)
                    print(curr_bingo)
                    print("")
                    if(strike_counter != comp_strikes):
                        print("I have ", comp_strikes, "strike(s)")
                    strike_counter = comp_strikes
        