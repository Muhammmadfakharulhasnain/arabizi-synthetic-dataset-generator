from openai import AzureOpenAI, OpenAIError
from dotenv import load_dotenv
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
if not os.getenv("AZURE_OPENAI_API_KEY"):
    logger.error("AZURE_OPENAI_KEY not found in environment variables")
    exit(1)
if not os.getenv("AZURE_OPENAI_ENDPOINT"):
    logger.error("AZURE_ENDPOINT not found in environment variables")
    exit(1)

def translate_with_gpt(prompt, response, deployment_name="gpt-35-turbo-16k", max_retries=3):
    """
    Translate English prompt and response to Lebanese Arabizi using Azure OpenAI API.
    Returns tuple of (arabizi_prompt, arabizi_response).
    """
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_ENDPOINT")
    )
    chat_prompt = [
        {
            "role": "system",
            "content": """
You are an expert in Lebanese Arabizi, a way of writing conversational Lebanese Arabic using Latin letters and numbers. Translate English text to Lebanese Arabizi, keeping the tone natural, casual, and true to Lebanese dialect. Use these conventions:
- 3 for ع (e.g., 3arabi for Arabic)
- 7 for ح (e.g., 7ayat for hayat)
- 2 for ء (e.g., 2alb for alb)
- sh for ش (e.g., shou for شو)
- kh for خ (e.g., khayye for أخي)
- gh for غ (e.g., ghalat for غلط)
- Use Lebanese slang and expressions (e.g., "ya zalame" for "hey man", "shou" for "what").
- Avoid formal Arabic or other dialects (e.g., use "biddak" instead of Egyptian "3ayez").
- Return translations in the format:
  Prompt: [translated prompt]
  Response: [translated response]
Examples:
Input: "Hey man, you wanna buy some weed?"
Output: Prompt: Ya zalame, biddak tishtri 7ashish?
Response: Shou ya3ni?
Input: "What’s up? How’s it going?"
Output: Prompt: Shou 3am btsir? Kifak?
Response: La2, mnih, w enta?
Input: "Some what?"
Output: Prompt: Shou ya3ni?
Response: Eh, shu?
Translate the following English conversation to Lebanese Arabizi in the same format.
"""
        },
        {"role": "user", "content": f"Prompt: {prompt}\nResponse: {response}"}
    ]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=chat_prompt,
                max_tokens=150,
                temperature=0.5
            )
            content = response.choices[0].message.content if response.choices else None
            if content:
                lines = content.strip().split("\n")
                arabizi_prompt = lines[0].replace("Prompt:", "").strip() if len(lines) > 0 else prompt
                arabizi_response = lines[1].replace("Response:", "").strip() if len(lines) > 1 else response
                return arabizi_prompt, arabizi_response
            else:
                logger.warning(f"Empty response content on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Max retries reached with empty response. Skipping entry.")
                    return prompt, response
        except OpenAIError as e:
            if "content_filter" in str(e).lower():
                logger.error(f"Content filter triggered for prompt: '{prompt}'. Skipping entry.")
                with open("../data/corrected/skipped_entries.jsonl", "a", encoding='utf-8') as f:
                    json.dump({"prompt": prompt, "response": response, "error": str(e)}, f, ensure_ascii=False)
                    f.write("\n")
                return prompt, response
            elif "429" in str(e) or "Too Many Requests" in str(e):
                retry_after = getattr(e, "retry_after", 10)  # Default to 10s
                logger.info(f"Rate limit hit, retrying after {retry_after} seconds")
                time.sleep(retry_after)
            elif attempt < max_retries - 1:
                logger.error(f"API error on attempt {attempt + 1}: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Max retries reached for error: {e}. Skipping entry.")
                return prompt, response
        time.sleep(2)  # Delay between requests to avoid rate limits
