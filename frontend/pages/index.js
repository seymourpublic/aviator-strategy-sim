// frontend/pages/index.js

import { useState, useEffect } from "react";
import { Line, Bar, Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  RadialLinearScale,
  LinearScale,
  PointElement,
  BarElement,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  LineElement, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  BarElement,
  RadialLinearScale,
  Tooltip, 
  Legend, 
  Filler
);

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

// Color palette for strategies
const strategyColors = {
  early: { border: "rgba(54, 162, 235, 1)", bg: "rgba(54, 162, 235, 0.2)" },
  mid: { border: "rgba(255, 99, 132, 1)", bg: "rgba(255, 99, 132, 0.2)" },
  high: { border: "rgba(255, 206, 86, 1)", bg: "rgba(255, 206, 86, 0.2)" },
  dual: { border: "rgba(75, 192, 192, 1)", bg: "rgba(75, 192, 192, 0.2)" },
  martingale: { border: "rgba(153, 102, 255, 1)", bg: "rgba(153, 102, 255, 0.2)" },
  paroli: { border: "rgba(255, 159, 64, 1)", bg: "rgba(255, 159, 64, 0.2)" },
  fixed_percent: { border: "rgba(29, 209, 161, 1)", bg: "rgba(29, 209, 161, 0.2)" },
  target_profit: { border: "rgba(238, 90, 36, 1)", bg: "rgba(238, 90, 36, 0.2)" }
};

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
  
  // New state for strategy comparison
  const [compareMode, setCompareMode] = useState(false);
  const [selectedStrategies, setSelectedStrategies] = useState([]);
  const [overlayChart, setOverlayChart] = useState(true);
  const [comparisonResults, setComparisonResults] = useState([]);
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonParameters, setComparisonParameters] = useState({
    rounds: 1000,
    bankroll: 100,
    bet: 1.0,
  });

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

  // Multi-strategy comparison data for overlay chart
  const multiStrategyComparisonData = () => {
    if (!comparisonResults || comparisonResults.length === 0) return null;
    
    return {
      labels: Array.from({ length: comparisonParameters.rounds }, (_, i) => i),
      datasets: comparisonResults.map((result, index) => ({
        label: result.strategy,
        data: result.json.history,
        fill: false,
        borderColor: strategyColors[result.strategy]?.border || `hsl(${index * 45}, 70%, 50%)`,
        backgroundColor: strategyColors[result.strategy]?.bg || `hsla(${index * 45}, 70%, 50%, 0.2)`,
        tension: 0.1,
      }))
    };
  };

  // Performance metrics comparison for bar chart
  const performanceComparisonData = () => {
    if (!comparisonResults || comparisonResults.length === 0) return null;
    
    const metrics = ["Final Balance", "Win Rate (%)", "ROI (%)", "Max Drawdown (%)"];
    
    const datasets = metrics.map((metric, metricIndex) => {
      return {
        label: metric,
        data: comparisonResults.map(result => {
          const stats = computeStats(result.json.history, result.bankroll);
          switch(metricIndex) {
            case 0: return result.json.final_balance;
            case 1: return stats.winRate;
            case 2: return stats.roi;
            case 3: return stats.maxDrawdown * 100;
            default: return 0;
          }
        }),
        backgroundColor: `hsla(${metricIndex * 60}, 70%, 50%, 0.7)`,
      };
    });
    
    return {
      labels: comparisonResults.map(result => result.strategy),
      datasets
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

  // Run multiple strategy simulations
  const compareStrategies = async () => {
    if (selectedStrategies.length === 0) {
      setError("Please select at least one strategy to compare");
      return;
    }
    
    setIsComparing(true);
    setError(null);
    const results = [];
    
    try {
      for (const strat of selectedStrategies) {
        const params = new URLSearchParams({
          strategy: strat,
          bet: comparisonParameters.bet,
          rounds: comparisonParameters.rounds,
          bankroll: comparisonParameters.bankroll,
          target_profit: targetProfit,
          percent_bet: percentBet
        });

        const res = await fetch(`http://localhost:8000/simulate?${params.toString()}`);
        const json = await res.json();

        if (json.error) {
          setError(`Error with ${strat}: ${json.error}`);
        } else {
          results.push({
            strategy: strat,
            bankroll: comparisonParameters.bankroll,
            bet: comparisonParameters.bet,
            rounds: comparisonParameters.rounds,
            json
          });
        }
      }
      
      if (results.length > 0) {
        setComparisonResults(results);
        // Also add these results to history log
        const newEntries = results.map(result => ({
          strategy: result.strategy,
          bet: result.bet,
          rounds: result.rounds,
          bankroll: result.bankroll,
          targetProfit,
          percentBet,
          json: result.json,
          timestamp: new Date().toISOString()
        }));
        setHistoryLog([...newEntries, ...historyLog]);
      }
    } catch (err) {
      setError("Failed to connect to backend.");
    } finally {
      setIsComparing(false);
    }
  };

  const handleStrategySelection = (strategy) => {
    setSelectedStrategies(prev => {
      if (prev.includes(strategy)) {
        return prev.filter(s => s !== strategy);
      } else {
        return [...prev, strategy];
      }
    });
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

  const handleExportComparison = () => {
    if (comparisonResults.length === 0) return;
    
    const rows = comparisonResults.map(result => {
      const stats = computeStats(result.json.history, result.bankroll);
      return {
        strategy: result.strategy,
        finalBalance: result.json.final_balance,
        rounds: result.rounds,
        bankroll: result.bankroll,
        winRate: stats.winRate.toFixed(2),
        roi: stats.roi.toFixed(2),
        maxDrawdown: (stats.maxDrawdown * 100).toFixed(2),
        maxWinStreak: stats.maxWinStreak,
        maxLossStreak: stats.maxLossStreak,
        ruin: result.json.ruin_occurred || false
      };
    });
    
    downloadCSV(rows, "strategy_comparison.csv");
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
      
      {/* Tabs for Single/Compare mode */}
      <div style={{ marginBottom: "1.5rem" }}>
        <button 
          onClick={() => setCompareMode(false)}
          style={{ 
            padding: "0.5rem 1rem", 
            fontWeight: !compareMode ? "bold" : "normal",
            background: !compareMode ? "#e0f7ff" : "#f0f0f0"
          }}
        >
          Single Strategy
        </button>
        <button 
          onClick={() => setCompareMode(true)}
          style={{ 
            padding: "0.5rem 1rem", 
            fontWeight: compareMode ? "bold" : "normal",
            background: compareMode ? "#e0f7ff" : "#f0f0f0"
          }}
        >
          🔍 Compare Strategies
        </button>
      </div>

      {!compareMode ? (
        // Single Strategy Mode
        <>
          {/* Radar or Bar Chart Comparison */}
          {historyLog.length >= 2 && (
            <div style={{ marginBottom: "2rem" }}>
              <h3>📊 Strategy Comparison</h3>
              <Radar
                data={comparisonData()}
                options={{
                  scales: {
                    r: {
                      beginAtZero: true,
                      pointLabels: {
                        font: { size: 14 },
                      },
                      ticks: {
                        backdropColor: 'transparent',
                        precision: 0,
                      },
                    }
                  }
                }}
              />
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
              <h3>Final Balance: R{data.final_balance.toFixed(2)}</h3>
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
        </>
      ) : (
        // Multi-Strategy Comparison Mode
        <div>
          <h2>🔍 Strategy Comparison Tool</h2>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", marginBottom: "1.5rem" }}>
            <div style={{ flex: "1", minWidth: "300px" }}>
              <h3>Comparison Parameters</h3>
              <div style={{ marginBottom: "1rem" }}>
                <label>Rounds:&nbsp;</label>
                <input
                  type="number"
                  value={comparisonParameters.rounds}
                  onChange={(e) => setComparisonParameters({...comparisonParameters, rounds: parseInt(e.target.value)})}
                />
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label>Starting Bankroll:&nbsp;</label>
                <input
                  type="number"
                  value={comparisonParameters.bankroll}
                  onChange={(e) => setComparisonParameters({...comparisonParameters, bankroll: parseFloat(e.target.value)})}
                />
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label>Base Bet:&nbsp;</label>
                <input
                  type="number"
                  value={comparisonParameters.bet}
                  onChange={(e) => setComparisonParameters({...comparisonParameters, bet: parseFloat(e.target.value)})}
                  step="0.1"
                />
              </div>
            </div>
            
            <div style={{ flex: "1", minWidth: "300px" }}>
              <h3>Select Strategies to Compare</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {["early", "mid", "high", "dual", "martingale", "paroli", "fixed_percent", "target_profit"].map(strat => (
                  <label key={strat} style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    padding: "6px 12px",
                    backgroundColor: selectedStrategies.includes(strat) ? strategyColors[strat]?.bg : "transparent",
                    borderLeft: `4px solid ${selectedStrategies.includes(strat) ? strategyColors[strat]?.border : "transparent"}`,
                    borderRadius: "4px"
                  }}>
                    <input
                      type="checkbox"
                      checked={selectedStrategies.includes(strat)}
                      onChange={() => handleStrategySelection(strat)}
                    />
                    <span style={{ marginLeft: "8px" }}>
                      {strat === "early" ? "Early Cashout" :
                        strat === "mid" ? "Mid-Risk" :
                        strat === "high" ? "High-Risk" :
                        strat === "dual" ? "Dual Bet" :
                        strat === "martingale" ? "Martingale" :
                        strat === "paroli" ? "Paroli" :
                        strat === "fixed_percent" ? "Fixed % of Bankroll" :
                        "Target Profit Goal"}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label>
              <input
                type="checkbox"
                checked={overlayChart}
                onChange={(e) => setOverlayChart(e.target.checked)}
              /> Overlay on Same Chart
            </label>
          </div>

          <button 
            onClick={compareStrategies} 
            disabled={isComparing || selectedStrategies.length === 0}
            style={{ 
              padding: "8px 16px", 
              backgroundColor: "#4CAF50", 
              color: "white", 
              border: "none", 
              borderRadius: "4px",
              opacity: isComparing || selectedStrategies.length === 0 ? 0.7 : 1
            }}
          >
            {isComparing ? "Running Simulations..." : "Compare Strategies"}
          </button>

          {error && <p style={{ color: "red" }}>{error}</p>}

          {comparisonResults.length > 0 && (
            <div style={{ marginTop: "2rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3>Comparison Results</h3>
                <button onClick={handleExportComparison}>Export Comparison</button>
              </div>
              
              <div style={{ marginBottom: "2rem" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ backgroundColor: "#f3f3f3" }}>
                      <th style={{ padding: "10px", textAlign: "left", borderBottom: "2px solid #ddd" }}>Strategy</th>
                      <th style={{ padding: "10px", textAlign: "right", borderBottom: "2px solid #ddd" }}>Final Balance</th>
                      <th style={{ padding: "10px", textAlign: "right", borderBottom: "2px solid #ddd" }}>Win Rate</th>
                      <th style={{ padding: "10px", textAlign: "right", borderBottom: "2px solid #ddd" }}>ROI</th>
                      <th style={{ padding: "10px", textAlign: "right", borderBottom: "2px solid #ddd" }}>Max Drawdown</th>
                      <th style={{ padding: "10px", textAlign: "right", borderBottom: "2px solid #ddd" }}>Risk of Ruin</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonResults.map((result, index) => {
                      const stats = computeStats(result.json.history, result.bankroll);
                      return (
                        <tr key={index} style={{ backgroundColor: index % 2 === 0 ? "#fff" : "#f9f9f9" }}>
                          <td style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>
                            <div style={{ display: "flex", alignItems: "center" }}>
                              <div style={{ width: "12px", height: "12px", borderRadius: "50%", backgroundColor: strategyColors[result.strategy]?.border, marginRight: "8px" }}></div>
                              {result.strategy}
                            </div>
                          </td>
                          <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #ddd", fontWeight: "bold" }}>
                            R{result.json.final_balance.toFixed(2)}
                          </td>
                          <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #ddd" }}>
                            {stats.winRate.toFixed(2)}%
                          </td>
                          <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #ddd" }}>
                            {stats.roi.toFixed(2)}%
                          </td>
                          <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #ddd" }}>
                            {(stats.maxDrawdown * 100).toFixed(2)}%
                          </td>
                          <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #ddd" }}>
                            {result.json.ruin_occurred ? "YES" : "NO"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              {/* Chart section */}
              <div style={{ marginBottom: "2rem" }}>
                <h3>Balance Over Time Comparison</h3>
                <Line
                  data={multiStrategyComparisonData()}
                  options={{
                    responsive: true,
                    scales: {
                      y: {
                        beginAtZero: false,
                      }
                    }
                  }}
                />
              </div>
              
              <div style={{ marginBottom: "2rem" }}>
                <h3>Performance Metrics Comparison</h3>
                <Bar
                  data={performanceComparisonData()}
                  options={{
                    responsive: true,
                    scales: {
                      x: {
                        stacked: false,
                      },
                      y: {
                        stacked: false,
                        beginAtZero: true
                      }
                    }
                  }}
                />
              </div>
            </div>
          )}
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