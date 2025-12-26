# Ruta: modules/dqn_cavebot.py - DQN avanzado para Tibia (visión del minimapa)

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import logging
import pyautogui
import time
from .utils import GameWindow

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 512)
        self.fc2 = nn.Linear(512, output_size)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

class DQNCavebot:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config
        self.minimap_region = config['regions']['minimap']
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = DQN(3, 8).to(self.device)  # 8 direcciones
        self.target_model = DQN(3, 8).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.00025)

        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.update_target_every = 1000

        self.steps = 0

    def get_state(self):
        img = self.game_window.capture_region(self.minimap_region)
        if img is None:
            return np.zeros((84, 84, 3), dtype=np.uint8)

        img_array = np.array(img)
        resized = cv2.resize(img_array, (84, 84))
        transposed = np.transpose(resized, (2, 0, 1))
        return torch.tensor(transposed, dtype=torch.float32).unsqueeze(0).to(self.device) / 255.0

    def act(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 7)  # Explorar
        with torch.no_grad():
            q_values = self.model(state)
            return q_values.argmax().item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states = torch.cat([e[0] for e in batch])
        actions = torch.tensor([e[1] for e in batch], device=self.device)
        rewards = torch.tensor([e[2] for e in batch], device=self.device, dtype=torch.float32)
        next_states = torch.cat([e[3] for e in batch])
        dones = torch.tensor([e[4] for e in batch], device=self.device, dtype=torch.float32)

        current_q = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        next_q = self.target_model(next_states).max(1)[0]
        target_q = rewards + (1 - dones) * self.gamma * next_q

        loss = nn.MSELoss()(current_q, target_q.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_model.load_state_dict(self.model.state_dict())

    def move(self, action):
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        dx, dy = directions[action]
        if dx > 0: pyautogui.press('right')
        if dx < 0: pyautogui.press('left')
        if dy > 0: pyautogui.press('down')
        if dy < 0: pyautogui.press('up')
        time.sleep(random.uniform(0.3, 0.7))

    def train_step(self, goal):
        state = self.get_state()
        action = self.act(state)
        self.move(action)

        time.sleep(0.5)
        next_state = self.get_state()
        current_pos = self.game_window.get_current_position()  # Usa tu método existente
        reward = 10 if self.is_closer(current_pos, goal) else -1
        if self.is_blocked():
            reward = -50

        done = self.reached_goal(current_pos, goal)
        self.remember(state, action, reward, next_state, done)
        self.replay()

        return done

    def is_closer(self, current, goal):
        # Implementa distancia Manhattan
        pass

    def is_blocked(self):
        # Detecta si no avanzó
        pass

    def reached_goal(self, current, goal):
        return abs(current[0] - goal[0]) <= 1 and abs(current[1] - goal[1]) <= 1