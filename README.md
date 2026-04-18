# AI Outreach Engine

A Python command-line tool that takes any company website URL and automatically generates a personalized cold outreach email using the Anthropic Claude API or the OpenAI API .

You give it a URL. It reads the website, figures out what the company does, and writes a compelling email — complete with a subject line and 3 key facts — in seconds.

---

## What It Does

1. You enter a company website URL
2. It fetches and reads the visible text on the page
3. It sends that content to Claude/OpenAI (sonnet-4-5 or the gpt 4o)
4. Claude/GPT analyzes the company and produces:
   - A 2-3 sentence company summary
   - 3 interesting facts about the company
   - A compelling email subject line
   - A personalized cold outreach email (under 120 words), signed by "Tanev"
5. Everything is displayed in a clean, color-coded terminal format

---

## Installation

**Requirements:** Python 3.8+ and an [Anthropic/OpenAI API key].

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-outreach-engine.git
cd ai-outreach-engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

Copy the example file and add your key:

```bash
cp .env.example .env
```

Open `.env` and replace `your-key-here` with your actual Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Then export it in your terminal:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

> On Windows (Command Prompt): `set ANTHROPIC_API_KEY=sk-ant-...`  
> On Windows (PowerShell): `$env:ANTHROPIC_API_KEY="sk-ant-..."`

---

## How to Run

```bash
python app.py
```

You will be prompted to enter a company URL:

```
Enter a company website URL: stripe.com
```

That's it. The tool handles everything from there.

---

## Example Output

```
╔══════════════════════════════════════╗
║      AI OUTREACH ENGINE  v1.0.0      ║
╚══════════════════════════════════════╝
Powered by Anthropic Claude

Enter a company website URL: stripe.com

Fetching https://stripe.com ...
Generating outreach with Claude...

────────────────────────────────────────────────────────────
  AI OUTREACH ENGINE — RESULTS
────────────────────────────────────────────────────────────

▸ COMPANY SUMMARY
────────────────────────────────────────────────────────────
  Stripe is a global financial infrastructure platform that helps
  businesses of all sizes accept payments, manage revenue, and build
  financial products. They serve millions of companies — from startups
  to Fortune 500 enterprises — across more than 135 countries.

▸ KEY FACTS
────────────────────────────────────────────────────────────
  • Stripe processes hundreds of billions of dollars in payments annually
  • Their products span payments, billing, fraud prevention, and banking-as-a-service
  • Used by leading companies including Amazon, Shopify, and Salesforce

▸ SUBJECT LINE
────────────────────────────────────────────────────────────
  A faster way to handle your payment reconciliation

▸ EMAIL BODY
────────────────────────────────────────────────────────────
  Hi team,

  I've been following Stripe's growth in the financial infrastructure
  space — the way you've made complex payment flows accessible to
  developers worldwide is genuinely impressive.

  I work with finance teams at high-growth SaaS companies, and I've
  noticed that even the best payment infrastructure still leaves
  reconciliation as a manual headache. We've built a solution that
  plugs directly into Stripe and automates the whole process.

  Worth a 20-minute call to see if it's a fit?

  Best,
  Tanev

────────────────────────────────────────────────────────────
```

---

## Project Structure

```
ai-outreach-engine/
├── app.py            # Main application (all logic lives here)
├── requirements.txt  # Pinned Python dependencies
├── .env.example      # Template for your API key
├── LICENSE           # MIT License
└── README.md         # This file
```

---

## Error Handling

The tool handles all common failure cases gracefully:

| Situation | What happens |
|---|---|
| Invalid or unreachable URL | Clear error message, exit cleanly |
| Network timeout | Timeout error with instructions |
| Missing API key | Step-by-step instructions to fix it |
| Invalid API key | Authentication error message |
| Anthropic API error | HTTP status code + error description |
| Empty page content | Warning message, exit cleanly |

---

## Contributing

Contributions are welcome! This project is intentionally kept simple so that beginners can jump in.

**Good first issues:**
- Add support for reading PDFs or LinkedIn URLs
- Add a `--save` flag to export the output to a `.txt` file
- Support multiple URLs in one run (batch mode)
- Add a `--language` flag to generate emails in other languages
- Improve the prompt for specific industries (SaaS, e-commerce, etc.)

**How to contribute:**

1. Fork this repository
2. Create a new branch: `git checkout -b my-feature`
3. Make your changes and commit: `git commit -m "Add my feature"`
4. Push to your fork: `git push origin my-feature`
5. Open a Pull Request

Please keep code readable and well-commented. New functions should follow the same style as the existing ones.

---

## License

MIT — see [LICENSE](LICENSE) for details.
