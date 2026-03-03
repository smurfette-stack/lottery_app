#!/usr/bin/env python3
"""Build updated Powerball HTML with new data format + search feature."""

import json

with open('powerball_data.json') as f:
    data = json.load(f)

total = len(data)
winners = sum(d['hasWinner'] for d in data)
avg_index = int(sum(d['comboIndex'] for d in data) / total)
win_rate = f"{(winners/total*100):.1f}%"

data_json = json.dumps(data, separators=(',', ':'))

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Powerball Winning Combo Index Over Time</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      min-height: 100vh;
      padding: 20px;
      color: #fff;
    }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    h1 {{
      text-align: center;
      margin-bottom: 10px;
      font-size: 2rem;
      background: linear-gradient(90deg, #f39c12, #e74c3c);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .subtitle {{
      text-align: center;
      color: #8892b0;
      margin-bottom: 30px;
      font-size: 0.95rem;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 20px;
    }}
    .stat-card {{
      background: rgba(255,255,255,0.05);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .stat-value {{ font-size: 2rem; font-weight: bold; color: #f39c12; }}
    .stat-label {{ color: #8892b0; font-size: 0.85rem; margin-top: 5px; }}

    /* Search section */
    .search-section {{
      background: rgba(255,255,255,0.05);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 20px;
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .search-section h2 {{
      font-size: 1.2rem;
      margin-bottom: 16px;
      color: #ccd6f6;
    }}
    .number-picker {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;
      align-items: flex-start;
    }}
    .picker-group {{ display: flex; flex-direction: column; gap: 6px; }}
    .picker-label {{ font-size: 0.75rem; color: #8892b0; text-transform: uppercase; letter-spacing: 0.05em; }}
    .ball-inputs {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .ball-input {{
      width: 54px;
      height: 54px;
      border-radius: 50%;
      border: 2px solid rgba(255,255,255,0.2);
      background: rgba(255,255,255,0.08);
      color: #fff;
      font-size: 1.1rem;
      font-weight: bold;
      text-align: center;
      outline: none;
      transition: border-color 0.2s, background 0.2s;
    }}
    .ball-input:focus {{ border-color: #3498db; background: rgba(52,152,219,0.15); }}
    .ball-input.powerball {{
      border-color: rgba(231,76,60,0.5);
      background: rgba(231,76,60,0.1);
    }}
    .ball-input.powerball:focus {{ border-color: #e74c3c; background: rgba(231,76,60,0.2); }}
    .ball-input.valid {{ border-color: #2ecc71; }}
    .ball-input.invalid {{ border-color: #e74c3c; }}
    .search-actions {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
    .btn {{
      padding: 10px 24px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 600;
      transition: all 0.2s;
    }}
    .btn-primary {{ background: linear-gradient(90deg, #f39c12, #e74c3c); color: #fff; }}
    .btn-primary:hover {{ opacity: 0.85; transform: translateY(-1px); }}
    .btn-secondary {{
      background: rgba(255,255,255,0.08);
      color: #ccd6f6;
      border: 1px solid rgba(255,255,255,0.15);
    }}
    .btn-secondary:hover {{ background: rgba(255,255,255,0.12); }}
    .search-hint {{ font-size: 0.8rem; color: #8892b0; }}

    /* Search results */
    .search-results {{
      margin-top: 16px;
      padding: 16px;
      background: rgba(0,0,0,0.2);
      border-radius: 10px;
      display: none;
    }}
    .search-results.visible {{ display: block; }}
    .result-match {{
      background: rgba(46,204,113,0.1);
      border: 1px solid rgba(46,204,113,0.4);
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 8px;
    }}
    .result-match.winner {{
      background: rgba(231,76,60,0.15);
      border-color: rgba(231,76,60,0.5);
    }}
    .result-no-match {{
      color: #8892b0;
      font-style: italic;
      padding: 8px 0;
    }}
    .result-count {{
      font-size: 0.85rem;
      color: #8892b0;
      margin-bottom: 10px;
    }}
    .match-balls {{
      display: flex;
      gap: 6px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .ball {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      font-weight: bold;
    }}
    .ball.white {{ background: #ccd6f6; color: #1a1a2e; }}
    .ball.red {{ background: #e74c3c; color: #fff; }}
    .match-info {{ margin-top: 6px; font-size: 0.82rem; color: #8892b0; }}
    .match-info .jackpot-badge {{
      display: inline-block;
      background: #e74c3c;
      color: #fff;
      font-size: 0.7rem;
      padding: 2px 7px;
      border-radius: 10px;
      margin-left: 6px;
      font-weight: bold;
      text-transform: uppercase;
    }}

    /* Chart */
    .chart-container {{
      background: rgba(255,255,255,0.05);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 20px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .legend-custom {{
      display: flex;
      justify-content: center;
      gap: 30px;
      margin-top: 15px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
      color: #ccd6f6;
    }}
    .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
    .legend-dot.winner {{ background: #e74c3c; box-shadow: 0 0 10px #e74c3c; }}
    .legend-dot.no-winner {{ background: #3498db; }}
    .info {{
      text-align: center;
      color: #8892b0;
      font-size: 0.85rem;
      margin-top: 15px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🎱 Powerball Winning Combo Index Analysis</h1>
    <p class="subtitle">Visualizing where winning combinations fall in the ~292M combination space (Oct 2015 – Present)</p>

    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">{total:,}</div>
        <div class="stat-label">Total Draws</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{winners}</div>
        <div class="stat-label">Jackpot Winners</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{avg_index:,}</div>
        <div class="stat-label">Avg Combo Index</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{win_rate}</div>
        <div class="stat-label">Win Rate</div>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <h2>🔍 Search Winning Numbers</h2>
      <div class="number-picker">
        <div class="picker-group">
          <span class="picker-label">White Balls (1–69)</span>
          <div class="ball-inputs">
            <input class="ball-input" id="w1" type="number" min="1" max="69" placeholder="–">
            <input class="ball-input" id="w2" type="number" min="1" max="69" placeholder="–">
            <input class="ball-input" id="w3" type="number" min="1" max="69" placeholder="–">
            <input class="ball-input" id="w4" type="number" min="1" max="69" placeholder="–">
            <input class="ball-input" id="w5" type="number" min="1" max="69" placeholder="–">
          </div>
        </div>
        <div class="picker-group">
          <span class="picker-label">Powerball (1–26)</span>
          <div class="ball-inputs">
            <input class="ball-input powerball" id="pb" type="number" min="1" max="26" placeholder="–">
          </div>
        </div>
      </div>
      <div class="search-actions">
        <button class="btn btn-primary" onclick="searchNumbers()">Search</button>
        <button class="btn btn-secondary" onclick="clearSearch()">Clear</button>
        <span class="search-hint">Enter some or all numbers — partial matches welcome!</span>
      </div>
      <div class="search-results" id="searchResults"></div>
    </div>

    <div class="chart-container">
      <canvas id="powerballChart"></canvas>
      <div class="legend-custom">
        <div class="legend-item">
          <div class="legend-dot no-winner"></div>
          <span>No Jackpot Winner</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot winner"></div>
          <span>Jackpot Winner</span>
        </div>
      </div>
    </div>

    <p class="info">
      Index range: 0 to 292,201,337 (all possible Powerball combinations)<br>
      Hover over points to see details. Winner draws are highlighted in red.
    </p>
  </div>

  <script>
    const data = {data_json};

    // --- Search ---
    function searchNumbers() {{
      const w = ['w1','w2','w3','w4','w5'].map(id => {{
        const v = parseInt(document.getElementById(id).value);
        return (!isNaN(v) && v >= 1 && v <= 69) ? v : null;
      }}).filter(v => v !== null);

      const pbVal = parseInt(document.getElementById('pb').value);
      const pb = (!isNaN(pbVal) && pbVal >= 1 && pbVal <= 26) ? pbVal : null;

      if (w.length === 0 && pb === null) {{
        showResults('<p class="result-no-match">Enter at least one number to search.</p>', 0);
        return;
      }}

      const matches = data.filter(draw => {{
        const wMatch = w.every(n => draw.numbers.includes(n));
        const pbMatch = pb === null || draw.powerball === pb;
        return wMatch && pbMatch;
      }});

      if (matches.length === 0) {{
        const query = [...w.map(n => `<span class="ball white" style="display:inline-flex;width:28px;height:28px;border-radius:50%;background:#ccd6f6;color:#1a1a2e;align-items:center;justify-content:center;font-size:.8rem;font-weight:bold">${{n}}</span>`), pb ? `<span class="ball red" style="display:inline-flex;width:28px;height:28px;border-radius:50%;background:#e74c3c;color:#fff;align-items:center;justify-content:center;font-size:.8rem;font-weight:bold">${{pb}}</span>` : ''].join(' ');
        showResults(`<p class="result-no-match">No draws found matching those numbers. These numbers have never come up together! 🤷</p>`, 0);
        return;
      }}

      const rows = matches.map(draw => {{
        const balls = draw.numbers.map(n => `<div class="ball white">${{n}}</div>`).join('');
        const pbBall = `<div class="ball red">${{draw.powerball}}</div>`;
        const badge = draw.hasWinner ? '<span class="jackpot-badge">Jackpot Winner!</span>' : '';
        return `
          <div class="result-match${{draw.hasWinner ? ' winner' : ''}}">
            <div class="match-balls">${{balls}}${{pbBall}}</div>
            <div class="match-info">
              📅 ${{draw.date}}
              ${{badge}}
              &nbsp;·&nbsp; Combo #${{draw.comboIndex.toLocaleString()}}
            </div>
          </div>`;
      }}).join('');

      showResults(rows, matches.length);
    }}

    function showResults(html, count) {{
      const el = document.getElementById('searchResults');
      const label = count === 0 ? '' : `<div class="result-count">${{count}} draw${{count !== 1 ? 's' : ''}} found</div>`;
      el.innerHTML = label + html;
      el.classList.add('visible');
    }}

    function clearSearch() {{
      ['w1','w2','w3','w4','w5','pb'].forEach(id => document.getElementById(id).value = '');
      const el = document.getElementById('searchResults');
      el.innerHTML = '';
      el.classList.remove('visible');
    }}

    // Allow Enter key to trigger search
    document.addEventListener('keydown', e => {{
      if (e.key === 'Enter' && document.activeElement?.classList.contains('ball-input')) searchNumbers();
    }});

    // --- Chart ---
    const ctx = document.getElementById('powerballChart').getContext('2d');
    new Chart(ctx, {{
      type: 'scatter',
      data: {{
        datasets: [
          {{
            label: 'No Jackpot Winner',
            data: data.filter(d => !d.hasWinner).map(d => ({{ x: d.date, y: d.comboIndex }})),
            backgroundColor: 'rgba(52, 152, 219, 0.6)',
            pointRadius: 3,
            pointHoverRadius: 6,
          }},
          {{
            label: 'Jackpot Winner',
            data: data.filter(d => d.hasWinner).map(d => ({{ x: d.date, y: d.comboIndex }})),
            backgroundColor: 'rgba(231, 76, 60, 0.9)',
            pointRadius: 6,
            pointHoverRadius: 9,
            pointStyle: 'star',
          }}
        ]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              title: ctx => {{
                const idx = ctx[0].dataIndex;
                const isWinner = ctx[0].dataset.label === 'Jackpot Winner';
                const match = data.find(d => d.date === ctx[0].raw.x && d.hasWinner === isWinner);
                return match ? match.date : ctx[0].raw.x;
              }},
              label: ctx => {{
                const isWinner = ctx.dataset.label === 'Jackpot Winner';
                const match = data.find(d => d.date === ctx.raw.x && d.hasWinner === isWinner);
                if (!match) return '';
                const nums = match.numbers.join(', ');
                const pct = ((match.comboIndex / 292201338) * 100).toFixed(2);
                return [
                  `Numbers: ${{nums}} | PB: ${{match.powerball}}`,
                  `Combo Index: ${{match.comboIndex.toLocaleString()}}`,
                  `Position: ${{pct}}% through combo space`,
                  isWinner ? '🏆 JACKPOT WINNER' : ''
                ].filter(Boolean);
              }}
            }}
          }}
        }},
        scales: {{
          x: {{
            type: 'time',
            time: {{ unit: 'month', displayFormats: {{ month: 'MMM yyyy' }} }},
            grid: {{ color: 'rgba(255,255,255,0.05)' }},
            ticks: {{ color: '#8892b0' }},
            title: {{ display: true, text: 'Draw Date', color: '#8892b0' }}
          }},
          y: {{
            min: 0,
            max: 292201338,
            grid: {{ color: 'rgba(255,255,255,0.05)' }},
            ticks: {{
              color: '#8892b0',
              callback: v => (v / 1e6).toFixed(0) + 'M'
            }},
            title: {{ display: true, text: 'Combination Index', color: '#8892b0' }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>'''

with open('index.html', 'w') as f:
    f.write(html)

print(f"Built index.html ({len(html):,} bytes)")
print(f"Data: {total} draws, {winners} jackpot winners")
