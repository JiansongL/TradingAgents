"""
Reward Calculator for RL Model
Calculates rewards based on trading outcomes
"""
import numpy as np
from typing import Dict, Optional


class RewardCalculator:
    """
    Calculates rewards for the RL agent based on trading performance
    
    Reward structure:
    - Profit: +1 for profit, -1 for loss
    - Risk-adjusted: Consider position size and volatility
    - Transaction costs: Penalize frequent trading
    """
    
    def __init__(
        self,
        profit_reward: float = 1.0,
        loss_penalty: float = -1.0,
        transaction_cost: float = 0.01,
        risk_penalty_weight: float = 0.1,
    ):
        """
        Initialize reward calculator
        
        Args:
            profit_reward: Reward for profitable trade
            loss_penalty: Penalty for losing trade
            transaction_cost: Cost per transaction (as fraction)
            risk_penalty_weight: Weight for risk penalty
        """
        self.profit_reward = profit_reward
        self.loss_penalty = loss_penalty
        self.transaction_cost = transaction_cost
        self.risk_penalty_weight = risk_penalty_weight
        
    def calculate_reward(
        self,
        action: str,
        entry_price: float,
        exit_price: float,
        position_size: float = 1.0,
        volatility: Optional[float] = None,
    ) -> float:
        """
        Calculate reward for a trading action
        
        Args:
            action: "BUY", "SELL", "HOLD"
            entry_price: Entry price of the trade
            exit_price: Exit price of the trade
            position_size: Size of the position (shares/contracts)
            volatility: Market volatility (for risk adjustment)
            
        Returns:
            reward: Calculated reward value
        """
        if action == "HOLD":
            # No transaction, no reward/penalty
            return 0.0
        
        # Calculate profit/loss
        if action == "BUY":
            pnl = (exit_price - entry_price) / entry_price
        elif action == "SELL":
            pnl = (entry_price - exit_price) / entry_price
        else:
            return 0.0
        
        # Base reward: +1 for profit, -1 for loss
        if pnl > 0:
            reward = self.profit_reward
        else:
            reward = self.loss_penalty
        
        # Scale by profit magnitude
        reward *= abs(pnl) * 10  # Scale to make rewards meaningful
        
        # Subtract transaction cost
        reward -= self.transaction_cost
        
        # Risk adjustment
        if volatility is not None:
            risk_penalty = volatility * self.risk_penalty_weight
            reward -= risk_penalty
        
        return float(reward)
    
    def calculate_options_reward(
        self,
        action: str,
        strategy: str,
        premium: float,
        pnl: float,
        max_loss: float,
        greeks: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate reward for options trading
        
        Args:
            action: "BUY" or "SELL"
            strategy: Options strategy name
            premium: Premium paid/received
            pnl: Profit/loss at expiration or close
            max_loss: Maximum possible loss
            greeks: Dictionary of Greeks values
            
        Returns:
            reward: Calculated reward value
        """
        # Base reward from P&L
        if pnl > 0:
            reward = self.profit_reward
        else:
            reward = self.loss_penalty
        
        # Scale by P&L magnitude relative to premium
        if premium > 0:
            reward *= abs(pnl) / premium
        
        # Risk-adjusted by max loss
        if max_loss > 0:
            risk_ratio = abs(pnl) / max_loss
            reward *= (1 + risk_ratio)
        
        # Greeks-based adjustment
        if greeks:
            # Penalize high negative theta (time decay)
            if 'theta' in greeks and greeks['theta'] < 0:
                reward -= abs(greeks['theta']) * 0.1
            
            # Penalize high gamma risk
            if 'gamma' in greeks:
                reward -= abs(greeks['gamma']) * 0.05
        
        # Subtract transaction cost
        reward -= self.transaction_cost
        
        return float(reward)
    
    def calculate_sharpe_ratio_reward(
        self,
        returns: np.ndarray,
        risk_free_rate: float = 0.02,
    ) -> float:
        """
        Calculate reward based on Sharpe ratio
        
        Args:
            returns: Array of returns
            risk_free_rate: Risk-free rate (annual)
            
        Returns:
            reward: Sharpe ratio as reward
        """
        if len(returns) == 0:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        sharpe = (mean_return - risk_free_rate) / std_return
        return float(sharpe)
    
    def calculate_profit_probability_reward(
        self,
        current_price: float,
        target_price: float,
        stop_loss: float,
        probability_up: float,
    ) -> float:
        """
        Calculate expected reward based on profit probability
        
        Args:
            current_price: Current asset price
            target_price: Target profit price
            stop_loss: Stop loss price
            probability_up: Probability of price going up
            
        Returns:
            expected_reward: Expected reward value
        """
        # Calculate potential profit and loss
        potential_profit = (target_price - current_price) / current_price
        potential_loss = (current_price - stop_loss) / current_price
        
        # Expected value
        expected_profit = potential_profit * probability_up
        expected_loss = potential_loss * (1 - probability_up)
        
        expected_value = expected_profit - expected_loss
        
        # Convert to reward
        if expected_value > 0:
            reward = self.profit_reward * expected_value * 10
        else:
            reward = self.loss_penalty * abs(expected_value) * 10
        
        return float(reward)
    
    def calculate_win_rate_reward(
        self,
        wins: int,
        losses: int,
        avg_win: float,
        avg_loss: float,
    ) -> float:
        """
        Calculate reward based on historical win rate
        
        Args:
            wins: Number of winning trades
            losses: Number of losing trades
            avg_win: Average win amount
            avg_loss: Average loss amount
            
        Returns:
            reward: Reward based on win rate and profit factor
        """
        total_trades = wins + losses
        if total_trades == 0:
            return 0.0
        
        win_rate = wins / total_trades
        
        # Profit factor
        if avg_loss != 0:
            profit_factor = (wins * avg_win) / (losses * abs(avg_loss))
        else:
            profit_factor = wins * avg_win
        
        # Combine win rate and profit factor
        reward = (win_rate - 0.5) * 2 + (profit_factor - 1)
        
        return float(reward)
