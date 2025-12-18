"""
Reinforcement Learning Trading Agent
Uses Deep Q-Network (DQN) to learn optimal trading strategies
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from typing import Dict, List, Tuple, Optional
import os
import json


class DQN(nn.Module):
    """Deep Q-Network for trading decisions"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 128, 64]):
        """
        Initialize DQN
        
        Args:
            state_dim: Dimension of state vector
            action_dim: Number of actions (usually 3: BUY, HOLD, SELL)
            hidden_dims: List of hidden layer dimensions
        """
        super(DQN, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            state: State tensor
            
        Returns:
            q_values: Q-values for each action
        """
        return self.network(state)


class ReplayBuffer:
    """Experience replay buffer"""
    
    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer
        
        Args:
            capacity: Maximum buffer size
        """
        self.buffer = deque(maxlen=capacity)
    
    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> Tuple:
        """Sample batch from buffer"""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones),
        )
    
    def __len__(self) -> int:
        return len(self.buffer)


class RLTradingAgent:
    """
    Reinforcement Learning agent for trading decisions
    
    Uses DQN to learn Q-values for state-action pairs
    Outputs profit probability for each action
    """
    
    def __init__(
        self,
        state_dim: int = 128,
        action_dim: int = 3,
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        buffer_capacity: int = 10000,
        batch_size: int = 64,
        target_update_freq: int = 10,
        device: str = "cpu",
    ):
        """
        Initialize RL trading agent
        
        Args:
            state_dim: State dimension
            action_dim: Number of actions
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon_start: Initial exploration rate
            epsilon_end: Minimum exploration rate
            epsilon_decay: Exploration decay rate
            buffer_capacity: Replay buffer capacity
            batch_size: Training batch size
            target_update_freq: Frequency to update target network
            device: Device to run model on ("cpu" or "cuda")
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.device = torch.device(device)
        
        # Q-networks
        self.policy_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)
        
        # Training tracking
        self.training_step = 0
        self.episode_rewards = []
        self.losses = []
        
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state
            training: Whether in training mode
            
        Returns:
            action: Selected action index
        """
        if training and random.random() < self.epsilon:
            # Explore: random action
            return random.randrange(self.action_dim)
        else:
            # Exploit: best action from Q-network
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return q_values.argmax().item()
    
    def get_profit_probability(self, state: np.ndarray, action: int) -> float:
        """
        Get profit probability for state-action pair
        
        Args:
            state: Current state
            action: Action to evaluate
            
        Returns:
            probability: Estimated probability of profit (0 to 1)
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            
            # Convert Q-value to probability using softmax
            probabilities = torch.softmax(q_values, dim=1)
            prob = probabilities[0, action].item()
            
            return prob
    
    def get_all_action_probabilities(self, state: np.ndarray) -> Dict[str, float]:
        """
        Get profit probability for all actions
        
        Args:
            state: Current state
            
        Returns:
            probabilities: Dict mapping action names to probabilities
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            
            # Convert to probabilities
            probabilities = torch.softmax(q_values, dim=1)[0]
            
            action_names = ["BUY", "HOLD", "SELL"]
            return {
                name: prob.item()
                for name, prob in zip(action_names, probabilities)
            }
    
    def store_experience(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        """Store experience in replay buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train_step(self) -> Optional[float]:
        """
        Perform one training step
        
        Returns:
            loss: Training loss value, or None if not enough samples
        """
        if len(self.replay_buffer) < self.batch_size:
            return None
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(
            self.batch_size
        )
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        # Current Q-values
        current_q_values = self.policy_net(states).gather(1, actions)
        
        # Target Q-values
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0].unsqueeze(1)
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.loss_fn(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network
        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        
        loss_value = loss.item()
        self.losses.append(loss_value)
        
        return loss_value
    
    def save_model(self, path: str):
        """
        Save model to disk
        
        Args:
            path: Path to save model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step,
            'episode_rewards': self.episode_rewards,
        }, path)
        
        # Save config
        config_path = path.replace('.pth', '_config.json')
        with open(config_path, 'w') as f:
            json.dump({
                'state_dim': self.state_dim,
                'action_dim': self.action_dim,
                'gamma': self.gamma,
                'epsilon': self.epsilon,
                'training_step': self.training_step,
            }, f, indent=2)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """
        Load model from disk
        
        Args:
            path: Path to load model from
        """
        checkpoint = torch.load(path, map_location=self.device)
        
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.training_step = checkpoint['training_step']
        self.episode_rewards = checkpoint.get('episode_rewards', [])
        
        print(f"Model loaded from {path}")
    
    def get_training_stats(self) -> Dict:
        """
        Get training statistics
        
        Returns:
            stats: Dictionary of training statistics
        """
        if not self.episode_rewards:
            return {
                'total_episodes': 0,
                'avg_reward': 0.0,
                'avg_loss': 0.0,
                'epsilon': self.epsilon,
            }
        
        return {
            'total_episodes': len(self.episode_rewards),
            'avg_reward': np.mean(self.episode_rewards[-100:]),  # Last 100 episodes
            'avg_loss': np.mean(self.losses[-100:]) if self.losses else 0.0,
            'epsilon': self.epsilon,
            'training_steps': self.training_step,
            'buffer_size': len(self.replay_buffer),
        }
