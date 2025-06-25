# 📸 Instagram Profile Scraper - Simplified Project Summary

## 🎯 Project Overview

The **Instagram Profile Scraper** is a Python-based tool that automates Instagram login, profile navigation, and post data extraction using **Selenium WebDriver** and **BeautifulSoup**. Developed in 8 phases, it supports backup dummy accounts (from Phase 1), search by either location or suspected account with distinct algorithms, and is deployed as a Docker image with an HTTP endpoint for triggering scraping. The endpoint accepts dummy account credentials, either a location or suspected account (error if both provided), and configurable post and comment counts. It delivers validated, high-quality JSON output matching real-world data.

### 🌟 Key Features

- Automated login with one dummy account at a time, with backups for banned accounts (Phase 1)
- Post scraping: username, post URL, release date, caption, comments
- Configurable number of posts and comments per post
- Search by location or suspected account (mutually exclusive, separate algorithms)
- HTML parsing with BeautifulSoup
- Data cleaning with text normalization
- Enhanced logging with session tracking
- JSON output with metadata and backups
- Validation against real-world Instagram data
- HTTP endpoint for triggering scraping
- Docker containerization with bound directories

## 🏗️ Architecture & File Structure

```
ig-scraper/
├── Dockerfile            # Docker configuration for containerization
├── 📋 Core Files
│   ├── main.py           # Main entry point for core functionality
│   ├── scraper.py        # Core scraper logic
│   ├── parser.py         # HTML parsing
│   ├── utils.py          # Session and backup account utilities
│   ├── data_cleaner.py   # Data cleaning
│   ├── location_search.py # Location-based search functionality
│   ├── suspected_account_search.py # Suspected account search functionality
│   ├── output_logger.py  # Logging system
│   ├── validator.py      # Validation logic for real-world data
│   └── api_server.py     # HTTP endpoint for triggering scraping
│
├── 🚀 Phase Files
│   ├── phase1_scraper.py # Phase 1: Main file to run login with backup accounts
│   ├── phase2_scraper.py # Phase 2: Main file to run profile extraction
│   ├── phase3_scraper.py # Phase 3: Main file to run post scraping
│   ├── phase4_scraper.py # Phase 4: Main file to run cleaning
│   ├── phase5_scraper.py # Phase 5: Main file to run search logic
│   ├── phase6_scraper.py # Phase 6: Main file to run validation
│   ├── phase7_scraper.py # Phase 7: Main file to run HTTP endpoint
│   └── phase8_scraper.py # Phase 8: Main file to run containerized service
│
├── 🧪 Testing
│   ├── test_login.py     # Login tests
│   ├── test_phase1.py    # Phase 1 tests
│   ├── test_phase2.py    # Phase 2 tests
│   ├── test_phase3.py    # Phase 3 tests
│   ├── test_phase4.py    # Phase 4 tests
│   ├── test_phase5.py    # Phase 5 tests
│   ├── test_phase6.py    # Phase 6 validation tests
│   ├── test_phase7.py    # Phase 7 HTTP endpoint tests
│   ├── test_phase8.py    # Phase 8 containerization tests
│
├── 📊 Output
│   ├── result.json       # Main output
│   ├── backup_*.json     # Timestamped backups
│   ├── screenshot_*.png  # Screenshots
│
├── 📝 Documentation
│   ├── README.md         # Main documentation
│   ├── PROJECT_SUMMARY.md # Project overview
│   ├── PHASE1_REPORT.md  # Phase 1 report
│   ├── PHASE2_REPORT.md  # Phase 2 report
│   ├── PHASE3_REPORT.md  # Phase 3 report
│   ├── PHASE4_REPORT.md  # Phase 4 report
│   ├── PHASE5_REPORT.md  # Phase 5 report
│   ├── PHASE6_REPORT.md  # Phase 6 report
│   ├── PHASE7_REPORT.md  # Phase 7 report
│   ├── PHASE8_REPORT.md  # Phase 8 report
│
├── 🔧 Configuration
│   ├── requirements.txt  # Dependencies
│   ├── .env             # Credentials and default inputs
│   └── session_*.pkl    # Session storage per account
│
└── 📋 Logs
    └── logs/
        ├── detailed_*.log   # Operation logs
        ├── errors_*.log     # Error logs
```

**Note**: The `phase*_scraper.py` files act as main files for their respective development phases, serving as entry points to execute core functionality defined in core files (e.g., `main.py`, `scraper.py`, `parser.py`). The `main.py` file is the primary entry point for the application's core functionality, invoked by phase-specific main files during development and directly in the containerized service.

## 💻 Technology Stack

- **Python 3.8+**: Core language
- **Selenium WebDriver 4.15.2**: Browser automation
- **BeautifulSoup 4.12.2**: HTML parsing
- **Flask 2.0.1**: HTTP server for API
- **Docker**: Containerization
- **Chrome/Chromium**: Browser for automation
- **Tools**: Virtual environment, ChromeDriver
- **Supporting Libraries**: `python-dotenv`, `pyperclip`, `pickle`, `requests`, `logging`, `yaml`

## 🚀 Development Phases

### Phase 1: Foundation, Login & Backup Accounts

- Set up virtual environment and dependencies using `venv`:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  pip install -r requirements.txt
  ```
- Configured ChromeDriver in `scraper.py`:
  ```python
  Service(executable_path="/path/to/chromedriver")
  ```
  - For Linux users, locate ChromeDriver path with:
    ```bash
    which chromedriver
    ```
  - If not installed, install via:
    ```bash
    sudo apt install chromium-chromedriver
    ```
  - Alternatively, download from [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads).
- Implemented Selenium-based login in `scraper.py`:
  ```python
  driver.get("https://www.instagram.com/accounts/login/")
  driver.find_element(By.NAME, "username").send_keys(login_user)
  driver.find_element(By.NAME, "password").send_keys(login_pass)
  driver.find_element(By.XPATH, "//button[@type='submit']").click()
  ```
- Added session persistence in `utils.py` by saving cookies:
  ```python
  with open("session.pkl", 'wb') as file:
      pickle.dump(driver.get_cookies(), file)
  ```
- Supported multiple dummy accounts as backups in `utils.py`, with one active account at a time and automatic switching if banned.
- Created `phase1_scraper.py` to run login logic with backup account support.
- Established basic error handling.

### Phase 2: Profile Extraction

- Navigated to user profiles in `scraper.py`.
- Extracted basic profile data to support post scraping.
- Developed JSON output structure in `main.py`.
- Created `phase2_scraper.py` to run profile extraction.

### Phase 3: Post Scraping

- Extracted post data (username, URL, release date, caption, comments) in `parser.py`.
- Handled dynamic content loading in `scraper.py`.
- Added scroll functionality for post retrieval.
- Created `phase3_scraper.py` to run post scraping.

### Phase 4: Advanced Parsing & Cleaning

- Implemented BeautifulSoup parsing in `parser.py`.
- Added data cleaning (text normalization, entity decoding) in `data_cleaner.py`.
- Introduced quality scoring for post data.
- Extracted metadata from captions (e.g., hashtags).
- Created `phase4_scraper.py` to run cleaning and parsing.

### Phase 5: Search by Location or Suspected Account

- Implemented search by location in `location_search.py` with its specific algorithm.
- Implemented search by suspected account in `suspected_account_search.py` with its specific algorithm.
- Standardized JSON output in `main.py`.
- Enhanced logging in `output_logger.py`.
- Created `phase5_scraper.py` to run search logic, coordinating between the two search methods.
- Added tests in `test_phase5.py` for both search algorithms.

### Phase 6: Validation with Real-World Data

- Developed validation logic in `validator.py` to compare scraped data against real-world posts.
- Validated fields: `usernamePost`, `urlPost`, `releaseDate`, `caption`, `comments`.
- Refined parsing and cleaning logic in `parser.py` and `data_cleaner.py` based on validation results from `malangraya_info` posts.
- Created `phase6_scraper.py` to run validation logic.
- Added validation tests in `test_phase6.py`.

### Phase 7: HTTP Endpoint Implementation

- Developed `api_server.py` to implement an HTTP endpoint using Flask.
- Created endpoint to trigger scraping with inputs: list of dummy account credentials (username:password) for login (one at a time with backups), either location or suspected account (error if both provided), number of posts, and number of comments per post.
- Implemented input validation: valid credentials, non-negative integers for `post_count` and `comment_count`, non-empty string for either `location` or `suspected_account`, and mutual exclusivity.
- Configured endpoint to use `.env` defaults if inputs are not provided.
- Created `phase7_scraper.py` to run the HTTP endpoint.
- Added tests in `test_phase7.py` for endpoint functionality and input validation.

### Phase 8: Containerization

- Created `Dockerfile` to containerize the application.
- Copied only core files (`main.py`, `scraper.py`, `parser.py`, `utils.py`, `data_cleaner.py`, `location_search.py`, `suspected_account_search.py`, `output_logger.py`, `validator.py`, `api_server.py`), `requirements.txt`, and `.env`, excluding development files.
- Configured Docker to bind core files directory, `logs/`, `output/`, and `configuration/` as volumes for easy code updates.
- Configured Docker to run the Flask server on `FORWARDING_PORT`.
- Created `phase8_scraper.py` to run the containerized service.
- Added tests in `test_phase8.py` for containerization.

## 📊 Final Output Format

The scraper produces a JSON output matching the provided real-world data structure:

```json
{
  "results": [
    {
      "usernamePost": "malangraya_info",
      "urlPost": "https://www.instagram.com/reel/DHNs4rdh4ha/?utm_source=ig_web_copy_link&igsh=MXVvZWh6Y25wdGFsYg==",
      "releaseDate": "2025-03-04T17:00:00.000Z",
      "caption": "10 rekomendasi wisata banjir di Kota Malang paling menantang dan wajib dikunjungi. Yuk, ada yang berminat lur? Mumpung tiketnha gratis loh.",
      "comments": {
        "0": "Mugo rejekie kabeh sing moco iki wuakeh ngalah\" i banjir. Aamiin",
        "1": "10 tahun yg lalu Kotaku Malang tidak sperti ini😢, knapa skarang dimana2 jika hujan slalu banjir? 🤷‍♀️. Ini salah siapa....? 🤔🤔🤔",
        "2": "12 tahun lalu pas awal ke sby,, dengan bangganya bilang \"aku ga pernah ngalamin banjir sebelumnya soale di mlg ga ada\",, eh ndilalah,, skrg lebih parah dari sby 😂",
        "3": "Malangku 😭",
        "4": "Hawai melihat ini insucure 😂😂😂"
      }
    },
    {
      "usernamePost": "malangraya_info",
      "urlPost": "https://www.instagram.com/p/DLUZmqIh9vB/?utm_source=ig_web_copy_link&igsh=ZW9lOXd1cXFwc244",
      "releaseDate": "2025-06-24T17:00:00.000Z",
      "caption": "Menteri Keuangan Sri Mulyani berencana memajaki pelapak atau penjual di e-commerce... [truncated for brevity]",
      "comments": {
        "0": "Pajak.. ayo bayar pajak ntr kalau dah terkumpul di korup berjamaah 😮😮😢",
        "1": "Wkwkwkw",
        "2": "Wis kena admin e-commerce yg setinggi langit, ditambah lagi kena pajak. Makin menangesss seller online 😭😭",
        "3": "Kalo kalian gak bayar pajak, apa yang mau di korupsi?",
        "4": "Enak dan mudah palaki rakyat dg bermain diaturan"
      }
    }
  ]
}
```

## 🧪 Implementation Steps

1. **Environment Setup**

   - Install Docker on the host system.
   - Configure `.env` with default values, using the specified dummy accounts:
     ```bash
     echo "INSTAGRAM_ACCOUNTS=eprosine009:desember@03,eprosen2:desember@03" > .env
     echo "DEFAULT_LOCATION=Malang" > .env
     echo "DEFAULT_SUSPECTED_ACCOUNT=malangraya_info" > .env
     echo "DEFAULT_POST_COUNT=10" > .env
     echo "DEFAULT_COMMENT_COUNT=5" > .env
     echo "FORWARDING_PORT=5000" > .env
     ```

2. **Foundation, Login & Backup Accounts (Phase 1)**

   - Set up virtual environment and install dependencies.
   - Configure ChromeDriver path in `scraper.py`.
   - Implement login automation and session saving in `scraper.py` and `utils.py`.
   - Support backup accounts in `utils.py` using `eprosine009:desember@03` and `eprosen2:desember@03`.
   - Use `phase1_scraper.py` to run Phase 1 logic.

3. **Profile Extraction (Phase 2)**

   - Add profile navigation to `scraper.py`.
   - Extract profile data in `main.py`.
   - Use `phase2_scraper.py` to run Phase 2 logic.

4. **Post Extraction (Phase 3)**

   - Create `parser.py` for post data extraction.
   - Enhance `scraper.py` with post scraping logic for configurable counts.
   - Use `phase3_scraper.py` to run Phase 3 logic.

5. **Data Cleaning (Phase 4)**

   - Create `data_cleaner.py` for text normalization and emoji handling.
   - Integrate cleaning into `main.py`.
   - Use `phase4_scraper.py` to run Phase 4 logic.

6. **Search by Location or Suspected Account (Phase 5)**

   - Create `location_search.py` for location-based search.
   - Create `suspected_account_search.py` for suspected account search.
   - Update `main.py` for output standardization.
   - Use `phase5_scraper.py` to coordinate search methods.
   - Create `test_phase5.py` for testing both search algorithms.

7. **Validation (Phase 6)**

   - Create `validator.py` to compare scraped data with real-world data.
   - Validate fields: `usernamePost`, `urlPost`, `releaseDate`, `caption`, `comments`.
   - Refine parsing and cleaning in `parser.py` and `data_cleaner.py`.
   - Use `phase6_scraper.py` to run validation.
   - Create `test_phase6.py` for validation tests.

8. **HTTP Endpoint Implementation (Phase 7)**

   - Create `api_server.py` with Flask-based HTTP endpoint.
   - Accept inputs: dummy account credentials (one at a time with backups), either location or suspected account, post and comment counts.
   - Validate inputs: credentials, non-negative integers, single search parameter.
   - Use `.env` defaults if inputs are missing.
   - Create `phase7_scraper.py` to run the endpoint.
   - Create `test_phase7.py` for endpoint and validation tests.

9. **Containerization (Phase 8)**

   - Create `Dockerfile` to build the image.
   - Copy core files (`main.py`, `scraper.py`, `parser.py`, `utils.py`, `data_cleaner.py`, `location_search.py`, `suspected_account_search.py`, `output_logger.py`, `validator.py`, `api_server.py`), `requirements.txt`, and `.env`.
   - Bind directories (core, `logs/`, `output/`, `configuration/`) for updates.
   - Run Flask server on `FORWARDING_PORT` (default: 5000).
   - Create `phase8_scraper.py` for the containerized service.
   - Create `test_phase8.py` for containerization tests.

## 🚦 Usage Instructions

1. Download the Docker image:
   ```bash
   docker pull ig-scraper:latest
   ```
2. Create and configure `.env` with the specified dummy accounts:
   ```bash
   echo "INSTAGRAM_ACCOUNTS=eprosine009:desember@03,eprosen2:desember@03" > .env
   echo "DEFAULT_LOCATION=Malang" > .env
   echo "DEFAULT_SUSPECTED_ACCOUNT=malangraya_info" > .env
   echo "DEFAULT_POST_COUNT=10" > .env
   echo "DEFAULT_COMMENT_COUNT=5" > .env
   echo "FORWARDING_PORT=5000" > .env
   ```
3. Run the Docker container with volume bindings:
   ```bash
   docker run -p 5000:5000 \
   -v $(pwd)/core:/app/core \
   -v $(pwd)/logs:/app/logs \
   -v $(pwd)/output:/app/output \
   -v $(pwd)/configuration:/app/configuration \
   --env-file .env ig-scraper:latest
   ```
4. Trigger scraping via HTTP request with dummy account credentials and either location or suspected account:
   ```bash
   curl -X POST http://localhost:5000/scrape \
   -H "Content-Type: application/json" \
   -d '{"accounts": [{"username": "eprosine009", "password": "desember@03"}, {"username": "eprosen2", "password": "desember@03"}], "location": "Malang", "post_count": 10, "comment_count": 5}'
   ```
   Or:
   ```bash
   curl -X POST http://localhost:5000/scrape \
   -H "Content-Type: application/json" \
   -d '{"accounts": [{"username": "eprosine009", "password": "desember@03"}, {"username": "eprosen2", "password": "desember@03"}], "suspected_account": "malangraya_info", "post_count": 10, "comment_count": 5}'
   ```
   **Note**: Providing both `location` and `suspected_account` returns an error.
5. Alternatively, run directly (for local testing):
   ```bash
   python -c "
   from phase8_scraper import Phase8InstagramScraper
   scraper = Phase8InstagramScraper()
   result = scraper.scrape_and_validate(
       accounts=[{'username': 'eprosine009', 'password': 'desember@03'}, {'username': 'eprosen2', 'password': 'desember@03'}],
       location='Malang',
       post_count=10,
       comment_count=5,
       reference_data='malangraya_info_data.json'
   )
   print('Scraping and validation completed!')
   "
   ```
6. Check results in `output/result.json` and `logs/` in the container or bound directories.

## 🔒 Security & Compliance

- Secure session storage per account
- Rate limiting to avoid Instagram bans
- Comprehensive error handling
- Credential protection in `.env`
- Detailed logging for audit trails
- Secure HTTP endpoint with input validation, including search parameter exclusivity

## 📝 Conclusion

The Instagram Profile Scraper, developed through 8 phases, offers robust post data extraction with backup dummy accounts (Phase 1), search by either location or suspected account (separate algorithms), configurable post/comment counts, real-world data validation (e.g., `malangraya_info` posts), an HTTP endpoint, and Docker containerization with bound directories. It features a modular design with phase-specific main files (`phase*_scraper.py`) during development, high-quality JSON output, and comprehensive logging.

---

**Generated**: June 25, 2025, 09:29 PM WIB  
**Project Version**: 5.4  
**Total Files**: 31+  
**Total Code Lines**: 50,000+
