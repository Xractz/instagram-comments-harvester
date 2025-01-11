<div align="center">
  <h1>Instagram Comments Harvester</h1>
  
  <img src="https://github.com/user-attachments/assets/fc4ce9ca-cc44-4ce1-b209-bdc7bcff23d2" alt="Instagram Comments Harvester Logo">
  <p>A Python tool for collecting comments from Instagram posts. This tool allows you to efficiently gather comments data and save it in CSV format for further analysis.</p>
  
  [✨ Features](#-features) • [📋 Installation](#-installation) • [📖 Usage](#-usage) • [🤝 Contributing](#-contributing)
</div>

## ✨ Features

- 🔍 Collect comments from any public Instagram post
- 💾 Save comments data in CSV format
- ⚡ Fast and efficient data collection
- 🔄 Rate limit handling
- 📊 Progress tracking
- 🎯 Limit number of comments to collect
- 🔑 Session ID management via .env file

## 📋 Requirements

- Python 3.6+
- Required Python packages:
  ```
  requests
  python-dotenv
  ```

## 🚀 Installation

1. Clone this repository
   ```bash
   git clone https://github.com/Xractz/instagram-comments-harvester.git
   cd instagram-comments-harvester
   ```

2. Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Configuration

Before using the tool, you need to configure your Instagram session ID. You can do this in two ways:

1. Using the command line flag:
   ```bash
   python harvest.py -s "your_session_id_here"
   ```

2. Manually creating a .env file:
   ```
   session_id=your_session_id_here
   ```

### 🔑 How to Get Your Session ID
![Screenshot 2025-01-11 101319](https://github.com/user-attachments/assets/df8b78bc-2c55-445f-8760-f3f886026dd6)

1. Log in to Instagram in your web browser
2. Open the browser's Developer Tools (F12)
3. Go to Application/Storage > Cookies
4. Find the 'sessionid' cookie
5. Copy the value

## 📖 Usage

### Basic Usage

```bash
# Collect comments from a post (default: 100 comments)
python harvest.py -u https://www.instagram.com/p/XXXX

# Collect specific number of comments
python harvest.py -u https://www.instagram.com/p/XXXX -l 500

# Set session ID and collect comments
python harvest.py -s "your_session_id" -u https://www.instagram.com/p/XXXX -l 500
```

### Command Line Arguments

| Flag | Description |
|------|-------------|
| `-u`, `--url` | Instagram post URL to scrape comments from |
| `-l`, `--limit` | Maximum number of comments to collect (default: 100) |
| `-s`, `--sessionid` | Instagram session ID (will be saved to .env file) |

## 📁 Output Format

The tool saves comments in CSV format with the following naming convention:
```
results/[username]_[post_id]_comments_[timestamp].csv
```

### CSV Columns
![image](https://github.com/user-attachments/assets/aedabce7-dc1c-486f-ac3d-80800b39eba7)

- `comment_id`: Unique identifier for the comment
- `media_id`: Instagram post identifier
- `username`: Commenter's username
- `full_name`: Commenter's full name
- `comment_text`: Content of the comment
- `created_at`: Comment timestamp
- `likes_count`: Number of likes on the comment

## ⚠️ Important Notes

- This tool is for educational purposes only
- Respect Instagram's rate limits and terms of service
- Be mindful of Instagram's usage policies
- Your session ID is sensitive information - keep it secure
- The tool includes built-in delays to avoid rate limiting

## 🤝 Contributing

This project is open for everyone! We welcome contributions of all kinds. Here's how you can help:

- 🐛 Report bugs and issues
- 💡 Suggest new features or improvements
- 📚 Improve documentation
- 🔧 Submit pull requests
- 👨‍💻 Review code changes
- ⭐ Star the project if you find it useful

For substantial changes, please open an issue first to discuss what you would like to change.
