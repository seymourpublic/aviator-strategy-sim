import random
from strategies import (
    early_cashout, mid_risk, high_risk, dual_bet, martingale_strategy,
    paroli_strategy, fixed_percent_strategy, target_profit_strategy
)


def generate_crash_multiplier():
    r = random.random()
    return max(1.01, 1 / (1 - r)) if r < 0.99 else 1.0


def simulate_strategy(strategy, rounds, bet, bankroll=100, target_profit=50, percent_bet=5):
    if strategy == "early":
        history = early_cashout(rounds, bet, cashout=1.5)
        return {"history": history, "final_balance": history[-1], "ruin_occurred": False, "max_loss_streak": None}
    elif strategy == "mid":
        history = mid_risk(rounds, bet, cashout=2.5)
        return {"history": history, "final_balance": history[-1], "ruin_occurred": False, "max_loss_streak": None}
    elif strategy == "high":
        history = high_risk(rounds, bet, cashout=10.0)
        return {"history": history, "final_balance": history[-1], "ruin_occurred": False, "max_loss_streak": None}
    elif strategy == "dual":
        history = dual_bet(rounds, bet1=bet, bet2=bet, cashout1=1.5, cashout2=5.0)
        return {"history": history, "final_balance": history[-1], "ruin_occurred": False, "max_loss_streak": None}
    elif strategy == "martingale":
        return martingale_strategy(rounds, base_bet=bet, bankroll=bankroll)
    elif strategy == "paroli":
        return paroli_strategy(rounds, base_bet=bet, bankroll=bankroll)
    elif strategy == "fixed_percent":
        return fixed_percent_strategy(rounds, percent=percent_bet, bankroll=bankroll)
    elif strategy == "target_profit":
        return target_profit_strategy(rounds, base_bet=bet, bankroll=bankroll, target_profit=target_profit)
    else:
        return {"error": "Invalid strategy"}

