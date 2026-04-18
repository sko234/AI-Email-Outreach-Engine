"""
AI Outreach Engine
==================
A command-line tool that takes any company website URL and generates a
personalized cold outreach email using the OpenAI API.

Usage:
    python aoe.py

Requirements:
    - Python 3.8+
    - OPENAI_API_KEY environment variable set
    - Dependencies: requests, beautifulsoup4, openai
"""

import os
import sys
import textwrap
import requests
import openai
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ─── ANSI Color Codes ─────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[36m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"
BLUE    = "\033[34m"
RED     = "\033[31m"
DIM     = "\033[2m"

# ─── Constants ─────────────────────────────────────────────────────────────────
MAX_TEXT_LENGTH = 3000
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# ─── Prompt Template ───────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """You are an expert B2B copywriter. Based on the following website content, produce exactly four sections with no extra commentary.

Website content:
\"\"\"
{text}
\"\"\"

Respond in this exact format (include the section headers exactly as shown):

[COMPANY SUMMARY]
Write 2-3 sentences summarizing what this company does, who they serve, and their core value proposition.

[KEY FACTS]
List exactly 3 specific, interesting facts about the company. Use bullet points starting with "•".

[SUBJECT LINE]
Write one compelling email subject line (no quotes, no prefix label).

[EMAIL BODY]
Write a personalized cold outreach email under 120 words. Be specific to this company. Do not use placeholder text like [Name] or [Company]. Sign it as "Tanev". Do not include a subject line here — just the email body starting with a greeting."""


def fetch_website(url: str) -> str:
    """
    Fetch the raw HTML from the given URL.

    Args:
        url: The website URL to fetch.

    Returns:
        The raw HTML content as a string.

    Raises:
        SystemExit: On connection errors, timeouts, or bad HTTP responses.
    """
    # Ensure the URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Basic URL validation
    parsed = urlparse(url)
    if not parsed.netloc:
        print(f"\n{RED}Error:{RESET} Invalid URL — could not parse a domain from '{url}'.")
        sys.exit(1)

    headers = {"User-Agent": USER_AGENT}

    try:
        print(f"\n{DIM}Fetching {url} ...{RESET}")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text

    except requests.exceptions.ConnectionError:
        print(f"\n{RED}Error:{RESET} Could not connect to '{url}'. Check the URL and your internet connection.")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print(f"\n{RED}Error:{RESET} Request timed out after {REQUEST_TIMEOUT} seconds.")
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"\n{RED}Error:{RESET} The server returned an error: {e}")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"\n{RED}Error:{RESET} An unexpected request error occurred: {e}")
        sys.exit(1)


def extract_text(html: str) -> str:
    """
    Parse HTML and extract only visible human-readable text.

    Removes all script, style, and noscript tags before extracting text
    so that code and CSS don't pollute the output.

    Args:
        html: Raw HTML string.

    Returns:
        Cleaned visible text as a single string.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-visible elements
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Get text with spaces between elements to avoid words running together
    text = soup.get_text(separator=" ")

    # Collapse excessive whitespace into single spaces and strip blank lines
    lines = (line.strip() for line in text.splitlines())
    cleaned_lines = (line for line in lines if line)
    return " ".join(cleaned_lines)


def prepare_text(text: str) -> str:
    """
    Trim the extracted text to MAX_TEXT_LENGTH characters.

    Keeping the input short reduces API costs and latency while still
    providing enough context for the model to write a great email.

    Args:
        text: Cleaned website text.

    Returns:
        Text trimmed to at most MAX_TEXT_LENGTH characters.
    """
    if len(text) <= MAX_TEXT_LENGTH:
        return text

    trimmed = text[:MAX_TEXT_LENGTH]
    # Try to trim at the last full word to avoid cutting mid-sentence
    last_space = trimmed.rfind(" ")
    if last_space > MAX_TEXT_LENGTH * 0.9:
        trimmed = trimmed[:last_space]

    return trimmed


def generate_outreach(text: str) -> str:
    """
    Send the website text to GPT-4o and return the raw AI response.

    Reads the OPENAI_API_KEY from the environment. Exits gracefully
    if the key is missing or the API call fails.

    Args:
        text: Prepared website text (max MAX_TEXT_LENGTH characters).

    Returns:
        The full text of the model's response.

    Raises:
        SystemExit: If the API key is missing or the API returns an error.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            f"\n{RED}Error:{RESET} OPENAI_API_KEY environment variable is not set.\n"
            f"  1. Copy .env.example to .env\n"
            f"  2. Add your OpenAI API key\n"
            f"  3. Run: export OPENAI_API_KEY=your-key-here"
        )
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(text=text)

    try:
        print(f"{DIM}Generating outreach with GPT-4o...{RESET}")
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.choices:
            print(f"\n{RED}Error:{RESET} The model returned no choices. Try again.")
            sys.exit(1)
        content = response.choices[0].message.content
        if content is None:
            print(f"\n{RED}Error:{RESET} The model returned an empty response. Try again.")
            sys.exit(1)
        return content

    except openai.AuthenticationError:
        print(f"\n{RED}Error:{RESET} Invalid OpenAI API key. Check your OPENAI_API_KEY.")
        sys.exit(1)

    except openai.RateLimitError:
        print(f"\n{RED}Error:{RESET} OpenAI rate limit reached. Please wait a moment and try again.")
        sys.exit(1)

    except openai.APIStatusError as e:
        print(f"\n{RED}Error:{RESET} OpenAI API error ({e.status_code}): {e.message}")
        sys.exit(1)

    except openai.APIConnectionError:
        print(f"\n{RED}Error:{RESET} Could not connect to the OpenAI API. Check your internet connection.")
        sys.exit(1)


def parse_and_display(result: str) -> None:
    """
    Parse the model's structured response and print it in a colorful terminal format.

    Looks for the four section headers defined in PROMPT_TEMPLATE and
    renders each section with its own color and separator.

    Args:
        result: Raw text response from the model.
    """
    # Section definitions: (header_in_response, display_label, color)
    sections = [
        ("[COMPANY SUMMARY]", "COMPANY SUMMARY",  CYAN),
        ("[KEY FACTS]",       "KEY FACTS",         GREEN),
        ("[SUBJECT LINE]",    "SUBJECT LINE",       YELLOW),
        ("[EMAIL BODY]",      "EMAIL BODY",         MAGENTA),
    ]

    # Parse each section by splitting on known headers
    parsed = {}
    for i, (header, label, _) in enumerate(sections):
        start = result.find(header)
        if start == -1:
            parsed[label] = "(Not found in response)"
            continue

        # Content starts after the header line
        content_start = start + len(header)

        # Content ends at the next section header (or end of string)
        if i + 1 < len(sections):
            next_header = sections[i + 1][0]
            end = result.find(next_header, content_start)
            content = result[content_start:end] if end != -1 else result[content_start:]
        else:
            content = result[content_start:]

        parsed[label] = content.strip()

    # ── Print the formatted output ─────────────────────────────────────────────
    divider = f"{DIM}{'─' * 60}{RESET}"
    print(f"\n{divider}")
    print(f"{BOLD}{BLUE}  AI OUTREACH ENGINE — RESULTS{RESET}")
    print(divider)

    for _, label, color in sections:
        section_text = parsed.get(label, "(Not found)")

        print(f"\n{BOLD}{color}▸ {label}{RESET}")
        print(f"{divider}")

        if label == "KEY FACTS":
            # Print bullet points on separate lines for readability
            for line in section_text.splitlines():
                line = line.strip()
                if line:
                    print(f"  {line}")
        elif label == "EMAIL BODY":
            # Wrap long email lines for a clean terminal display
            wrapped = textwrap.fill(section_text, width=70, subsequent_indent="  ")
            print(f"  {wrapped}")
        else:
            print(f"  {section_text}")

    print(f"\n{divider}\n")


def main() -> None:
    """
    Entry point: prompt the user for a URL, then run the full pipeline.

    Pipeline:
        1. Ask for URL input
        2. Fetch HTML from the website
        3. Extract visible text
        4. Trim to MAX_TEXT_LENGTH characters
        5. Send to GPT-4o for analysis
        6. Parse and display the result
    """
    print(f"\n{BOLD}{BLUE}╔══════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{BLUE}║      AI OUTREACH ENGINE  v1.0.0      ║{RESET}")
    print(f"{BOLD}{BLUE}╚══════════════════════════════════════╝{RESET}")
    print(f"{DIM}Powered by OpenAI GPT-4o{RESET}\n")

    # Step 1: Get the URL from the user
    try:
        url = input(f"{BOLD}Enter a company website URL:{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{DIM}Cancelled.{RESET}")
        sys.exit(0)

    if not url:
        print(f"{RED}Error:{RESET} No URL provided.")
        sys.exit(1)

    # Step 2: Fetch the website HTML
    html = fetch_website(url)

    # Step 3: Extract visible text
    text = extract_text(html)
    if not text:
        print(f"\n{RED}Error:{RESET} No readable text found on the page.")
        sys.exit(1)

    # Step 4: Trim to token-efficient length
    prepared = prepare_text(text)

    # Step 5: Generate outreach with GPT-4o
    result = generate_outreach(prepared)

    # Step 6: Parse and display the output
    parse_and_display(result)


if __name__ == "__main__":
    main()
