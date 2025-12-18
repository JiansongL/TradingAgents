"""
Training script for RL Trading Agent
"""
import numpy as np
from typing import Dict, Optional
from tradingagents.rl.rl_agent import RLTradingAgent
from tradingagents.rl.rl_environment import TradingEnvironment
from tradingagents.rl.rl_state_encoder import StateEncoder
from tradingagents.rl.rl_reward import RewardCalculator
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()


class RLTrainer:
    """Trainer for RL Trading Agent"""
    
    def __init__(
        self,
        trading_agents_config: Optional[Dict] = None,
        state_dim: int = 128,
        action_dim: int = 3,
        episodes: int = 1000,
        max_steps_per_episode: int = 100,
    ):
        """
        Initialize trainer
        
        Args:
            trading_agents_config: Config for TradingAgents system
            state_dim: State vector dimension
            action_dim: Number of actions
            episodes: Number of training episodes
            max_steps_per_episode: Max steps per episode
        """
        self.config = trading_agents_config or DEFAULT_CONFIG.copy()
        self.episodes = episodes
        self.max_steps = max_steps_per_episode
        
        # Initialize components
        self.state_encoder = StateEncoder(state_dim=state_dim)
        self.reward_calculator = RewardCalculator()
        self.env = TradingEnvironment(
            state_encoder=self.state_encoder,
            reward_calculator=self.reward_calculator,
            max_steps=max_steps_per_episode,
        )
        self.rl_agent = RLTradingAgent(
            state_dim=state_dim,
            action_dim=action_dim,
        )
        
        # Initialize TradingAgents (for generating states)
        self.trading_agents = TradingAgentsGraph(
            debug=False,
            config=self.config,
        )
        
        # Training history
        self.episode_rewards = []
        self.episode_lengths = []
        self.win_rates = []
        
    def train(
        self,
        tickers: list = ["NVDA", "AAPL", "TSLA"],
        dates: list = None,
        save_path: str = "./models/rl_trading_agent.pth",
    ):
        """
        Train RL agent
        
        Args:
            tickers: List of ticker symbols to train on
            dates: List of dates to use for training
            save_path: Path to save trained model
        """
        if dates is None:
            # Generate some training dates
            dates = ["2024-05-10", "2024-06-15", "2024-07-20", "2024-08-25"]
        
        print("=" * 80)
        print("Starting RL Trading Agent Training")
        print("=" * 80)
        print(f"Episodes: {self.episodes}")
        print(f"Tickers: {tickers}")
        print(f"Max steps per episode: {self.max_steps}")
        print("=" * 80)
        
        for episode in range(self.episodes):
            # Randomly select ticker and date
            ticker = np.random.choice(tickers)
            date = np.random.choice(dates)
            
            # Get initial state from TradingAgents
            try:
                agent_state, decision = self.trading_agents.propagate(ticker, date)
                
                # Extract current price (mock for now)
                current_price = 100.0 + np.random.randn() * 10
                
            except Exception as e:
                print(f"Error in episode {episode}: {e}")
                continue
            
            # Reset environment
            state = self.env.reset(agent_state)
            episode_reward = 0
            
            # Run episode
            for step in range(self.max_steps):
                # Select action
                action = self.rl_agent.select_action(state, training=True)
                
                # Simulate price movement
                price_change = np.random.randn() * 0.02  # 2% volatility
                next_price = current_price * (1 + price_change)
                
                # Take step in environment
                next_state, reward, done, info = self.env.step(
                    action,
                    agent_state,
                    next_price,
                )
                
                # Store experience
                self.rl_agent.store_experience(
                    state, action, reward, next_state, done
                )
                
                # Train
                loss = self.rl_agent.train_step()
                
                # Update state and price
                state = next_state
                current_price = next_price
                episode_reward += reward
                
                if done:
                    break
            
            # Record episode stats
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(step + 1)
            
            stats = self.env.get_trade_statistics()
            self.win_rates.append(stats['win_rate'])
            
            # Print progress
            if (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_win_rate = np.mean(self.win_rates[-10:])
                rl_stats = self.rl_agent.get_training_stats()
                
                print(f"Episode {episode + 1}/{self.episodes}")
                print(f"  Avg Reward (last 10): {avg_reward:.2f}")
                print(f"  Avg Win Rate (last 10): {avg_win_rate:.2%}")
                print(f"  Epsilon: {rl_stats['epsilon']:.3f}")
                print(f"  Buffer Size: {rl_stats['buffer_size']}")
                print()
            
            # Save checkpoint
            if (episode + 1) % 100 == 0:
                self.rl_agent.save_model(save_path)
                self.plot_training_progress(f"./training_progress_ep{episode+1}.png")
        
        # Final save
        self.rl_agent.save_model(save_path)
        print(f"\nTraining completed! Model saved to {save_path}")
        
        # Plot final results
        self.plot_training_progress("./training_final.png")
        
        return self.rl_agent
    
    def plot_training_progress(self, save_path: str = None):
        """Plot training progress"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Episode rewards
        axes[0, 0].plot(self.episode_rewards)
        axes[0, 0].set_title("Episode Rewards")
        axes[0, 0].set_xlabel("Episode")
        axes[0, 0].set_ylabel("Total Reward")
        axes[0, 0].grid(True)
        
        # Moving average of rewards
        if len(self.episode_rewards) > 20:
            window = 20
            moving_avg = np.convolve(
                self.episode_rewards,
                np.ones(window) / window,
                mode='valid'
            )
            axes[0, 1].plot(moving_avg)
            axes[0, 1].set_title(f"Moving Average Reward (window={window})")
            axes[0, 1].set_xlabel("Episode")
            axes[0, 1].set_ylabel("Avg Reward")
            axes[0, 1].grid(True)
        
        # Episode lengths
        axes[1, 0].plot(self.episode_lengths)
        axes[1, 0].set_title("Episode Lengths")
        axes[1, 0].set_xlabel("Episode")
        axes[1, 0].set_ylabel("Steps")
        axes[1, 0].grid(True)
        
        # Win rates
        axes[1, 1].plot(self.win_rates)
        axes[1, 1].set_title("Win Rates")
        axes[1, 1].set_xlabel("Episode")
        axes[1, 1].set_ylabel("Win Rate")
        axes[1, 1].grid(True)
        axes[1, 1].set_ylim([0, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Training progress plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()


if __name__ == "__main__":
    # Example training
    trainer = RLTrainer(
        episodes=100,  # Start with fewer episodes for testing
        max_steps_per_episode=50,
    )
    
    trained_agent = trainer.train(
        tickers=["NVDA", "AAPL"],
        save_path="./models/rl_trading_agent.pth",
    )
    
    print("\n" + "=" * 80)
    print("Training Statistics:")
    print("=" * 80)
    stats = trained_agent.get_training_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
