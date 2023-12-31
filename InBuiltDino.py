import gym
from stable_baselines3 import PPO
from main import DinosaurGame
from gym.envs.registration import register


register(id='Custom-v0',
         entry_point='DinosaurGame',
         max_episode_steps=150,
)

env = gym.make('Custom-v0')
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones = env.step(action)
    env.render()