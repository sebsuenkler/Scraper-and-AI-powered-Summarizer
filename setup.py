from setuptools import setup, find_packages

setup(
    name="scraper-summarizer",
    version="0.1.0",
    description="Web page scraper and AI-powered summarizer",
    author="Sebastian Sünkler - Suenkler AI",
    packages=find_packages(),
    # Including individual Python modules that aren't in a package
    py_modules=["scraper", "summarizer"],
    # Dependencies that will be installed automatically
    install_requires=[
        "seleniumbase",     # For browser automation and scraping
        "beautifulsoup4",   # For HTML parsing
        "openai",           # For API integration with AI models
        "python-dotenv",    # For loading API keys from .env files
    ],
    # This creates the 'scraper' command that runs the main() function in scraper.py
    entry_points={
        "console_scripts": [
            "scraper=scraper:main",
        ],
    },
)
