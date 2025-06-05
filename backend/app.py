from flask import Flask, request, jsonify
from flask_cors import CORS
from simulator import simulate_strategy
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_float(value, default, min_val=None, max_val=None, name="parameter"):
    """Validate and convert string to float with bounds checking"""
    try:
        result = float(value) if value is not None else default
        if min_val is not None and result < min_val:
            logger.warning(f"{name} {result} below minimum {min_val}, using {min_val}")
            return min_val
        if max_val is not None and result > max_val:
            logger.warning(f"{name} {result} above maximum {max_val}, using {max_val}")
            return max_val
        return result
    except (ValueError, TypeError):
        logger.warning(f"Invalid {name} value: {value}, using default: {default}")
        return default


def validate_int(value, default, min_val=None, max_val=None, name="parameter"):
    """Validate and convert string to int with bounds checking"""
    try:
        result = int(value) if value is not None else default
        if min_val is not None and result < min_val:
            logger.warning(f"{name} {result} below minimum {min_val}, using {min_val}")
            return min_val
        if max_val is not None and result > max_val:
            logger.warning(f"{name} {result} above maximum {max_val}, using {max_val}")
            return max_val
        return result
    except (ValueError, TypeError):
        logger.warning(f"Invalid {name} value: {value}, using default: {default}")
        return default


def validate_bool(value, default, name="parameter"):
    """Validate and convert string to boolean"""
    if value is None:
        return default
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)


def validate_bet_sequence(bet_sequence, default="1,2,4"):
    """Validate and parse bet sequence"""
    if not bet_sequence:
        return default.split(',')

    try:
        # Parse and validate bet sequence
        bets = [float(x.strip()) for x in bet_sequence.split(',') if x.strip()]
        if not bets:
            logger.warning(f"Empty bet sequence, using default: {default}")
            return default.split(',')

        # Ensure all bets are positive
        valid_bets = [max(0.01, bet) for bet in bets]
        if valid_bets != [float(x) for x in bets]:
            logger.warning("Some bet values were below 0.01, adjusted to minimum")

        return [str(bet) for bet in valid_bets]
    except Exception as e:
        logger.warning(f"Invalid bet sequence '{bet_sequence}': {e}, using default: {default}")
        return default.split(',')


@app.route('/simulate', methods=['GET'])
def simulate():
    try:
        # Basic parameters with validation
        strategy = request.args.get('strategy', 'early')
        if strategy not in ['early', 'mid', 'high', 'dual', 'martingale', 'paroli',
                            'fixed_percent', 'target_profit', 'custom']:
            return jsonify({"error": f"Invalid strategy: {strategy}"}), 400

        rounds = validate_int(request.args.get('rounds'), 1000, 1, 100000, "rounds")
        bet = validate_float(request.args.get('bet'), 1.0, 0.01, 10000, "bet")
        bankroll = validate_float(request.args.get('bankroll'), 100, 1, 1000000, "bankroll")
        target_profit = validate_float(request.args.get('target_profit'), 50, 1, 1000000, "target_profit")
        percent_bet = validate_float(request.args.get('percent_bet'), 5, 0.1, 100, "percent_bet")

        # Realistic conditions parameters with validation
        realistic_conditions = validate_bool(request.args.get('realistic_conditions'), True)
        min_bet = validate_float(request.args.get('min_bet'), 0.10, 0.01, 1000, "min_bet")
        max_bet = validate_float(request.args.get('max_bet'), 1000.0, 1, 100000, "max_bet")
        network_delay = validate_bool(request.args.get('network_delay'), True)
        error_simulation = validate_bool(request.args.get('error_simulation'), True)

        # Ensure min_bet <= max_bet
        if min_bet > max_bet:
            logger.warning(f"min_bet ({min_bet}) > max_bet ({max_bet}), swapping values")
            min_bet, max_bet = max_bet, min_bet

        # Custom strategy parameters with validation
        custom_params = {}
        if strategy == 'custom':
            custom_params = {
                'cashout_target': validate_float(request.args.get('cashout_target'), 2.0, 1.01, 1000, "cashout_target"),
                'bet_sequence': ','.join(validate_bet_sequence(request.args.get('bet_sequence'))),
                'max_bet': validate_float(request.args.get('max_bet'), 20, 1, 100000, "custom_max_bet"),
                'stop_loss': validate_float(request.args.get('stop_loss'), 50, 0, 1000000, "stop_loss"),
                'take_profit': validate_float(request.args.get('take_profit'), 200, 1, 1000000, "take_profit"),
                'progression_type': request.args.get('progression_type', 'loss')
            }

            # Validate progression type
            if custom_params['progression_type'] not in ['loss', 'win']:
                logger.warning(f"Invalid progression_type: {custom_params['progression_type']}, using 'loss'")
                custom_params['progression_type'] = 'loss'

        # Validate bankroll is sufficient for minimum bet
        if bankroll < min_bet:
            return jsonify({"error": f"Bankroll ({bankroll}) must be at least the minimum bet ({min_bet})"}), 400

        logger.info(f"Simulating {strategy} strategy for {rounds} rounds")

        result = simulate_strategy(
            strategy=strategy,
            rounds=rounds,
            bet=bet,
            bankroll=bankroll,
            target_profit=target_profit,
            percent_bet=percent_bet,
            realistic_conditions=realistic_conditions,
            min_bet=min_bet,
            max_bet=max_bet,
            network_delay=network_delay,
            error_simulation=error_simulation,
            custom_params=custom_params
        )

        if "error" in result:
            logger.error(f"Simulation error: {result['error']}")
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        logger.error(f"Unexpected error in simulate endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "aviator-simulator"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')