// frontend/pages/index.js

import { useState, useEffect } from "react";
import { Line, Bar, Radar } from "react-chartjs-2";
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

function computeStats(history, startingBankroll = 100) {
  let maxDrawdown = 0;
  let peak = history[0];
  let winStreak = 0;
  let lossStreak = 0;
  let maxWinStreak = 0;
  let maxLossStreak = 0;
  let wins = 0;
  let total = history.length;

  for (let i = 1; i < history.length; i++) {
    if (history[i] > peak) peak = history[i];
    const drawdown = (peak - history[i]) / peak;
    if (drawdown > maxDrawdown) maxDrawdown = drawdown;

    if (history[i] > history[i - 1]) {
      winStreak++;
      wins++;
      lossStreak = 0;
    } else if (history[i] < history[i - 1]) {
      lossStreak++;
      winStreak = 0;
    }
    if (winStreak > maxWinStreak) maxWinStreak = winStreak;
    if (lossStreak > maxLossStreak) maxLossStreak = lossStreak;
  }

  const avg = history.reduce((a, b) => a + b, 0) / total;
  const stdDev = Math.sqrt(history.map(x => Math.pow(x - avg, 2)).reduce((a, b) => a + b, 0) / total);
  const upperBand = history.map(() => avg + 2 * stdDev);
  const lowerBand = history.map(() => avg - 2 * stdDev);
  const finalBalance = history[history.length - 1];
  const roi = ((finalBalance - startingBankroll) / startingBankroll) * 100;
  const avgReturnPerRound = (finalBalance - startingBankroll) / total;

  return {
    maxDrawdown,
    maxWinStreak,
    maxLossStreak,
    upperBand,
    lowerBand,
    winRate: (wins / total) * 100,
    avgReturnPerRound,
    roi,
    finalBalance
  };
}

function downloadCSV(rows, fileName = "simulation_history.csv") {
  const header = Object.keys(rows[0]).join(",");
  const csv = [header, ...rows.map(row => Object.values(row).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
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
  const [showBands, setShowBands] = useState(true);
  const [historyLog, setHistoryLog] = useState([]);
  const [filterStrategy, setFilterStrategy] = useState("");
  const [minProfit, setMinProfit] = useState("");
  const [highlightedEntry, setHighlightedEntry] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("aviator_history");
    if (stored) setHistoryLog(JSON.parse(stored));
  }, []);

  useEffect(() => {
    localStorage.setItem("aviator_history", JSON.stringify(historyLog));
  }, [historyLog]);

  useEffect(() => {
    const stored = localStorage.getItem("aviator_history");
    if (stored) {
      const parsed = JSON.parse(stored);
      setHistoryLog(parsed);
      if (parsed.length > 0) {
        const best = parsed.reduce((prev, curr) =>
          curr.json.final_balance > prev.json.final_balance ? curr : prev
        );
        setHighlightedEntry(best);
      }
    }
  }, []);

  const comparisonData = () => {
    const [first, second] = historyLog.slice(0, 2);
    if (!first || !second) return null;
    const stat1 = computeStats(first.json.history, first.bankroll);
    const stat2 = computeStats(second.json.history, second.bankroll);
    return {
      labels: ["Win Rate", "Avg Return", "ROI", "Max Drawdown", "Max Win Streak", "Max Loss Streak"],
      datasets: [
        {
          label: `${first.strategy}`,
          data: [
            stat1.winRate,
            stat1.avgReturnPerRound,
            stat1.roi,
            stat1.maxDrawdown * 100,
            stat1.maxWinStreak,
            stat1.maxLossStreak
          ],
          backgroundColor: "rgba(54, 162, 235, 0.5)"
        },
        {
          label: `${second.strategy}`,
          data: [
            stat2.winRate,
            stat2.avgReturnPerRound,
            stat2.roi,
            stat2.maxDrawdown * 100,
            stat2.maxWinStreak,
            stat2.maxLossStreak
          ],
          backgroundColor: "rgba(255, 99, 132, 0.5)"
        }
      ]
    };
  };

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
        const newEntry = { strategy, bet, rounds, bankroll, targetProfit, percentBet, json, timestamp: new Date().toISOString() };
        setHistoryLog([newEntry, ...historyLog]);
        setError(null);
      }
    } catch (err) {
      setError("Failed to connect to backend.");
      setData(null);
    }
  };

  const filteredHistory = historyLog.filter(entry => {
    const profitOk = minProfit === "" || entry.json.final_balance >= parseFloat(minProfit);
    const strategyOk = filterStrategy === "" || entry.strategy === filterStrategy;
    return profitOk && strategyOk;
  });

  const handleExport = () => {
    const rows = filteredHistory.map(entry => ({
      timestamp: entry.timestamp,
      strategy: entry.strategy,
      bet: entry.bet,
      rounds: entry.rounds,
      bankroll: entry.bankroll,
      targetProfit: entry.targetProfit,
      percentBet: entry.percentBet,
      finalBalance: entry.json.final_balance,
      ruin: entry.json.ruin_occurred
    }));
    downloadCSV(rows);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Aviator Strategy Simulator</h1>

      {/* Highlighted Best Performing Run */}
      {highlightedEntry && (
        <div style={{ background: "#e0ffe0", padding: "1rem", marginBottom: "1rem" }}>
          <strong>🏆 Best Run:</strong> {highlightedEntry.strategy} - R{highlightedEntry.json.final_balance.toFixed(2)}
        </div>
      )}

      {/* Radar or Bar Chart Comparison */}
      {historyLog.length >= 2 && (
        <div style={{ marginBottom: "2rem" }}>
          <h3>📊 Strategy Comparison</h3>
          <Radar data={comparisonData()} />
        </div>
      )}

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

      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            type="checkbox"
            checked={showBands}
            onChange={(e) => setShowBands(e.target.checked)}
          /> Show Confidence Bands
        </label>
      </div>

      <button onClick={simulate}>Simulate</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {data && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Final Balance: R{data.final_balance}</h3>
          {data.max_loss_streak !== null && (
            <p>Max Loss Streak: {data.max_loss_streak}</p>
          )}
          {data.ruin_occurred !== null && (
            <p>Risk of Ruin: <strong>{data.ruin_occurred ? "YES" : "NO"}</strong></p>
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
                showBands && stats && {
                  label: "Upper Band (95%)",
                  data: stats.upperBand,
                  fill: false,
                  borderColor: "rgba(0, 0, 255, 0.3)",
                  borderDash: [5, 5],
                },
                showBands && stats && {
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

      {historyLog.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Simulation History</h2>
          <div style={{ marginBottom: "1rem" }}>
            <label>Filter Strategy:&nbsp;</label>
            <select value={filterStrategy} onChange={(e) => setFilterStrategy(e.target.value)}>
              <option value="">All</option>
              <option value="early">Early Cashout</option>
              <option value="mid">Mid-Risk</option>
              <option value="high">High-Risk</option>
              <option value="dual">Dual Bet</option>
              <option value="martingale">Martingale</option>
              <option value="paroli">Paroli</option>
              <option value="fixed_percent">Fixed % of Bankroll</option>
              <option value="target_profit">Target Profit Goal</option>
            </select>
            &nbsp;&nbsp;
            <label>Min Final Balance:&nbsp;</label>
            <input type="number" value={minProfit} onChange={(e) => setMinProfit(e.target.value)} />
            &nbsp;&nbsp;
            <button onClick={handleExport}>Export CSV</button>
          </div>
          <ul>
            {filteredHistory.map((entry, index) => (
              <li key={index}>
                [{entry.timestamp}] <strong>{entry.strategy}</strong> - Final Balance: R{entry.json.final_balance.toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
