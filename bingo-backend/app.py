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


@app.route("/bingo/version", methods = ["GET"])
def bingo_version():
    return jsonify(version= "1.0")

@app.route("/bingo/start", methods = ["POST"])
def bingo_start():

    data = request.get_json()

    if not request.json or not 'bingo_size' in request.json or not 'num_players' in request.json:
        err_msg ="Bad input. Request not correct. Request: {data}"
        print(err_msg)
        abort(400, err_msg)
    
    size = int(data['bingo_size'])
    num_players_playing = int(data['num_players'])

    bingo_env_play = Env(size, num_players = num_players_playing, debug = True)

    game_id = str(uuid.uuid4())
    bingo_env_play.reset()

    AllGamesDatabase[game_id] = bingo_env_play

    return jsonify(message = f"Game started", 
                   game_id = game_id)

# user's play
@app.route("/bingo/play", methods = ["POST"])
def bingo_play():

    data = request.get_json()

    if not request.json or not 'game_id' in request.json or not 'number_to_cut' in request.json:
        err_msg =f"Bad input. Request not correct. Request: {data}"
        print(err_msg)
        abort(400, err_msg)
        
    gameid = data['game_id']
    pl_num = int(data['number_to_cut'])

    if gameid not in AllGamesDatabase:
        err_msg = f"Game id {gameid} not found. Valid Game ids: {AllGamesDatabase.keys()}"
        print(err_msg)
        abort(400, err_msg)

    bingo_env_play = AllGamesDatabase[data['game_id']]

    obs, rewards, done, num_cut, bingo_curr, curr_strike = bingo_env_play.step(pl_num,"player_turn")

    if(done == True):
        listOfNum = [] 
        for i in range(bingo_env_play.size):
            for j in range(bingo_env_play.size):
                listOfNum.append(int(bingo_env_play.bingo[i,j])) 

        msg = None
        if 'player_won' in request.json and data['player_won']:
            msg = "Congrats! I also won :)"
        else:
            msg = "I won. Game over. Better luck next time"
        return jsonify(message = msg, bot_final = listOfNum)
    
    if 'player_won' in request.json and data['player_won']:
        msg = "Congrats! :)"
        return jsonify(message = msg)
        
    return jsonify(message = "Turn received")

# bot's play
@app.route("/bingo/botplay", methods = ["GET"])
def bingo_bot_play():

    data = request.get_json()

    if not request.json or not 'game_id' in request.json:
        err_msg ="Bad input. Request not correct. Request: {data}"
        print(err_msg)
        abort(400, err_msg)
        
    gameid = data['game_id']

    if gameid not in AllGamesDatabase:
        err_msg = f"Game id {gameid} not found. Valid Game ids: {AllGamesDatabase.keys()}"
        print(err_msg)
        abort(400, err_msg)

    bingo_env_play = AllGamesDatabase[data['game_id']]

    action, _states = bingo_env_play.model.predict(bingo_env_play.bingo_state)
    obs, rewards, done, num_cut, bingo_curr, curr_strike = bingo_env_play.step(action, "comp_turn")

    if(done == True):
        listOfNum = [] 
        for i in range(bingo_env_play.size):
            for j in range(bingo_env_play.size):
                listOfNum.append(int(bingo_env_play.bingo[i,j])) 
        msg = "I won. Game over. Better luck next time"
        return jsonify(number = int(num_cut), message = msg, bot_final = listOfNum) 

    return jsonify(number = int(num_cut), message = f"The number I am striking is {int(num_cut)}")

if __name__ == "__main__":
    app.run(host='0.0.0.0')