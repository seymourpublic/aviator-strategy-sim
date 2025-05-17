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

    result = simulate_strategy(strategy, rounds, bet, bankroll, target_profit, percent_bet)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
