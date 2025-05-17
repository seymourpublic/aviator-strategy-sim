import random


def generate_crash_multiplier():
    r = random.random()
    return max(1.01, 1 / (1 - r)) if r < 0.99 else 1.0


def early_cashout(rounds, bet, cashout=1.5):
    balance, history = 0, []
    for _ in range(rounds):
        crash = generate_crash_multiplier()
        if crash >= cashout:
            profit = (cashout - 1) * bet
            balance += profit
        else:
            balance -= bet
        history.append(round(balance, 2))
    return history


def mid_risk(rounds, bet, cashout=2.5):
    return early_cashout(rounds, bet, cashout)


def high_risk(rounds, bet, cashout=10.0):
    return early_cashout(rounds, bet, cashout)


def dual_bet(rounds, bet1=1.0, cashout1=1.5, bet2=1.0, cashout2=5.0):
    balance, history = 0, []
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
    return history


def martingale_strategy(rounds, base_bet=1.0, cashout=2.0, bankroll=100):
    balance = bankroll
    bet = base_bet
    history = []
    current_loss_streak = 0
    max_loss_streak = 0
    ruin_occurred = False

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

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin_occurred,
        "max_loss_streak": max_loss_streak,
    }


def paroli_strategy(rounds, base_bet=1.0, cashout=2.0, bankroll=100):
    balance = bankroll
    history = []
    win_streak = 0
    bet = base_bet
    max_loss_streak = 0
    loss_streak = 0
    ruin = False

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
            bet = base_bet * (2 ** win_streak)
        else:
            balance -= bet
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
    }


def fixed_percent_strategy(rounds, percent=5, cashout=2.0, bankroll=100):
    balance = bankroll
    history = []
    max_loss_streak = 0
    loss_streak = 0
    ruin = False

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

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
    }


def target_profit_strategy(rounds, base_bet=1.0, target_profit=50, cashout=2.0, bankroll=100):
    balance = bankroll
    history = []
    current_profit = 0
    ruin = False
    max_loss_streak = 0
    loss_streak = 0

    for _ in range(rounds):
        if current_profit >= target_profit:
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

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "max_loss_streak": max_loss_streak,
    }
