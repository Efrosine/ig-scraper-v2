# Phase 7 Quick Start Guide

## 🚀 Getting Started with Phase 7 HTTP Endpoint

Phase 7 provides a RESTful API for Instagram scraping operations. This guide will help you get started quickly.

## Prerequisites

1. **Virtual Environment**: Make sure you're in the project's virtual environment
2. **Dependencies**: Flask and other required packages should be installed
3. **Environment Variables**: `.env` file with Instagram credentials

## Quick Start

### 1. Activate Virtual Environment
```bash
cd /home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2
source venv/bin/activate
```

### 2. Verify Installation
```bash
python other/phase7_validation.py
```
You should see: `🎉 All Phase 7 validation tests passed!`

### 3. Start the API Server
```bash
python "phase files/phase7_scraper.py"
```

The server will start on `http://localhost:5000` by default.

### 4. Test the API

In another terminal, test the health endpoint:
```bash
curl -X GET http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-26T...",
  "service": "Instagram Profile Scraper API"
}
```

## API Usage Examples

### Basic Scraping Request
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "suspected_account": "malangraya_info",
    "post_count": 5,
    "comment_count": 3
  }'
```

### With Custom Accounts
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": [
      {"username": "eprosine009", "password": "desember@03"},
      {"username": "eprosen2", "password": "desember@03"}
    ],
    "suspected_account": "malangraya_info",
    "post_count": 10,
    "comment_count": 5
  }'
```

### Using Default Values (Minimal Request)
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Health check |
| POST   | `/scrape` | Trigger scraping |

## Request Parameters

For the `/scrape` endpoint:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `accounts` | Array | No | From .env | List of Instagram accounts |
| `suspected_account` | String | No | `malangraya_info` | Username to scrape |
| `post_count` | Integer | No | `10` | Number of posts to extract |
| `comment_count` | Integer | No | `5` | Comments per post |

## Response Format

### Success Response (200)
```json
{
  "status": "success",
  "timestamp": "2025-06-26T10:00:00.000Z",
  "parameters": {
    "suspected_account": "malangraya_info",
    "post_count": 10,
    "comment_count": 5,
    "accounts_used": 2
  },
  "results": [
    {
      "usernamePost": "malangraya_info",
      "urlPost": "https://www.instagram.com/p/example/",
      "releaseDate": "2025-06-25T17:00:00.000Z",
      "caption": "Sample caption",
      "comments": {
        "0": "First comment",
        "1": "Second comment"
      }
    }
  ],
  "metadata": {
    "total_posts_extracted": 10,
    "profile_info": {
      "username": "malangraya_info",
      "profile_url": "https://instagram.com/malangraya_info/"
    }
  }
}
```

### Error Response (400/500)
```json
{
  "error": "Invalid request",
  "message": "post_count must be a non-negative integer"
}
```

## Configuration

Edit `.env` file to customize:

```properties
# Server Configuration
FORWARDING_PORT=5000
API_HOST=0.0.0.0
DEBUG=false

# Default Parameters
DEFAULT_SUSPECTED_ACCOUNT=malangraya_info
DEFAULT_POST_COUNT=10
DEFAULT_COMMENT_COUNT=5

# Instagram Accounts
INSTAGRAM_ACCOUNTS=eprosine009:desember@03,eprosen2:desember@03
```

## Troubleshooting

### Server Won't Start
1. Check if port 5000 is available: `lsof -i :5000`
2. Try a different port in `.env`: `FORWARDING_PORT=5001`
3. Check dependencies: `pip install flask==2.3.3 werkzeug==2.3.7`

### Import Errors
```bash
# Reinstall dependencies
pip install -r configuration/requirements.txt
```

### Validation Errors
- Check parameter types (integers for counts, strings for usernames)
- Ensure account objects have both `username` and `password` fields
- Use non-negative integers for counts

### Scraping Fails
- Verify Instagram accounts are valid
- Check ChromeDriver is installed: `which chromedriver`
- Review logs in `logs/` directory

## Command Line Options

```bash
# Run server
python "phase files/phase7_scraper.py"

# Show help
python "phase files/phase7_scraper.py" help

# Show test instructions
python "phase files/phase7_scraper.py" test
```

## Output Files

Results are saved in:
- `output/result.json` - Latest results
- `output/backup_YYYYMMDD_HHMMSS.json` - Timestamped backups

## Testing

### Validation Tests
```bash
python other/phase7_validation.py
```

### API Demo (requires running server)
```bash
python other/phase7_api_demo.py
```

## Security Notes

- Account passwords are not logged
- Input validation prevents injection attacks
- Rate limiting prevents Instagram blocking
- Error messages don't expose system details

## Next Steps

Once Phase 7 is working correctly, you can:
1. Integrate with other applications via the REST API
2. Set up monitoring using the `/health` endpoint
3. Scale horizontally by running multiple instances
4. Proceed to Phase 8 for containerization

## Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Verify environment variables in `.env`
3. Test with the validation script first
4. Use curl to test API endpoints manually

---

**Phase 7 Complete!** 🎉

The HTTP endpoint is now ready to handle Instagram scraping requests via REST API calls.
