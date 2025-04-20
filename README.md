# Web page scraper and AI-powered summarizer

A tool to scrape web pages and generate summaries using AI.

## Features

- Scrapes web content using Selenium with undetectable browser configuration
- Handles special characters in URLs automatically
- Detects language and summarize the content using [phi-4 by Microsoft](https://huggingface.co/microsoft/phi-4) via the Nebius API (modify the .env file and the get_response() method in summarizer.py to suit your needs, e.g. using a different model, API or ChatGPT)

## Live-Demo

[https://suenkler-ai.de/summarizer](https://suenkler-ai.de/summarizer)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd scraper-summarizer
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```
   pip install -e .
   ```

4. Create a `.env` file in the project directory with your Nebius API key:
   ```
   NEBIUS_API_KEY=your_api_key_here
   ```

## Usage

Use the `scraper` command followed by the `--url` parameter:

```
scraper --url https://example.com
```

To save the summary to a file, use the `--output` parameter:

```
scraper --url https://example.com --output summary.txt
```

## Handling Special Characters in URLs

The tool automatically handles special characters in URLs by using proper URL encoding. This means you can safely use URLs containing spaces, non-ASCII characters, and other special symbols.

Examples:
```
scraper --url "https://example.com/path with spaces"
scraper --url "https://example.com/search?q=special+query&lang=en"
```

## Notes

- Make sure ChromeDriver is properly installed and compatible with your Chrome version
- The tool requires an internet connection to access the [Nebius API](https://studio.nebius.com/) 
- The `.env` file with your API key must be in the directory where you run the command
- The extension folder contains the downloaded browser extension [https://github.com/OhMyGuus/I-Still-Dont-Care-About-Cookies](https://github.com/OhMyGuus/I-Still-Dont-Care-About-Cookies)
- Result quality varies based on the specific LLM model and the prompt.
