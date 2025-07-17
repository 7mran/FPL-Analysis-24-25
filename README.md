# 🏆 Fantasy Premier League Analysis Tool

A comprehensive command-line tool for analyzing Fantasy Premier League (FPL) data, providing insights into player performance, form analysis, and value for money calculations.

## 🚀 Features

### 🔍 Player Rankings & Lists
- **Top Players by Total Points** — Season-long point leaders
- **Top Players by Pick Rate** — Most popular players among managers
- **Top Players by Value for Money** — Best points per million ratio
- **Players by Position** — Filter and analyze by specific positions
- **Alphabetical & Team Sorting** — Organized player listings

### ⚡ Form & Performance Analysis
- **Recent Form Analysis** — Track player performance over recent gameweeks
- **Historical Performance** — Points up to specific gameweeks
- **Detailed Form Analysis** — In-depth performance breakdowns
- **Multi-Player Form Comparison** — Visual comparison of multiple players

### 📈 Individual Player Analysis
- **Full Gameweek History** — Complete season performance record
- **Specific Gameweek Stats** — Detailed stats for any gameweek
- **Points Visualization** — Interactive charts showing point trends
- **Price Tracking** — Monitor player price changes over time
- **Head-to-Head Comparisons** — Compare two players side by side

### 🎯 Advanced Analysis
- **Custom Date Range Analysis** — Analyze performance over specific periods
- **Custom Period Comparisons** — Compare players over defined timeframes
- **Multi-Player Form Charts** — Visual comparison of up to 6 players

## 🛠 Installation

### ✅ Prerequisites
- Python 3.7 or higher
- pip package manager

### ✅ Required Dependencies
```bash
pip install requests pandas tabulate matplotlib numpy
```

### ✅ Quick Install
```bash
# Clone the repository
git clone https://github.com/yourusername/fpl-analysis-tool.git
cd fpl-analysis-tool

# Install dependencies
pip install -r requirements.txt

# Run the application
python fpl_analysis.py
```

## ⚡ Usage

### ✅ Getting Started
1. Run the application:
   ```bash
   python fpl_analysis.py
   ```
2. The tool automatically fetches the latest FPL data from the official API.
3. Navigate through the menu options using numbers (0-18).

### ✅ Menu Structure

#### 🔍 PLAYER RANKINGS & LISTS
1. Top players by total points
2. Top players by pick rate
3. Top players by value for money
4. Players by position
5. All players (sorted alphabetically)
6. All players (sorted by team)

#### ⚡ FORM & PERFORMANCE ANALYSIS
7. Top players by recent form
8. Top players up to specific gameweek
9. Player form analysis (detailed)
10. Compare multiple players' form

#### 📈 INDIVIDUAL PLAYER ANALYSIS
11. Player's full gameweek history
12. Player's specific gameweek stats
13. Player points chart
14. Player price chart
15. Compare two players' points

#### 🎯 ADVANCED ANALYSIS
16. Custom form analysis (date range)
17. Custom period comparison
18. Multi-player form comparison

#### ❌ EXIT
0. Exit application

## 🔍 Example Usage

### Finding Top Value Players
```
Select option: 3
How many top players to show: 10
Enter position (goalkeeper/defender/midfielder/forward) or press Enter for all: midfielder
Minimum points threshold (default 50): 75
```

### Analyzing Player Form
```
Select option: 9
Enter player ID: 123
Number of recent gameweeks (default 5): 8
```

### Comparing Players
```
Select option: 15
Enter first player ID: 123
Enter second player ID: 456
```

## 📊 Data Source

- **API**: Official Fantasy Premier League API
- **Data Updates**: Real-time data from the official FPL servers
- **Coverage**: All current season data including player stats, prices, and gameweek history

## 📈 Key Metrics Explained

### Value for Money
- **Calculation**: Total Points ÷ Cost (in millions)
- **Purpose**: Identify players providing the best return on investment

### Form Analysis
- Recent form, custom periods, and trend indicators for performance analysis.

### Pick Rate
- Percentage of FPL managers who own the player — useful for identifying differential picks.

## ⚙️ Technical Details

- **Language**: Python 3.7+
- **API Integration**: RESTful API calls to FPL endpoints
- **Data Processing**: Pandas
- **Visualization**: Matplotlib
- **Interface**: Command-line with tabulated output

### ✅ Error Handling
- Graceful handling of network/API failures
- Input validation
- Clean exit on keyboard interrupts

### ✅ Performance
- Efficient data loading (single API call for season data)
- Caching to minimize redundant requests
- Optimized memory management

## 🤝 Contributing

We welcome contributions!

### How to contribute:

```bash
# Fork the repository
git checkout -b feature/amazing-feature

# Make your changes
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature
```

Open a Pull Request and describe your changes.

### ✅ Areas for Contribution
- Additional analysis features
- Performance optimizations
- UI/UX improvements
- Documentation enhancements
- Bug fixes and testing

## 🗺️ Roadmap

- [ ] Web interface version
- [ ] Export functionality (CSV, PDF)
- [ ] Historical season data
- [ ] Team analysis features
- [ ] Transfer suggestions
- [ ] Fixture difficulty integration

## 📌 Version History

- **v1.0**: Initial release with core analysis features
- **v1.1**: Added form comparison charts
- **v1.2**: Enhanced error handling and user experience

## 🛠 Troubleshooting

| Issue | Solution |
|-------|----------|
| Error loading data | Check internet connection & FPL API |
| Player ID not found | Ensure valid and active player ID |
| Chart display issues | Ensure matplotlib is installed |

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.

## 🙌 Acknowledgments

- Fantasy Premier League for providing the official API
- Python Community for excellent data analysis libraries
- Contributors who help improve this tool

## ⚠️ Disclaimer

This tool is for educational and analytical purposes only.
It is not affiliated with the official Fantasy Premier League game or the Premier League.

**Author**: Imran Ahmed Kamal  
**Data Source**: Fantasy Premier League API  
**Last Updated**: July 2025
