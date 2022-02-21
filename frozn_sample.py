import gym
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import InputLayer
from tensorflow.keras.layers import Dense

env = gym.make('FrozenLake-v1')

discount_factor = 0.95
eps = 0.5
eps_decay_factor = 0.999
num_episodes = 500

model = Sequential()
model.add(InputLayer(batch_input_shape=(1, env.observation_space.n)))
model.add(Dense(20, activation='relu'))
model.add(Dense(env.action_space.n, activation='linear'))
model.compile(loss='mse', optimizer='adam', metrics=['mae'])


for i in range(num_episodes):
    state = env.reset()
    eps *= eps_decay_factor
    done = False
    while not done:
        if np.random.random() < eps:
            action = np.random.randint(0, env.action_space.n)
        else:
            mat = np.identity(env.observation_space.n)[state:state + 1]
            action = np.argmax(model.predict(mat))
        new_state, reward, done, _ = env.step(action)

        mat = np.identity(env.observation_space.n)[new_state:new_state + 1]
        pred = model.predict(mat)
        part = np.max(pred)
        target = reward + discount_factor * part
        woof = np.identity(env.observation_space.n)[state:state + 1]
        target_vector = model.predict(woof)[0]
        target_vector[action] = target

        woof = np.identity(env.observation_space.n)[state:state + 1]
        tv = target_vector.reshape(-1, env.action_space.n)
        model.fit(woof, tv, epochs=1, verbose=0)
        state = new_state
        env.render()
    env.close()