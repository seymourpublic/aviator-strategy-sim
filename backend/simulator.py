import random
import logging
from strategies import (
    early_cashout, mid_risk, high_risk, dual_bet, martingale_strategy,
    paroli_strategy, fixed_percent_strategy, target_profit_strategy,
    custom_strategy
)

logger = logging.getLogger(__name__)


def generate_crash_multiplier():
    """Generate a crash multiplier using exponential distribution"""
    try:
        r = random.random()
        # Prevent division by zero and ensure minimum multiplier
        if r >= 0.99:
            return 1.0
        return max(1.01, 1 / (1 - r))
    except Exception as e:
        logger.error(f"Error generating crash multiplier: {e}")
        return 1.01


def simulate_network_conditions(enable_realistic=True, enable_errors=True):
    """
    Simulate network delays and potential errors without blocking
    Returns: (success: bool, delay: float)
    """
    if not enable_realistic:
        return True, 0

    # 5% chance of network error when errors are enabled
    if enable_errors and random.random() < 0.05:
        return False, 0  # Network error

    # Simulate delay time (but don't actually sleep)
    # In a real implementation, this would be handled by async/await
    delay = random.uniform(0.05, 0.5)
    return True, delay


def apply_betting_limits(bet_amount, min_bet=0.10, max_bet=1000.0):
    """Apply realistic betting limits and return adjusted bet"""
    if bet_amount < min_bet:
        return min_bet
    if bet_amount > max_bet:
        return max_bet
    return bet_amount


def simulate_strategy(strategy, rounds, bet, bankroll=100, target_profit=50, percent_bet=5,
                      realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                      network_delay=True, error_simulation=True, custom_params=None):
    """
    Main simulation function that routes to appropriate strategy
    """
    try:
        logger.info(f"Starting simulation: {strategy} strategy, {rounds} rounds")

        if strategy == "early":
            return early_cashout_realistic(
                rounds, bet, cashout=1.5,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "mid":
            return mid_risk_realistic(
                rounds, bet, cashout=2.5,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "high":
            return high_risk_realistic(
                rounds, bet, cashout=10.0,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "dual":
            return dual_bet_realistic(
                rounds, bet1=bet, bet2=bet, cashout1=1.5, cashout2=5.0,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "martingale":
            return martingale_strategy_realistic(
                rounds, base_bet=bet, bankroll=bankroll,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "paroli":
            return paroli_strategy_realistic(
                rounds, base_bet=bet, bankroll=bankroll,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "fixed_percent":
            return fixed_percent_strategy_realistic(
                rounds, percent=percent_bet, bankroll=bankroll,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "target_profit":
            return target_profit_strategy_realistic(
                rounds, base_bet=bet, bankroll=bankroll,
                target_profit=target_profit,
                realistic_conditions=realistic_conditions,
                min_bet=min_bet, max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        elif strategy == "custom":
            if not custom_params:
                return {"error": "Custom strategy requires additional parameters"}

            return custom_strategy_realistic(
                rounds=rounds,
                bankroll=bankroll,
                cashout_target=custom_params['cashout_target'],
                bet_sequence=custom_params['bet_sequence'],
                max_bet_custom=custom_params['max_bet'],
                stop_loss=custom_params['stop_loss'],
                take_profit=custom_params['take_profit'],
                progression_type=custom_params['progression_type'],
                realistic_conditions=realistic_conditions,
                min_bet=min_bet,
                max_bet=max_bet,
                network_delay=network_delay,
                error_simulation=error_simulation
            )

        else:
            return {"error": f"Invalid strategy: {strategy}"}

    except Exception as e:
        logger.error(f"Error in simulate_strategy: {e}")
        return {"error": f"Simulation failed: {str(e)}"}


def create_base_result_dict():
    """Create base result dictionary with default values"""
    return {
        "history": [],
        "final_balance": 0.0,
        "ruin_occurred": False,
        "max_loss_streak": 0,
        "network_errors": 0,
        "total_delay": 0.0,
        "bet_limit_hits": 0,
        "rounds_played": 0
    }


# Realistic versions of the basic strategies
def early_cashout_realistic(rounds, bet, cashout=1.5, realistic_conditions=True,
                            min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    """Early cashout strategy with realistic conditions"""
    balance = 0
    history = []
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0

    try:
        for round_num in range(rounds):
            # Apply betting limits
            actual_bet = apply_betting_limits(bet, min_bet, max_bet)
            if actual_bet != bet:
                bet_limit_hits += 1

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            if crash >= cashout:
                profit = (cashout - 1) * actual_bet
                balance += profit
            else:
                balance -= actual_bet

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in early_cashout_realistic: {e}")
        return {"error": f"Early cashout simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": False,
        "max_loss_streak": None,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits,
        "rounds_played": rounds_played
    }


def mid_risk_realistic(rounds, bet, cashout=2.5, realistic_conditions=True,
                       min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    """Mid risk strategy - just calls early_cashout_realistic with different cashout"""
    return early_cashout_realistic(rounds, bet, cashout, realistic_conditions,
                                   min_bet, max_bet, network_delay, error_simulation)


def high_risk_realistic(rounds, bet, cashout=10.0, realistic_conditions=True,
                        min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    """High risk strategy - just calls early_cashout_realistic with different cashout"""
    return early_cashout_realistic(rounds, bet, cashout, realistic_conditions,
                                   min_bet, max_bet, network_delay, error_simulation)


def dual_bet_realistic(rounds, bet1=1.0, cashout1=1.5, bet2=1.0, cashout2=5.0,
                       realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                       network_delay=True, error_simulation=True):
    """Dual bet strategy with realistic conditions"""
    balance = 0
    history = []
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0

    try:
        for round_num in range(rounds):
            # Apply betting limits
            actual_bet1 = apply_betting_limits(bet1, min_bet, max_bet)
            actual_bet2 = apply_betting_limits(bet2, min_bet, max_bet)

            if actual_bet1 != bet1 or actual_bet2 != bet2:
                bet_limit_hits += 1

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            # First bet: cash out early
            if crash >= cashout1:
                balance += (cashout1 - 1) * actual_bet1
            else:
                balance -= actual_bet1

            # Second bet: let it ride
            if crash >= cashout2:
                balance += (cashout2 - 1) * actual_bet2
            else:
                balance -= actual_bet2

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in dual_bet_realistic: {e}")
        return {"error": f"Dual bet simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": False,
        "max_loss_streak": None,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits,
        "rounds_played": rounds_played
    }


def martingale_strategy_realistic(rounds, base_bet=1.0, cashout=2.0, bankroll=100,
                                  realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                                  network_delay=True, error_simulation=True):
    """Martingale strategy with realistic conditions"""
    balance = bankroll
    bet = base_bet
    history = []
    current_loss_streak = 0
    max_loss_streak = 0
    ruin_occurred = False
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0

    try:
        for round_num in range(rounds):
            # Apply betting limits
            actual_bet = apply_betting_limits(bet, min_bet, max_bet)
            if actual_bet != bet:
                bet_limit_hits += 1

            if balance < actual_bet:
                ruin_occurred = True
                break  # Out of money

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            if crash >= cashout:
                profit = (cashout - 1) * actual_bet
                balance += profit
                current_loss_streak = 0
                bet = base_bet  # reset
            else:
                balance -= actual_bet
                current_loss_streak += 1
                max_loss_streak = max(max_loss_streak, current_loss_streak)
                bet *= 2  # double

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in martingale_strategy_realistic: {e}")
        return {"error": f"Martingale simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin_occurred,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits,
        "rounds_played": rounds_played
    }


def paroli_strategy_realistic(rounds, base_bet=1.0, cashout=2.0, bankroll=100,
                              realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                              network_delay=True, error_simulation=True):
    """Paroli strategy with realistic conditions"""
    balance = bankroll
    history = []
    win_streak = 0
    bet = base_bet
    max_loss_streak = 0
    loss_streak = 0
    ruin = False
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0

    try:
        for round_num in range(rounds):
            # Apply betting limits
            actual_bet = apply_betting_limits(bet, min_bet, max_bet)
            if actual_bet != bet:
                bet_limit_hits += 1

            if balance < actual_bet:
                ruin = True
                break

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            if crash >= cashout:
                win_streak += 1
                loss_streak = 0
                profit = (cashout - 1) * actual_bet
                balance += profit
                bet = base_bet * (2 ** min(win_streak, 3))  # Cap win streak progression
            else:
                balance -= actual_bet
                win_streak = 0
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)
                bet = base_bet

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in paroli_strategy_realistic: {e}")
        return {"error": f"Paroli simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits,
        "rounds_played": rounds_played
    }


def fixed_percent_strategy_realistic(rounds, percent=5, cashout=2.0, bankroll=100,
                                     realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                                     network_delay=True, error_simulation=True):
    """Fixed percent strategy with realistic conditions"""
    balance = bankroll
    history = []
    max_loss_streak = 0
    loss_streak = 0
    ruin = False
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0

    try:
        for round_num in range(rounds):
            bet = round((percent / 100.0) * balance, 2)

            # Apply betting limits
            actual_bet = apply_betting_limits(bet, min_bet, max_bet)
            if actual_bet != bet:
                bet_limit_hits += 1

            if actual_bet < 0.01 or balance < actual_bet:
                ruin = True
                break

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            if crash >= cashout:
                profit = (cashout - 1) * actual_bet
                balance += profit
                loss_streak = 0
            else:
                balance -= actual_bet
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in fixed_percent_strategy_realistic: {e}")
        return {"error": f"Fixed percent simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits,
        "rounds_played": rounds_played
    }


def target_profit_strategy_realistic(rounds, base_bet=1.0, target_profit=50, cashout=2.0, bankroll=100,
                                     realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                                     network_delay=True, error_simulation=True):
    """Target profit strategy with realistic conditions"""
    balance = bankroll
    history = []
    current_profit = 0
    ruin = False
    max_loss_streak = 0
    loss_streak = 0
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0
    target_reached = False

    try:
        for round_num in range(rounds):
            if current_profit >= target_profit:
                target_reached = True
                break

            # Apply betting limits
            actual_bet = apply_betting_limits(base_bet, min_bet, max_bet)
            if actual_bet != base_bet:
                bet_limit_hits += 1

            if balance < actual_bet:
                ruin = True
                break

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            if crash >= cashout:
                profit = (cashout - 1) * actual_bet
                balance += profit
                current_profit += profit
                loss_streak = 0
            else:
                balance -= actual_bet
                current_profit -= actual_bet
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)

            history.append(round(balance, 2))

    except Exception as e:
        logger.error(f"Error in target_profit_strategy_realistic: {e}")
        return {"error": f"Target profit simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "target_reached": target_reached,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits,
        "rounds_played": rounds_played
    }


def custom_strategy_realistic(rounds, bankroll=100, cashout_target=2.0, bet_sequence="1,2,4",
                              max_bet_custom=20, stop_loss=50, take_profit=200,
                              progression_type="loss", realistic_conditions=True,
                              min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    """Custom strategy with realistic conditions"""
    balance = bankroll
    history = []
    max_loss_streak = 0
    loss_streak = 0
    win_streak = 0
    ruin = False
    target_reached = False
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0
    rounds_played = 0

    try:
        # Parse bet sequence
        bet_amounts = [float(x.strip()) for x in bet_sequence.split(',') if x.strip()]
        if not bet_amounts:
            bet_amounts = [1.0]  # fallback

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

            # Ensure bet doesn't exceed limits
            current_bet = min(current_bet, max_bet_custom, balance)

            # Apply global betting limits
            actual_bet = apply_betting_limits(current_bet, min_bet, max_bet)
            if actual_bet != current_bet:
                bet_limit_hits += 1

            if actual_bet < 0.01 or balance < actual_bet:
                ruin = True
                break

            # Simulate network conditions
            if realistic_conditions and network_delay:
                success, delay = simulate_network_conditions(True, error_simulation)
                total_delay += delay

                if not success:
                    network_errors += 1
                    # Skip this round due to network error
                    history.append(round(balance, 2))
                    continue

            crash = generate_crash_multiplier()
            rounds_played += 1

            if crash >= cashout_target:
                # Win
                profit = (cashout_target - 1) * actual_bet
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
                balance -= actual_bet
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
        logger.error(f"Error in custom_strategy_realistic: {e}")
        return {"error": f"Custom strategy simulation failed: {str(e)}"}

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "target_reached": target_reached,
        "max_loss_streak": max_loss_streak,
        "rounds_played": rounds_played,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits
    }