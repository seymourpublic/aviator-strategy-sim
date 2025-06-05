import random
import logging

logger = logging.getLogger(__name__)


def generate_crash_multiplier():
    """
    Generate a crash multiplier using exponential distribution
    Ensures safe generation without division by zero
    """
    try:
        r = random.random()
        # Prevent extreme values and division by zero
        if r >= 0.99:
            return 1.0
        # Use a more controlled exponential distribution
        multiplier = 1 / (1 - r)
        return max(1.01, min(multiplier, 1000.0))  # Cap at 1000x
    except Exception as e:
        logger.error(f"Error generating crash multiplier: {e}")
        return 1.01


# Basic strategies (non-realistic versions for backward compatibility)
def early_cashout(rounds, bet, cashout=1.5):
    """Basic early cashout strategy"""
    balance = 0
    history = []

    try:
        for _ in range(rounds):
            crash = generate_crash_multiplier()
            if crash >= cashout:
                profit = (cashout - 1) * bet
                balance += profit
            else:
                balance -= bet
            history.append(round(balance, 2))
    except Exception as e:
        logger.error(f"Error in early_cashout: {e}")
        return []

    return history


def mid_risk(rounds, bet, cashout=2.5):
    """Basic mid-risk strategy"""
    return early_cashout(rounds, bet, cashout)


def high_risk(rounds, bet, cashout=10.0):
    """Basic high-risk strategy"""
    return early_cashout(rounds, bet, cashout)


def dual_bet(rounds, bet1=1.0, cashout1=1.5, bet2=1.0, cashout2=5.0):
    """Basic dual bet strategy"""
    balance = 0
    history = []

    try:
        for _ in range(rounds):
            crash = generate_crash_multiplier()

            # First bet: cash out early
            if crash >= cashout1:
                balance += (cashout1 - 1) * bet1
            else:
                balance -= bet1

            # Second bet: let it ride
            if crash >= cashout2:
                balance += (cashout2 - 1) * bet2
            else:
                balance -= bet2

            history.append(round(balance, 2))
    except Exception as e:
        logger.error(f"Error in dual_bet: {e}")
        return []

    return history


def martingale_strategy(rounds, base_bet=1.0, cashout=2.0, bankroll=100):
    """Basic Martingale strategy"""
    balance = bankroll
    bet = base_bet
    history = []
    current_loss_streak = 0
    max_loss_streak = 0
    ruin_occurred = False

    try:
        for _ in range(rounds):
            if balance < bet:
                ruin_occurred = True
                break  # Out of money

            crash = generate_crash_multiplier()

            if crash >= cashout:
                profit = (cashout - 1) * bet
                balance += profit
                current_loss_streak = 0
                bet = base_bet  # reset
            else:
                balance -= bet
                current_loss_streak += 1
                max_loss_streak = max(max_loss_streak, current_loss_streak)
                bet *= 2  # double

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in martingale_strategy: {e}")
        return {
            "history": [],
            "final_balance": 0.0,
            "ruin_occurred": True,
            "max_loss_streak": 0,
        }

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin_occurred,
        "max_loss_streak": max_loss_streak,
    }


def paroli_strategy(rounds, base_bet=1.0, cashout=2.0, bankroll=100):
    """Basic Paroli strategy"""
    balance = bankroll
    history = []
    win_streak = 0
    bet = base_bet
    max_loss_streak = 0
    loss_streak = 0
    ruin = False

    try:
        for _ in range(rounds):
            if balance < bet:
                ruin = True
                break

            crash = generate_crash_multiplier()

            if crash >= cashout:
                win_streak += 1
                loss_streak = 0
                profit = (cashout - 1) * bet
                balance += profit
                # Cap the progression to prevent extreme bets
                bet = base_bet * (2 ** min(win_streak, 3))
            else:
                balance -= bet
                win_streak = 0
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)
                bet = base_bet

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in paroli_strategy: {e}")
        return {
            "history": [],
            "final_balance": 0.0,
            "ruin_occurred": True,
            "max_loss_streak": 0,
        }

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
    }


def fixed_percent_strategy(rounds, percent=5, cashout=2.0, bankroll=100):
    """Basic fixed percentage strategy"""
    balance = bankroll
    history = []
    max_loss_streak = 0
    loss_streak = 0
    ruin = False

    try:
        for _ in range(rounds):
            bet = round((percent / 100.0) * balance, 2)
            if bet < 0.01 or balance < bet:
                ruin = True
                break

            crash = generate_crash_multiplier()

            if crash >= cashout:
                profit = (cashout - 1) * bet
                balance += profit
                loss_streak = 0
            else:
                balance -= bet
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in fixed_percent_strategy: {e}")
        return {
            "history": [],
            "final_balance": 0.0,
            "ruin_occurred": True,
            "max_loss_streak": 0,
        }

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
    }


def target_profit_strategy(rounds, base_bet=1.0, target_profit=50, cashout=2.0, bankroll=100):
    """Basic target profit strategy"""
    balance = bankroll
    history = []
    current_profit = 0
    ruin = False
    max_loss_streak = 0
    loss_streak = 0
    target_reached = False

    try:
        for _ in range(rounds):
            if current_profit >= target_profit:
                target_reached = True
                break

            if balance < base_bet:
                ruin = True
                break

            crash = generate_crash_multiplier()

            if crash >= cashout:
                profit = (cashout - 1) * base_bet
                balance += profit
                current_profit += profit
                loss_streak = 0
            else:
                balance -= base_bet
                current_profit -= base_bet
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in target_profit_strategy: {e}")
        return {
            "history": [],
            "final_balance": 0.0,
            "ruin_occurred": True,
            "max_loss_streak": 0,
            "target_reached": False,
        }

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "target_reached": target_reached,
    }


def custom_strategy(rounds, bankroll=100, cashout_target=2.0, bet_sequence="1,2,4",
                    max_bet=20, stop_loss=50, take_profit=200, progression_type="loss"):
    """
    Custom strategy with user-defined parameters

    Args:
        rounds: Number of rounds to simulate
        bankroll: Starting bankroll
        cashout_target: Multiplier to cash out at
        bet_sequence: Comma-separated string of bet amounts (e.g., "1,2,4,8")
        max_bet: Maximum bet size allowed
        stop_loss: Stop when bankroll drops to this level
        take_profit: Stop when bankroll reaches this level
        progression_type: "loss" (increase on loss) or "win" (increase on win)
    """
    balance = bankroll
    history = []
    max_loss_streak = 0
    loss_streak = 0
    win_streak = 0
    ruin = False
    target_reached = False

    try:
        # Parse and validate bet sequence
        bet_amounts = []
        for bet_str in bet_sequence.split(','):
            try:
                bet_val = float(bet_str.strip())
                if bet_val > 0:
                    bet_amounts.append(bet_val)
            except ValueError:
                continue

        if not bet_amounts:
            bet_amounts = [1.0]  # fallback

        # Validate parameters
        cashout_target = max(1.01, min(cashout_target, 1000.0))
        max_bet = max(0.01, max_bet)
        stop_loss = max(0, stop_loss)
        take_profit = max(1, take_profit)

        if progression_type not in ["loss", "win"]:
            progression_type = "loss"

        sequence_index = 0
        current_bet = bet_amounts[0]

        for round_num in range(rounds):
            # Check stop conditions
            if balance <= stop_loss:
                ruin = True
                break

            if balance >= take_profit:
                target_reached = True
                break

            # Ensure bet doesn't exceed max_bet or available balance
            current_bet = min(current_bet, max_bet, balance)

            if current_bet < 0.01 or balance < current_bet:
                ruin = True
                break

            crash = generate_crash_multiplier()

            if crash >= cashout_target:
                # Win
                profit = (cashout_target - 1) * current_bet
                balance += profit
                loss_streak = 0
                win_streak += 1

                # Adjust bet based on progression type
                if progression_type == "win":
                    # Increase bet on win (Paroli-style)
                    sequence_index = min(sequence_index + 1, len(bet_amounts) - 1)
                else:
                    # Reset to first bet on win (Martingale-style)
                    sequence_index = 0

            else:
                # Loss
                balance -= current_bet
                win_streak = 0
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)

                # Adjust bet based on progression type
                if progression_type == "loss":
                    # Increase bet on loss (Martingale-style)
                    sequence_index = min(sequence_index + 1, len(bet_amounts) - 1)
                else:
                    # Reset to first bet on loss (Paroli-style)
                    sequence_index = 0

            # Set next bet amount
            current_bet = bet_amounts[sequence_index]
            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in custom_strategy: {e}")
        return {
            "history": [],
            "final_balance": 0.0,
            "ruin_occurred": True,
            "target_reached": False,
            "max_loss_streak": 0,
            "rounds_played": 0,
        }

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "target_reached": target_reached,
        "max_loss_streak": max_loss_streak,
        "rounds_played": len(history),
    }


# Utility functions for strategy validation and testing
def validate_strategy_params(strategy, params):
    """
    Validate strategy parameters and return cleaned/corrected values

    Args:
        strategy: Strategy name
        params: Dictionary of parameters

    Returns:
        Dictionary of validated parameters
    """
    validated = {}

    try:
        # Common validations
        validated['rounds'] = max(1, min(params.get('rounds', 1000), 100000))
        validated['bankroll'] = max(1, params.get('bankroll', 100))
        validated['base_bet'] = max(0.01, params.get('base_bet', 1.0))
        validated['cashout'] = max(1.01, min(params.get('cashout', 2.0), 1000.0))

        # Strategy-specific validations
        if strategy == 'fixed_percent':
            validated['percent'] = max(0.1, min(params.get('percent', 5), 100))

        elif strategy == 'target_profit':
            validated['target_profit'] = max(1, params.get('target_profit', 50))

        elif strategy == 'custom':
            validated['cashout_target'] = max(1.01, min(params.get('cashout_target', 2.0), 1000.0))
            validated['bet_sequence'] = params.get('bet_sequence', '1,2,4')
            validated['max_bet'] = max(0.01, params.get('max_bet', 20))
            validated['stop_loss'] = max(0, params.get('stop_loss', 50))
            validated['take_profit'] = max(1, params.get('take_profit', 200))
            validated['progression_type'] = params.get('progression_type', 'loss')

            if validated['progression_type'] not in ['loss', 'win']:
                validated['progression_type'] = 'loss'

    except Exception as e:
        logger.error(f"Error validating strategy params: {e}")
        # Return safe defaults
        return {
            'rounds': 1000,
            'bankroll': 100,
            'base_bet': 1.0,
            'cashout': 2.0
        }

    return validated


def get_strategy_info(strategy):
    """
    Get information about a strategy including description and required parameters

    Args:
        strategy: Strategy name

    Returns:
        Dictionary with strategy information
    """
    strategies = {
        'early': {
            'name': 'Early Cashout',
            'description': 'Cash out at low multipliers (1.5x) for consistent small wins',
            'risk_level': 'Low',
            'required_params': ['rounds', 'bet'],
            'optional_params': ['cashout']
        },
        'mid': {
            'name': 'Mid Risk',
            'description': 'Cash out at medium multipliers (2.5x) for balanced risk/reward',
            'risk_level': 'Medium',
            'required_params': ['rounds', 'bet'],
            'optional_params': ['cashout']
        },
        'high': {
            'name': 'High Risk',
            'description': 'Cash out at high multipliers (10x) for large but rare wins',
            'risk_level': 'High',
            'required_params': ['rounds', 'bet'],
            'optional_params': ['cashout']
        },
        'dual': {
            'name': 'Dual Bet',
            'description': 'Place two bets with different cashout targets',
            'risk_level': 'Medium',
            'required_params': ['rounds', 'bet1', 'bet2'],
            'optional_params': ['cashout1', 'cashout2']
        },
        'martingale': {
            'name': 'Martingale',
            'description': 'Double bet after each loss to recover previous losses',
            'risk_level': 'Very High',
            'required_params': ['rounds', 'base_bet', 'bankroll'],
            'optional_params': ['cashout']
        },
        'paroli': {
            'name': 'Paroli',
            'description': 'Double bet after each win to maximize winning streaks',
            'risk_level': 'Medium-High',
            'required_params': ['rounds', 'base_bet', 'bankroll'],
            'optional_params': ['cashout']
        },
        'fixed_percent': {
            'name': 'Fixed Percentage',
            'description': 'Bet a fixed percentage of current bankroll',
            'risk_level': 'Medium',
            'required_params': ['rounds', 'percent', 'bankroll'],
            'optional_params': ['cashout']
        },
        'target_profit': {
            'name': 'Target Profit',
            'description': 'Stop when reaching a specific profit target',
            'risk_level': 'Medium',
            'required_params': ['rounds', 'base_bet', 'bankroll', 'target_profit'],
            'optional_params': ['cashout']
        },
        'custom': {
            'name': 'Custom Strategy',
            'description': 'User-defined strategy with custom parameters',
            'risk_level': 'Variable',
            'required_params': ['rounds', 'bankroll', 'cashout_target', 'bet_sequence'],
            'optional_params': ['max_bet', 'stop_loss', 'take_profit', 'progression_type']
        }
    }

    return strategies.get(strategy, {
        'name': 'Unknown',
        'description': 'Unknown strategy',
        'risk_level': 'Unknown',
        'required_params': [],
        'optional_params': []
    })