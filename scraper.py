import os
import inspect
import argparse
import urllib.parse  # Standard library for URL handling
from seleniumbase import Driver
import time
import logging

from summarizer import summarize_text
from bs4 import BeautifulSoup

# Configure module logger
logger = logging.getLogger(__name__)

def strip_html_tags(html_string):
    """
    Removes HTML tags from a string.

    Args:
        html_string: The HTML string to be processed.

    Returns:
        A string containing the text content without HTML tags.
    """
    soup = BeautifulSoup(html_string, "html.parser")
    return soup.get_text(separator=" ", strip=True)

class ScraperSummarizer:
    def __init__(self):
        self.ext_path = self.read_extension_path()
        self.driver = None  # Initialize driver only when needed
        self.url = None

    def set_url(self, url):
        """
        Sets the URL to scrape, handling special characters properly.
        
        This method parses the URL and selectively encodes different parts:
        - The path component (encodes spaces and special chars)
        - The query string (preserves = and & for parameter structure)
        - The fragment (encodes special characters)
        
        Args:
            url: The raw URL string that might contain special characters
            
        Returns:
            self: For method chaining
        """
        # Parse URL into components
        parsed_url = urllib.parse.urlparse(url)
        
        # Selectively encode only certain parts of the URL to maintain structure
        # but escape special characters
        safe_url = urllib.parse.urlunparse((
            parsed_url.scheme,                                      # http/https unchanged
            parsed_url.netloc,                                      # domain unchanged
            urllib.parse.quote(parsed_url.path),                    # encode path (spaces etc)
            parsed_url.params,                                      # params unchanged
            urllib.parse.quote_plus(parsed_url.query, safe='=&'),   # encode query, preserve = and &
            urllib.parse.quote(parsed_url.fragment)                 # encode fragment
        ))
        self.url = safe_url
        return self

    def get_url(self):
        return self.url
        
    def init_driver(self):
        """
        Initializes the Selenium WebDriver with anti-detection settings.
        
        This configures a ChromeDriver with settings to avoid bot detection:
        - undetectable: Avoids common fingerprinting methods
        - uc: Uses undetectable Chrome mode
        - custom user agent: Mimics a standard browser
        - headless2: Runs in headless mode but with better site compatibility
        
        Returns:
            The configured WebDriver instance
        """
        if self.driver is not None:
            logger.warning("Driver already initialized, returning existing instance")
            return self.driver
            
        try:
            logger.debug("Initializing Chrome driver")
            driver_options = {
                "browser": "chrome",             # Use Chrome browser
                "wire": True,                    # Enable wire mode for better request handling
                "uc": True,                      # Undetectable Chrome mode
                "headless2": True,               # Improved headless mode
                "incognito": False,              # Not using incognito
                "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "do_not_track": True,            # Add DNT header
                "undetectable": True,            # Additional undetectable settings
                "no_sandbox": True               # No sandbox for better compatibility
            }

            # Only add extension if it exists
            if os.path.exists(self.ext_path):
                driver_options["extension_dir"] = self.ext_path

            page_load_timeout = 60
            self.driver = Driver(**driver_options)

            self.driver.set_page_load_timeout(page_load_timeout)
            self.driver.set_script_timeout(min(10, page_load_timeout * 0.5))
            self.driver.implicitly_wait(60)

            try:
                self.driver.execute_cdp_cmd("Network.enable", {})
            except Exception as e:
                logger.warning(f"CDP Network enable failed: {e}")

            return self.driver
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}", exc_info=True)
            raise

    def close(self):
        """
        Safely closes the browser and cleans up resources.
        """
        if self.driver is not None:
            try:
                logger.debug("Closing browser driver")
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None
                logger.debug("Driver set to None")

    def read_extension_path(self):
        # Define the path for configurations and extensions
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        ext_path = os.path.join(currentdir, "extension")
        return ext_path

class ScraperSummarizer(ScraperSummarizer):
    
    def summarize(self):
        """
        Scrapes the web page and generates a summary of its content.
        
        This method:
        1. Accesses the URL with Selenium
        2. Scrolls to load dynamic content
        3. Extracts and cleans the text content
        4. Limits the content to the first 20,000 words
        5. Calls the summarizer to generate a summary
        
        Returns:
            A string containing the generated summary or error message
        """
        if self.url:
            try:
                logger.info(f"Accessing URL: {self.url}")
                # Initialize the driver
                self.init_driver()
                
                # Load the page
                self.driver.get(self.url)
                # Wait for initial content to load
                time.sleep(1)
                # Scroll to bottom to load any lazy-loaded content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait for scrolled content to load
                time.sleep(1)
                
                # Remove HTML and extract text
                stripped_text = strip_html_tags(self.driver.page_source)
                
                # Limit to first 5,000 words to avoid token limits
                number_of_words = 5000
                words = stripped_text.split()
                reduced_content = ' '.join(words[:number_of_words])
                
                # Remove quotes that might interfere with the API prompt
                reduced_content = reduced_content.replace("'", "").replace('"', '')
         
                logger.info("Generating summary...")
                # Call the AI summarizer
                self.summary = summarize_text(reduced_content)
                return self.summary
            except Exception as e:
                logger.error(f"Error during scraping or summarizing: {e}", exc_info=True)
                return f"Error: {str(e)}"
            finally:
                # Always close the driver to properly clean up resources
                self.close()
        else:
            return "Error: No URL provided"

def main():
    """
    Main function that serves as the entry point for the command-line interface.
    
    This function:
    1. Parses command-line arguments
    2. Initializes the scraper with the provided URL
    3. Generates a summary
    4. Either saves the summary to a file or prints it to the console
    5. Ensures the browser is properly closed
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Web page scraper and summarizer')
    parser.add_argument('--url', type=str, required=True, 
                        help='URL of the web page to scrape and summarize')
    parser.add_argument('--output', type=str, 
                        help='Optional file to save the summary to')
    args = parser.parse_args()
    
    # Initialize the scraper with the provided URL
    scraper_summarizer = ScraperSummarizer()
    scraper_summarizer.set_url(args.url)
    
    try:
        # Get the summary
        content = scraper_summarizer.summarize()
        
        # Write to file if output option is provided
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Summary saved to {args.output}")
        else:
            # Otherwise print to console
            print("\n" + "="*50 + " SUMMARY " + "="*50)
            print(content)
            print("="*110)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always close the driver to prevent browser processes from remaining active
        scraper_summarizer.close()

if __name__ == "__main__":
    main()