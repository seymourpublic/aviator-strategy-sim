import random
import time
from strategies import (
    early_cashout, mid_risk, high_risk, dual_bet, martingale_strategy,
    paroli_strategy, fixed_percent_strategy, target_profit_strategy
)


def generate_crash_multiplier():
    r = random.random()
    return max(1.01, 1 / (1 - r)) if r < 0.99 else 1.0


def simulate_network_conditions(enable_realistic=True):
    """Simulate network delays and potential errors"""
    if not enable_realistic:
        return True, 0

    # 95% success rate for network requests
    if random.random() < 0.05:
        return False, 0  # Network error

    # Random delay between 50ms to 500ms
    delay = random.uniform(0.05, 0.5)
    time.sleep(delay)
    return True, delay


def apply_betting_limits(bet_amount, min_bet=0.10, max_bet=1000.0):
    """Apply realistic betting limits"""
    return max(min_bet, min(bet_amount, max_bet))


def simulate_strategy(strategy, rounds, bet, bankroll=100, target_profit=50, percent_bet=5,
                      realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                      network_delay=True, error_simulation=True):
    # Track realistic conditions
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0

    if strategy == "early":
        history, stats = early_cashout_realistic(rounds, bet, cashout=1.5,
                                                 realistic_conditions=realistic_conditions,
                                                 min_bet=min_bet, max_bet=max_bet,
                                                 network_delay=network_delay,
                                                 error_simulation=error_simulation)
        return {
            "history": history,
            "final_balance": history[-1] if history else bankroll,
            "ruin_occurred": False,
            "max_loss_streak": None,
            "network_errors": stats.get("network_errors", 0),
            "total_delay": stats.get("total_delay", 0),
            "bet_limit_hits": stats.get("bet_limit_hits", 0)
        }
    elif strategy == "mid":
        history, stats = mid_risk_realistic(rounds, bet, cashout=2.5,
                                            realistic_conditions=realistic_conditions,
                                            min_bet=min_bet, max_bet=max_bet,
                                            network_delay=network_delay,
                                            error_simulation=error_simulation)
        return {
            "history": history,
            "final_balance": history[-1] if history else bankroll,
            "ruin_occurred": False,
            "max_loss_streak": None,
            "network_errors": stats.get("network_errors", 0),
            "total_delay": stats.get("total_delay", 0),
            "bet_limit_hits": stats.get("bet_limit_hits", 0)
        }
    elif strategy == "high":
        history, stats = high_risk_realistic(rounds, bet, cashout=10.0,
                                             realistic_conditions=realistic_conditions,
                                             min_bet=min_bet, max_bet=max_bet,
                                             network_delay=network_delay,
                                             error_simulation=error_simulation)
        return {
            "history": history,
            "final_balance": history[-1] if history else bankroll,
            "ruin_occurred": False,
            "max_loss_streak": None,
            "network_errors": stats.get("network_errors", 0),
            "total_delay": stats.get("total_delay", 0),
            "bet_limit_hits": stats.get("bet_limit_hits", 0)
        }
    elif strategy == "dual":
        history, stats = dual_bet_realistic(rounds, bet1=bet, bet2=bet, cashout1=1.5, cashout2=5.0,
                                            realistic_conditions=realistic_conditions,
                                            min_bet=min_bet, max_bet=max_bet,
                                            network_delay=network_delay,
                                            error_simulation=error_simulation)
        return {
            "history": history,
            "final_balance": history[-1] if history else bankroll,
            "ruin_occurred": False,
            "max_loss_streak": None,
            "network_errors": stats.get("network_errors", 0),
            "total_delay": stats.get("total_delay", 0),
            "bet_limit_hits": stats.get("bet_limit_hits", 0)
        }
    elif strategy == "martingale":
        return martingale_strategy_realistic(rounds, base_bet=bet, bankroll=bankroll,
                                             realistic_conditions=realistic_conditions,
                                             min_bet=min_bet, max_bet=max_bet,
                                             network_delay=network_delay,
                                             error_simulation=error_simulation)
    elif strategy == "paroli":
        return paroli_strategy_realistic(rounds, base_bet=bet, bankroll=bankroll,
                                         realistic_conditions=realistic_conditions,
                                         min_bet=min_bet, max_bet=max_bet,
                                         network_delay=network_delay,
                                         error_simulation=error_simulation)
    elif strategy == "fixed_percent":
        return fixed_percent_strategy_realistic(rounds, percent=percent_bet, bankroll=bankroll,
                                                realistic_conditions=realistic_conditions,
                                                min_bet=min_bet, max_bet=max_bet,
                                                network_delay=network_delay,
                                                error_simulation=error_simulation)
    elif strategy == "target_profit":
        return target_profit_strategy_realistic(rounds, base_bet=bet, bankroll=bankroll,
                                                target_profit=target_profit,
                                                realistic_conditions=realistic_conditions,
                                                min_bet=min_bet, max_bet=max_bet,
                                                network_delay=network_delay,
                                                error_simulation=error_simulation)
    else:
        return {"error": "Invalid strategy"}


# Realistic versions of the basic strategies
def early_cashout_realistic(rounds, bet, cashout=1.5, realistic_conditions=True,
                            min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    balance, history = 0, []
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0

    for round_num in range(rounds):
        # Apply betting limits
        actual_bet = apply_betting_limits(bet, min_bet, max_bet)
        if actual_bet != bet:
            bet_limit_hits += 1

        # Simulate network conditions
        if realistic_conditions and network_delay:
            success, delay = simulate_network_conditions(error_simulation)
            total_delay += delay

            if not success:
                network_errors += 1
                # Skip this round due to network error
                history.append(round(balance, 2))
                continue

        crash = generate_crash_multiplier()
        if crash >= cashout:
            profit = (cashout - 1) * actual_bet
            balance += profit
        else:
            balance -= actual_bet
        history.append(round(balance, 2))

    stats = {
        "network_errors": network_errors,
        "total_delay": total_delay,
        "bet_limit_hits": bet_limit_hits
    }

    return history, stats


def mid_risk_realistic(rounds, bet, cashout=2.5, realistic_conditions=True,
                       min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    return early_cashout_realistic(rounds, bet, cashout, realistic_conditions,
                                   min_bet, max_bet, network_delay, error_simulation)


def high_risk_realistic(rounds, bet, cashout=10.0, realistic_conditions=True,
                        min_bet=0.10, max_bet=1000.0, network_delay=True, error_simulation=True):
    return early_cashout_realistic(rounds, bet, cashout, realistic_conditions,
                                   min_bet, max_bet, network_delay, error_simulation)


def dual_bet_realistic(rounds, bet1=1.0, cashout1=1.5, bet2=1.0, cashout2=5.0,
                       realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                       network_delay=True, error_simulation=True):
    balance, history = 0, []
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0

    for round_num in range(rounds):
        # Apply betting limits
        actual_bet1 = apply_betting_limits(bet1, min_bet, max_bet)
        actual_bet2 = apply_betting_limits(bet2, min_bet, max_bet)

        if actual_bet1 != bet1 or actual_bet2 != bet2:
            bet_limit_hits += 1

        # Simulate network conditions
        if realistic_conditions and network_delay:
            success, delay = simulate_network_conditions(error_simulation)
            total_delay += delay

            if not success:
                network_errors += 1
                # Skip this round due to network error
                history.append(round(balance, 2))
                continue

        crash = generate_crash_multiplier()

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

    stats = {
        "network_errors": network_errors,
        "total_delay": total_delay,
        "bet_limit_hits": bet_limit_hits
    }

    return history, stats


def martingale_strategy_realistic(rounds, base_bet=1.0, cashout=2.0, bankroll=100,
                                  realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                                  network_delay=True, error_simulation=True):
    balance = bankroll
    bet = base_bet
    history = []
    current_loss_streak = 0
    max_loss_streak = 0
    ruin_occurred = False
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0

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
            success, delay = simulate_network_conditions(error_simulation)
            total_delay += delay

            if not success:
                network_errors += 1
                # Skip this round due to network error
                history.append(round(balance, 2))
                continue

        crash = generate_crash_multiplier()

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

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin_occurred,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits
    }


def paroli_strategy_realistic(rounds, base_bet=1.0, cashout=2.0, bankroll=100,
                              realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                              network_delay=True, error_simulation=True):
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
            success, delay = simulate_network_conditions(error_simulation)
            total_delay += delay

            if not success:
                network_errors += 1
                # Skip this round due to network error
                history.append(round(balance, 2))
                continue

        crash = generate_crash_multiplier()

        if crash >= cashout:
            win_streak += 1
            loss_streak = 0
            profit = (cashout - 1) * actual_bet
            balance += profit
            bet = base_bet * (2 ** win_streak)
        else:
            balance -= actual_bet
            win_streak = 0
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
            bet = base_bet

        history.append(round(balance, 2))

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits
    }


def fixed_percent_strategy_realistic(rounds, percent=5, cashout=2.0, bankroll=100,
                                     realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                                     network_delay=True, error_simulation=True):
    balance = bankroll
    history = []
    max_loss_streak = 0
    loss_streak = 0
    ruin = False
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0

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
            success, delay = simulate_network_conditions(error_simulation)
            total_delay += delay

            if not success:
                network_errors += 1
                # Skip this round due to network error
                history.append(round(balance, 2))
                continue

        crash = generate_crash_multiplier()

        if crash >= cashout:
            profit = (cashout - 1) * actual_bet
            balance += profit
            loss_streak = 0
        else:
            balance -= actual_bet
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)

        history.append(round(balance, 2))

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits
    }


def target_profit_strategy_realistic(rounds, base_bet=1.0, target_profit=50, cashout=2.0, bankroll=100,
                                     realistic_conditions=True, min_bet=0.10, max_bet=1000.0,
                                     network_delay=True, error_simulation=True):
    balance = bankroll
    history = []
    current_profit = 0
    ruin = False
    max_loss_streak = 0
    loss_streak = 0
    network_errors = 0
    total_delay = 0
    bet_limit_hits = 0

    for round_num in range(rounds):
        if current_profit >= target_profit:
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
            success, delay = simulate_network_conditions(error_simulation)
            total_delay += delay

            if not success:
                network_errors += 1
                # Skip this round due to network error
                history.append(round(balance, 2))
                continue

        crash = generate_crash_multiplier()

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

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
        "network_errors": network_errors,
        "total_delay": round(total_delay, 2),
        "bet_limit_hits": bet_limit_hits
    }