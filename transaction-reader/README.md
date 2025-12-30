# 💳 Transaction Reader

An AI-powered Gmail purchase analyzer that automatically extracts and categorizes your transactions from email receipts. Uses Claude AI to intelligently detect purchases, categorize spending, and provide actionable insights.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.50+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 📧 **Multiple Gmail Account Support** - Analyze transactions from multiple email accounts
- 🤖 **AI-Powered Analysis** - Uses Claude AI to intelligently extract transaction details
- 📊 **Interactive Dashboard** - Beautiful visualizations of spending patterns
- 🏷️ **Smart Categorization** - Automatically categorizes purchases (groceries, dining, entertainment, etc.)
- 💡 **Spending Insights** - Get actionable suggestions to optimize your spending
- 📈 **Trend Analysis** - View spending over time with interactive charts
- 📥 **CSV Export** - Download your transaction data
- 🔒 **Privacy-First** - All data stays on your machine, no external storage

## 📸 Screenshots

### Dashboard
View spending overview with interactive charts showing category breakdowns, top merchants, and spending trends.

### Multi-Account Support
Manage and analyze transactions from multiple Gmail accounts simultaneously.

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Gmail account(s)
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Google Cloud project with Gmail API enabled

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jaskiran9941/transaction-reader.git
cd transaction-reader
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Gmail API credentials**

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions on:
- Creating a Google Cloud project
- Enabling Gmail API
- Creating OAuth 2.0 credentials
- Downloading credentials.json

5. **Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

6. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## 📖 How to Use

### First Time Setup

1. **Add Email Account(s)**
   - Open the app sidebar
   - Click "➕ Add New Account"
   - Enter a nickname (e.g., "personal" or "work")
   - Click "Authenticate New Account"
   - Complete Gmail OAuth in the browser

2. **Run Analysis**
   - Select which accounts to analyze
   - Go to "Analyze" tab
   - Click "🚀 Run Analysis"
   - Wait for emails to be fetched and analyzed

3. **View Results**
   - **Dashboard**: See spending overview, charts, and trends
   - **Analyze**: View AI-generated insights and suggestions
   - **Transactions**: Browse detailed transaction list, filter, and export

### Settings

- **Max emails to fetch**: Number of emails per account (10-200)
- **Days to look back**: How far back to search (7-90 days)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

### Gmail API Credentials

Place your `credentials.json` file in the project root. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for details.

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Anthropic Claude API
- **Email**: Gmail API (Google)
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Language**: Python 3.9+

## 📝 How It Works

1. **Email Fetching**: Connects to your Gmail account(s) via OAuth 2.0 and searches for emails containing keywords like "receipt", "order", "invoice", etc.

2. **Content Extraction**: Extracts both text and HTML email content to capture transaction details from various merchants.

3. **AI Analysis**: Sends email content to Claude AI, which intelligently:
   - Identifies actual purchases (vs promotional emails)
   - Extracts merchant, amount, date, and items
   - Categorizes transactions by type
   - Handles various email formats automatically

4. **Visualization**: Presents data through interactive charts and provides spending insights.

## 🔒 Privacy & Security

- **Local Processing**: All data processing happens on your machine
- **No Data Storage**: Transaction data is stored locally in your session only
- **OAuth 2.0**: Secure authentication with Gmail
- **Read-Only Access**: App only requests read permissions for Gmail
- **API Keys**: Your keys never leave your machine

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- **Python 3.9 Warning**: You may see warnings about Python 3.9 being past end-of-life. The app works fine but consider upgrading to Python 3.10+.
- **First-Time OAuth**: Browser must open for Gmail authentication. Ensure port 8080 is available.

## 💡 Tips

- Run analysis weekly or monthly to track spending trends
- Use multiple accounts to separate personal vs work expenses
- Adjust the "days to look back" setting based on your email volume
- Export to CSV for further analysis in Excel/Google Sheets

## 🙋 FAQ

**Q: Is my Gmail data safe?**
A: Yes! All processing happens locally. The app only reads emails (read-only access) and doesn't store anything externally.

**Q: Why do I need an Anthropic API key?**
A: The AI analysis uses Claude API. Free tier includes $5 credit. Typical usage costs $1-5/month depending on email volume.

**Q: Can I use this with other email providers?**
A: Currently Gmail only. Support for other providers (Outlook, Yahoo) may be added in future.

**Q: What if it misses some transactions?**
A: Try increasing "Max emails to fetch" and "Days to look back". Some merchants use unusual email formats.

## 🌟 Star History

If you find this project helpful, please consider giving it a star!

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

Made with ❤️ using Claude AI & Streamlit
