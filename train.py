import sys
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
    model_name = "deep_bingo_" + str(size) + "_model_candidate"
    
    bingo_env = Env(size, num_players = 0, debug = True)
    
    
    # Use deterministic actions for evaluation
    eval_callback = EvalCallback(eval_env, best_model_save_path='./logs/',
                             log_path='./logs/', eval_freq=500,
                             deterministic=True, render=False)
    model = PPO2(MlpPolicy, bingo_env,verbose = 0, callback = None)
    
    timesteps = 3000000
    timesteps = int(sys.argv[1])
    print("timesteps", timesteps)
    model.learn(total_timesteps=timesteps)
    model.save(model_name)
    
   
    train_action_list= []
    obs = bingo_env.reset()
    done=False
    while(done == False):
        action, _states = model.predict(obs)
        #print(action)
        obs, rewards, done, num_cut = bingo_env.step(action)
        train_action_list.append(action)
        bingo_env.render(mode='train')
        #print(train_list[-1])
        
    del model
    model = PPO2.load(model_name)
     
    print("Testing the trained model")
    for i in range(20):
    
        test_action_list=[]
        obs = bingo_env.reset()
        done = False
        while(done ==False):
            action, _states = model.predict(obs)
            obs, rewards, done, num_cut = bingo_env.step(action)
            test_action_list.append(action)
            test_list = bingo_env.render(mode='test')
        print(len(test_action_list))
        print(test_list[-1])

   