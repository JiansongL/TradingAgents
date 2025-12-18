"""
Trading Environment for Reinforcement Learning
Wraps TradingAgents system as an RL environment
"""
import numpy as np
from typing import Dict, Tuple, Optional, List
from tradingagents.rl.rl_state_encoder import StateEncoder
from tradingagents.rl.rl_reward import RewardCalculator


class TradingEnvironment:
    """
    RL Environment for trading with TradingAgents
    
    Follows gym-like interface:
    - reset(): Initialize environment
    - step(action): Take action and observe reward
    - render(): Visualize current state
    """
    
    def __init__(
        self,
        state_encoder: Optional[StateEncoder] = None,
        reward_calculator: Optional[RewardCalculator] = None,
        initial_capital: float = 100000.0,
        max_steps: int = 1000,
    ):
        """
        Initialize trading environment
        
        Args:
            state_encoder: State encoder instance
            reward_calculator: Reward calculator instance
            initial_capital: Starting capital
            max_steps: Maximum steps per episode
        """
        self.state_encoder = state_encoder or StateEncoder()
        self.reward_calculator = reward_calculator or RewardCalculator()
        self.initial_capital = initial_capital
        self.max_steps = max_steps
        
        # State tracking
        self.current_step = 0
        self.capital = initial_capital
        self.position = 0  # 0: no position, 1: long, -1: short
        self.entry_price = 0.0
        self.agent_state = {}
        self.trade_history = []
        
        # Action space: BUY, HOLD, SELL
        self.action_space_n = 3
        self.state_dim = self.state_encoder.state_dim
        
    def reset(self, agent_state: Optional[Dict] = None) -> np.ndarray:
        """
        Reset environment to initial state
        
        Args:
            agent_state: Initial agent state from TradingAgents
            
        Returns:
            initial_state: Encoded initial state vector
        """
        self.current_step = 0
        self.capital = self.initial_capital
        self.position = 0
        self.entry_price = 0.0
        self.trade_history = []
        
        if agent_state:
            self.agent_state = agent_state
        
        return self.state_encoder.encode(self.agent_state)
    
    def step(
        self,
        action: int,
        agent_state: Dict,
        current_price: float,
    ) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Take action in environment
        
        Args:
            action: Action to take (0=BUY, 1=HOLD, 2=SELL)
            agent_state: Updated agent state from TradingAgents
            current_price: Current asset price
            
        Returns:
            next_state: Next state vector
            reward: Reward for the action
            done: Whether episode is finished
            info: Additional information
        """
        self.current_step += 1
        self.agent_state = agent_state
        
        action_str = self.state_encoder.decode_action(action, self.action_space_n)
        
        reward = 0.0
        info = {
            "action": action_str,
            "position": self.position,
            "capital": self.capital,
            "step": self.current_step,
        }
        
        # Execute action
        if action_str == "BUY" and self.position == 0:
            # Open long position
            self.position = 1
            self.entry_price = current_price
            info["entry_price"] = self.entry_price
            
        elif action_str == "SELL" and self.position == 1:
            # Close long position
            reward = self.reward_calculator.calculate_reward(
                "BUY",
                self.entry_price,
                current_price,
            )
            
            # Update capital
            pnl = ((current_price - self.entry_price) / self.entry_price) * self.capital
            self.capital += pnl
            
            # Record trade
            self.trade_history.append({
                "entry": self.entry_price,
                "exit": current_price,
                "pnl": pnl,
                "reward": reward,
            })
            
            self.position = 0
            self.entry_price = 0.0
            
            info["exit_price"] = current_price
            info["pnl"] = pnl
            info["trade_result"] = "profit" if pnl > 0 else "loss"
        
        # Check if episode is done
        done = (
            self.current_step >= self.max_steps or
            self.capital <= 0 or
            self.capital >= self.initial_capital * 2  # Stop if doubled capital
        )
        
        # Encode next state
        next_state = self.state_encoder.encode(self.agent_state)
        
        return next_state, reward, done, info
    
    def step_options(
        self,
        action: int,
        agent_state: Dict,
        strategy: str,
        premium: float,
        pnl: float,
        max_loss: float,
        greeks: Optional[Dict[str, float]] = None,
    ) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Take options trading action
        
        Args:
            action: Action to take
            agent_state: Agent state
            strategy: Options strategy
            premium: Option premium
            pnl: Current P&L
            max_loss: Maximum possible loss
            greeks: Greeks dictionary
            
        Returns:
            next_state, reward, done, info
        """
        self.current_step += 1
        self.agent_state = agent_state
        
        action_str = "BUY" if action == 0 else "SELL"
        
        # Calculate reward for options trade
        reward = self.reward_calculator.calculate_options_reward(
            action_str,
            strategy,
            premium,
            pnl,
            max_loss,
            greeks,
        )
        
        # Update capital
        self.capital += pnl
        
        # Record trade
        self.trade_history.append({
            "strategy": strategy,
            "premium": premium,
            "pnl": pnl,
            "reward": reward,
            "greeks": greeks,
        })
        
        info = {
            "action": action_str,
            "strategy": strategy,
            "capital": self.capital,
            "pnl": pnl,
            "step": self.current_step,
        }
        
        # Check if done
        done = (
            self.current_step >= self.max_steps or
            self.capital <= self.initial_capital * 0.5 or  # Lost 50%
            self.capital >= self.initial_capital * 1.5  # Gained 50%
        )
        
        next_state = self.state_encoder.encode(self.agent_state)
        
        return next_state, reward, done, info
    
    def calculate_profit_probability(
        self,
        state: np.ndarray,
        action: int,
    ) -> float:
        """
        Calculate probability of profit for given state-action pair
        
        This is a placeholder - actual implementation would use trained model
        
        Args:
            state: Current state vector
            action: Action to evaluate
            
        Returns:
            probability: Probability of profit (0 to 1)
        """
        # TODO: Implement with trained model
        # For now, return based on simple heuristics
        
        # Extract some features (assuming we know their positions)
        trend = state[8] if len(state) > 8 else 0  # Trend feature
        sentiment = state[17] if len(state) > 17 else 0  # News sentiment
        
        if action == 0:  # BUY
            # Higher probability if trend and sentiment are positive
            prob = 0.5 + (trend * 0.2) + (sentiment * 0.2)
        elif action == 2:  # SELL
            # Higher probability if trend and sentiment are negative
            prob = 0.5 + (-trend * 0.2) + (-sentiment * 0.2)
        else:  # HOLD
            prob = 0.5
        
        return np.clip(prob, 0.0, 1.0)
    
    def get_trade_statistics(self) -> Dict:
        """
        Get statistics from trade history
        
        Returns:
            stats: Dictionary of trading statistics
        """
        if not self.trade_history:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "total_pnl": 0.0,
                "sharpe_ratio": 0.0,
            }
        
        pnls = [trade.get("pnl", 0) for trade in self.trade_history]
        wins = [pnl for pnl in pnls if pnl > 0]
        losses = [pnl for pnl in pnls if pnl < 0]
        
        stats = {
            "total_trades": len(self.trade_history),
            "win_rate": len(wins) / len(self.trade_history) if self.trade_history else 0,
            "avg_profit": np.mean(wins) if wins else 0,
            "avg_loss": np.mean(losses) if losses else 0,
            "total_pnl": sum(pnls),
            "sharpe_ratio": self.reward_calculator.calculate_sharpe_ratio_reward(
                np.array(pnls)
            ),
            "final_capital": self.capital,
            "return_pct": ((self.capital - self.initial_capital) / self.initial_capital) * 100,
        }
        
        return stats
    
    def render(self, mode: str = "human") -> None:
        """
        Render current environment state
        
        Args:
            mode: Render mode ("human" or "rgb_array")
        """
        if mode == "human":
            print(f"\n=== Trading Environment Step {self.current_step} ===")
            print(f"Capital: ${self.capital:,.2f}")
            print(f"Position: {self.position}")
            print(f"Total Trades: {len(self.trade_history)}")
            
            stats = self.get_trade_statistics()
            print(f"Win Rate: {stats['win_rate']:.2%}")
            print(f"Total P&L: ${stats['total_pnl']:,.2f}")
            print(f"Return: {stats['return_pct']:.2f}%")
