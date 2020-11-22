from flask import Flask, request, jsonify, abort
from flask_api import status
import math
import gym
import random
from gym import spaces
import numpy as np
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
import uuid

from environment import Env

app = Flask(__name__)

# Global in memory Database to hold all games' data
# key -> game ID
# value -> environment object which will have the current state of the game for bot
AllGamesDatabase = {}

@app.errorhandler(400)
def custom400(error):
    response = jsonify({"Error": error.description})
    return response, status.HTTP_400_BAD_REQUEST


@app.route("/bingo/start", mehtods = "POST")
def bingo_start():

    data = request.get_json()

    if not request.json or not 'bingo_size' in request.json or not 'num_players' in request.json:
        err_msg ="Bad input. Request not correct."
        print(err_msg)
        abort(400, err_msg)
    
    size = data['bingo_size']
    num_players_playing = data['num_players']

    bingo_env_play = Env(size, num_players = num_players_playing, debug = True)

    game_id = str(uuid.uuid4())
    bingo_env_play.reset()

    AllGamesDatabases[game_id] = bingo_env_play

    return jsonify(message = f"Game started See {request.url}?gameid={workflow_id}", 
                   game_id = workflow_id, href = f"{request.url}?gameid={workflow_id}")


# user's play
@app.route("/bingo/play", mehtods = "POST")
def bingo_play():

    data = request.get_json()

    if not request.json or not 'game_id' in request.json or not 'number_to_cut' in request.json or not 'did_player_win' in request.json:
        err_msg ="Bad input. Request not correct."
        print(err_msg)
        abort(400, err_msg)
        
    gameid = data['game_id']
    didplayerwin = data['did_player_win']

    if didplayerwin:
        msg = "Congrats! You won :)"
        return jsonify(message = msg) 

    if gameid not in AllGamesDatabases:
        err_msg = f"Game id {gameid} not found. Valid Game ids: {AllGamesDatabases.keys()}"
        print(err_msg)
        abort(400, err_msg)

    env = AllGamesDatabase[data['game_id']]

    obs, rewards, done, num_cut, bingo_curr, curr_strike = bingo_env_play.step(pl_num,"player_turn")

    if(done == True):
        msg = "I won. Game over. Better luck next time"
        return jsonify(message = msg) 

    return jsonify(message = "turn received")

# bot's play
@app.route("/bingo/botplay", mehtods = "GET")
def bingo_play():

    data = request.get_json()

    if not request.json or not '' in request.json or not 'num_players' in request.json:
        err_msg ="Bad input. Request not correct."
        print(err_msg)
        abort(400, err_msg)

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
        