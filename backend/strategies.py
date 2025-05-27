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

    # Parse bet sequence
    try:
        bet_amounts = [float(x.strip()) for x in bet_sequence.split(',')]
    except:
        bet_amounts = [1.0]  # fallback

    if not bet_amounts:
        bet_amounts = [1.0]

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

    return {
        "history": history,
        "final_balance": round(balance, 2),
        "ruin_occurred": ruin,
        "target_reached": target_reached,
        "max_loss_streak": max_loss_streak,
        "rounds_played": len(history),
    }