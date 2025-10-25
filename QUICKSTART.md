# Quick Start Guide

Get up and running with the Portfolio Backtesting Dashboard in 5 minutes!

## 🚀 Installation (2 minutes)

```bash
# 1. Navigate to project directory
cd "improved backtesting"

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

## ▶️ Running (30 seconds)

```bash
python dashboard.py
```

Then open in your browser: **http://127.0.0.1:8050**

## 🎯 Your First Backtest (2 minutes)

### Option 1: Manual Entry

1. **Add Apple stock**:
   - Enter: `AAPL`
   - Click "**+ Add Holding**"
   - Set weight to `50%`

2. **Add Microsoft**:
   - Enter: `MSFT`
   - Click "**+ Add Holding**"
   - Set weight to `50%`

3. **Run backtest**:
   - Click "**Run Backtest**"
   - View results!

### Option 2: CSV Import

1. **Download template**:
   - Click "**📋 Sample CSV**"
   - Save the file

2. **Import**:
   - Click "**📁 Import CSV**"
   - Select the template file
   - Backtest ready!

## 💡 Tips

### Quick Examples

**Try different assets**:
```
AAPL  → Apple stock
SPY   → S&P 500 ETF
GC=F  → Gold futures
^GSPC → S&P 500 Index
```

**View log scale**:
- Click "**Toggle Log Scale**" after running backtest
- Great for portfolios with large gains/losses

**Export everything**:
- Click "**💾 Export CSV**" to save portfolio
- Click "**📊 Export Full Report**" to save all data

## ❓ Common Questions

**Q: What if a ticker doesn't work?**  
A: Check it on [Yahoo Finance](https://finance.yahoo.com/) first

**Q: Why does my portfolio show a warning?**  
A: Weights must sum to exactly 100%

**Q: How far back can I backtest?**  
A: As far as the youngest ticker has data

**Q: Can I test crypto?**  
A: Yes! Use format like `BTC-USD`, `ETH-USD`

## 📚 Next Steps

- Read the full [README.md](README.md)
- Check [EXPORT_FORMAT.md](EXPORT_FORMAT.md) for export details
- Explore [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for technical details

## 🆘 Troubleshooting

**Dashboard won't start?**
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Import errors?**
- Make sure virtual environment is activated
- Check you're in the right directory
- Try: `pip list` to see installed packages

**Still stuck?**
- Check the full README.md
- Review error messages in terminal
- Verify internet connection (needed for data)

---

**Ready to backtest? Let's go! 📈**

