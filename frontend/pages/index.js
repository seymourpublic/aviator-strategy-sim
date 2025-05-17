// frontend/pages/index.js

import { useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, Filler);

function computeStats(history) {
  let maxDrawdown = 0;
  let peak = history[0];
  let drawdowns = [];
  let winStreak = 0;
  let lossStreak = 0;
  let maxWinStreak = 0;
  let maxLossStreak = 0;

  for (let i = 1; i < history.length; i++) {
    if (history[i] > peak) peak = history[i];
    const drawdown = (peak - history[i]) / peak;
    drawdowns.push(drawdown);
    if (drawdown > maxDrawdown) maxDrawdown = drawdown;

    if (history[i] > history[i - 1]) {
      winStreak++;
      lossStreak = 0;
    } else if (history[i] < history[i - 1]) {
      lossStreak++;
      winStreak = 0;
    }
    if (winStreak > maxWinStreak) maxWinStreak = winStreak;
    if (lossStreak > maxLossStreak) maxLossStreak = lossStreak;
  }

  // Probability bands (simplified)
  const avg = history.reduce((a, b) => a + b, 0) / history.length;
  const stdDev = Math.sqrt(history.map(x => Math.pow(x - avg, 2)).reduce((a, b) => a + b, 0) / history.length);
  const upperBand = history.map(() => avg + 2 * stdDev);
  const lowerBand = history.map(() => avg - 2 * stdDev);

  return { maxDrawdown, maxWinStreak, maxLossStreak, upperBand, lowerBand };
}

export default function Home() {
  const [strategy, setStrategy] = useState("early");
  const [bet, setBet] = useState(1.0);
  const [rounds, setRounds] = useState(1000);
  const [bankroll, setBankroll] = useState(100);
  const [targetProfit, setTargetProfit] = useState(50);
  const [percentBet, setPercentBet] = useState(5);
  const [data, setData] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  const simulate = async () => {
    try {
      const params = new URLSearchParams({
        strategy,
        bet,
        rounds,
        bankroll,
        target_profit: targetProfit,
        percent_bet: percentBet
      });

      const res = await fetch(`http://localhost:8000/simulate?${params.toString()}`);
      const json = await res.json();

      if (json.error) {
        setError(json.error);
        setData(null);
      } else {
        setData(json);
        setStats(computeStats(json.history));
        setError(null);
      }
    } catch (err) {
      setError("Failed to connect to backend.");
      setData(null);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Aviator Strategy Simulator</h1>

      <div style={{ marginBottom: "1rem" }}>
        <label>Strategy:&nbsp;</label>
        <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
          <option value="early">Early Cashout</option>
          <option value="mid">Mid-Risk</option>
          <option value="high">High-Risk</option>
          <option value="dual">Dual Bet</option>
          <option value="martingale">Martingale</option>
          <option value="paroli">Paroli</option>
          <option value="fixed_percent">Fixed % of Bankroll</option>
          <option value="target_profit">Target Profit Goal</option>
        </select>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Base Bet:&nbsp;</label>
        <input
          type="number"
          value={bet}
          onChange={(e) => setBet(e.target.value)}
          step="0.1"
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Rounds:&nbsp;</label>
        <input
          type="number"
          value={rounds}
          onChange={(e) => setRounds(e.target.value)}
        />
      </div>

      {(strategy === "martingale" || strategy === "paroli" || strategy === "fixed_percent" || strategy === "target_profit") && (
        <div style={{ marginBottom: "1rem" }}>
          <label>Starting Bankroll:&nbsp;</label>
          <input
            type="number"
            value={bankroll}
            onChange={(e) => setBankroll(e.target.value)}
          />
        </div>
      )}

      {strategy === "target_profit" && (
        <div style={{ marginBottom: "1rem" }}>
          <label>Target Profit:&nbsp;</label>
          <input
            type="number"
            value={targetProfit}
            onChange={(e) => setTargetProfit(e.target.value)}
          />
        </div>
      )}

      {strategy === "fixed_percent" && (
        <div style={{ marginBottom: "1rem" }}>
          <label>Percent of Bankroll per Bet:&nbsp;</label>
          <input
            type="number"
            value={percentBet}
            onChange={(e) => setPercentBet(e.target.value)}
            step="1"
          />
        </div>
      )}

      <button onClick={simulate}>Simulate</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {data && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Final Balance: ${data.final_balance}</h3>
          {data.max_loss_streak !== null && (
            <p>Max Loss Streak: {data.max_loss_streak}</p>
          )}
          {data.ruin_occurred !== null && (
            <p>
              Risk of Ruin: <strong>{data.ruin_occurred ? "YES" : "NO"}</strong>
            </p>
          )}
          {stats && (
            <>
              <p>📉 Max Drawdown: {(stats.maxDrawdown * 100).toFixed(2)}%</p>
              <p>📊 Max Win Streak: {stats.maxWinStreak}</p>
              <p>📊 Max Loss Streak: {stats.maxLossStreak}</p>
            </>
          )}

          <Line
            data={{
              labels: data.history.map((_, i) => i),
              datasets: [
                {
                  label: "Balance Over Time",
                  data: data.history,
                  fill: false,
                  borderColor: "green",
                  tension: 0.1,
                },
                stats && {
                  label: "Upper Band (95%)",
                  data: stats.upperBand,
                  fill: false,
                  borderColor: "rgba(0, 0, 255, 0.3)",
                  borderDash: [5, 5],
                },
                stats && {
                  label: "Lower Band (95%)",
                  data: stats.lowerBand,
                  fill: false,
                  borderColor: "rgba(255, 0, 0, 0.3)",
                  borderDash: [5, 5],
                }
              ].filter(Boolean),
            }}
          />
        </div>
      )}
    </div>
  );
}
