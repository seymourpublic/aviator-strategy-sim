from flask import Flask, request, jsonify
from flask_cors import CORS
from simulator import simulate_strategy

app = Flask(__name__)
CORS(app)


@app.route('/simulate', methods=['GET'])
def simulate():
    strategy = request.args.get('strategy', 'early')
    rounds = int(request.args.get('rounds', 1000))
    bet = float(request.args.get('bet', 1.0))
    bankroll = float(request.args.get('bankroll', 100))
    target_profit = float(request.args.get('target_profit', 50))
    percent_bet = float(request.args.get('percent_bet', 5))

    # Custom strategy parameters
    cashout_target = float(request.args.get('cashout_target', 2.0))
    bet_sequence = request.args.get('bet_sequence', '1,2,4')
    max_bet = float(request.args.get('max_bet', 20))
    stop_loss = float(request.args.get('stop_loss', 50))
    take_profit = float(request.args.get('take_profit', 200))
    progression_type = request.args.get('progression_type', 'loss')

    result = simulate_strategy(
        strategy=strategy,
        rounds=rounds,
        bet=bet,
        bankroll=bankroll,
        target_profit=target_profit,
        percent_bet=percent_bet,
        cashout_target=cashout_target,
        bet_sequence=bet_sequence,
        max_bet=max_bet,
        stop_loss=stop_loss,
        take_profit=take_profit,
        progression_type=progression_type
    )
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=8000)