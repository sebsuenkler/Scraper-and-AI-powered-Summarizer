import os
from openai import OpenAI
from dotenv import load_dotenv

def summarize_text(text):
    """
    Main function that summarizes a text using AI.
    
    This function orchestrates the summarization process:
    1. Detects the primary language of the text
    2. Creates a summary in the detected language
    3. Identifies the main topic/category of the content
    4. Returns the category and summary together
    
    Args:
        text: The text to be summarized
        
    Returns:
        A string containing the main category followed by the summary
    """

    def init_client():
        """
        Initializes and returns the OpenAI client for Nebius API.
        
        This function:
        1. Loads environment variables from .env file
        2. Sets up the API client with the appropriate base URL and API key
        
        Returns:
            An initialized OpenAI client configured for Nebius API
        """
        load_dotenv()  # Load API key from .env file
        client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",  # Nebius API endpoint
            api_key=os.environ.get("NEBIUS_API_KEY")       # Get API key from environment variables
        )
        return client
    
    def get_response(text, tokens):
        """
        Sends a prompt to the AI model and retrieves the response.
        
        This function:
        1. Initializes the API client
        2. Sends the prompt to the Mixtral model
        3. Configures response parameters (temperature, tokens, etc.)
        4. Extracts and returns the content from the response
        
        Args:
            text: The prompt text to send to the AI
            tokens: Maximum number of tokens for the response
            
        Returns:
            The text response from the AI model
        """
        client = init_client()
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1-fast",  # Using Mixtral 8x7B model
            max_tokens=tokens,                           # Maximum length of response
            temperature=0.2,                             # Lower creativity (more focused)
            top_p=0.85,                                  # Restricted word variety
            extra_body={
                "top_k": 20                              # Consider only top 20 token options
            },
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]
        )

        # Extract the actual text content from the response
        content = response.choices[0].message.content.strip()
        return content

    def detect_language(text):
        """
        Determines the primary language of the provided text.
        
        This function uses the AI to analyze word frequency
        and identify the dominant language in the text, even if
        multiple languages are present.
        
        Args:
            text: The text to analyze for language
            
        Returns:
            A string containing the detected language
        """
        prompt = (
            f"Recognize the main language of this text disregard the content, topic, or subject matter completely. Use a frequency analysis of the words. Always choose the language with the most words, regardless of whether there are other languages in the text. Do not make assumptions based on mentioned people, places, or organizations.\n\n"
            f"At the end, **only enter the language as a single word** in the following form. No explanation, no introduction, no justification - just the keyword:\n\n"
            f"Language: <language>"
            f"Text:\n{text}\n\n"
        )     
        language = get_response(prompt, 100).strip()
        return language

    def create_summary(text, language):
        """
        Generates a concise summary of the provided text in the specified language.
        
        This function creates a well-structured summary with multiple paragraphs
        for better readability. It specifically requests the AI to avoid
        unnecessary explanations or introductions.
        
        Args:
            text: The text to summarize
            language: The language to use for the summary
            
        Returns:
            A string containing the formatted summary
        """
        prompt = (
            f"Read the following text and summarize its content briefly and precisely in **{language}** as continuous text. Try to limit the summary to a maximum of 300 words if appropriate."
            f"Return **only** the summary in {language} - without introduction, without original text, without explanation, without a translation:\n\n" \
            f"{text}\n\n" \
            f"Divide the summary into paragraphs and separate each paragraph with a blank line (\n\n) to improve readability."
        )
        summary = get_response(prompt, 1024).strip()  # Allow up to 1024 tokens for detailed summary
        return summary

    
    # Execute the summarization workflow
    language = detect_language(text)
    summary = create_summary(text, language)
    
    # Return the summary
    return summary