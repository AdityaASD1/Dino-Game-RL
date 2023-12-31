import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import matplotlib.pyplot as plt
from main import DinosaurGame
import random
from tqdm import tqdm
from DQN import DQN_Agent
import numpy as np
'''
Model will take location of dino and obstacle as well as distance between dino and obstacle
Output of model will be action 0 => UP, 1 => Run, 2 => Down 
'''


def trainDQN():
    env = DinosaurGame()
    exp_replay_size = 256
    input_dim = 5
    output_dim = 3
    agent = DQN_Agent(seed=1423, layer_sizes=[input_dim, 256, output_dim], lr=1e-3, sync_freq=5,
                      exp_replay_size=exp_replay_size)
    # agent.load_model('Iter3_128_5Input_3Output')
    losses_list, reward_list, episode_len_list, epsilon_list = [], [], [], []
    index = 128
    episodes = 200
    epsilon = 0.2

    for i in (range(episodes)):
        obs, done, losses, ep_len, rew = env.reset(), False, 0, 1, 0
        while not done:
            ep_len += 1
            A = agent.get_action(obs, 3, epsilon)
            obs_next, reward, done = env.step(A.item())
            agent.collect_experience([obs, A.item(), reward, obs_next])

            obs = obs_next
            rew += reward
            index += 1
            # print(reward)
            if index > 128:
                index = 0
                for j in range(4):
                    loss = agent.train(batch_size=16)
                    losses += loss
        if epsilon > 0.05:
            epsilon -= (1 / 5000)

        losses_list.append(losses / ep_len), reward_list.append(rew), episode_len_list.append(
            ep_len), epsilon_list.append(
            epsilon)
    agent.save_model('Iter1_256')
    return losses_list, reward_list

def playTrained():
    env = DinosaurGame()
    exp_replay_size = 256
    input_dim = 5
    output_dim = 3
    agent = DQN_Agent(seed=1423, layer_sizes=[input_dim, 128, output_dim], lr=1e-3, sync_freq=5,
                      exp_replay_size=exp_replay_size)
    agent.load_model('Iter1_128')
    epsilon = 0
    episodes = 1000
    for i in tqdm(range(episodes)):
        obs, done, losses, ep_len, rew = env.reset(), False, 0, 1, 0
        while (done != True):
            A = agent.get_action(obs, action_space_len=3, epsilon=0)
            obs_next, reward, done = env.step(A.item())
            print(reward)
            obs = obs_next


env = DinosaurGame()
env.run_game()
# playTrained()
# print("Please enter one of the interger below :")
# print("1 : Train DQN model")
# print("2: Run trained DQN model")
# print("3: Play Dino Game")
#
# inp = int(input())
# if inp == 1:
#     losses_list, reward_list = trainDQN()
#     # plt.plot(reward_list)
#     # plt.show()
# elif inp == 2:
#     playTrained()
# elif inp == 3:
#     env = DinosaurGame()
#     env.run_game()
# else:
#     print("Please enter valid number")
# trainDQN()
