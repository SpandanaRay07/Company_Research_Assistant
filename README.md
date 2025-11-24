# Company Research Assistant

A simple AI-powered assistant that helps you research companies by gathering information from multiple sources including Wikipedia, news articles, LinkedIn, and web search.

## Features

- **Multiple Sources**: Gathers information from Wikipedia, News API, LinkedIn, and web search
- **Conflict Detection**: Identifies conflicting information across sources and asks if you want to dig deeper
- **Two Modes**: 
  - **Chat Mode**: Full detailed responses with all sources
  - **Voice Mode**: Short, concise responses optimized for text-to-speech
- **Follow-up Questions**: Ask follow-up questions naturally - the assistant remembers previous context
- **Account Plan Generation**: Generate structured account plans from research

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up your API keys**:
Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
NEWS_API_KEY=your-news-api-key-here  # Optional
OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini
```

3. **Get API keys**:
   - OpenAI API key: https://platform.openai.com/api-keys
   - News API key (optional): https://newsapi.org/ (free tier available)

## Usage

### Chat Mode (Default)
```bash
python -m src.main --mode chat
```

### Voice Mode
```bash
python -m src.main --mode voice
```

**Note for macOS users**: Voice mode requires `portaudio`. Install it first:
```bash
brew install portaudio
pip install pyaudio
```

## How It Works

1. Ask about any company (e.g., "Tell me about Apple Inc")
2. The assistant searches multiple sources:
   - Wikipedia for company overview
   - News API for recent articles (if configured)
   - LinkedIn for company profile
   - Web search for additional information
3. If conflicts are found, you'll be asked if you want to dig deeper
4. You can ask follow-up questions naturally
5. Optionally generate an account plan from the research

## Sample Output

### Chat Mode Example

```
============================================================
👋 Hello there! I am a Company Research Assistant, how may i help you ?
You can ask follow-up questions anytime - I'll remember our conversation
Type 'quit' to exit when you're done
============================================================

You: Tell me about Tesla

🔍 Let me gather information from multiple sources...

============================================================
Here's what I found:
============================================================

Tesla, Inc. is an American electric vehicle and clean energy company founded in 2003. 
The company is known for manufacturing electric cars, energy storage systems, and solar 
panels. Tesla's most popular models include the Model S, Model 3, Model X, and Model Y. 
The company is led by CEO Elon Musk and is headquartered in Austin, Texas. Tesla has been 
a major player in accelerating the world's transition to sustainable energy, with a 
strong focus on innovation in battery technology and autonomous driving capabilities.

Sources I used:
  Tesla, Inc.
  Tesla reports record deliveries - Reuters
  Tesla (LinkedIn)
  Tesla Official Website

✨ Found information from 8 sources total!
============================================================

💡 Would you like me to create an account plan for this company? (yes/no)
Your answer: no

You: What's their revenue?

🔍 Great question! Let me find more about that...

============================================================
Here's what I found:
============================================================

Tesla's revenue has been growing significantly over the years. In 2023, Tesla reported 
total revenue of approximately $96.8 billion, with the majority coming from automotive 
sales. The company has seen strong growth in its energy generation and storage segment 
as well. Tesla's revenue growth has been driven by increasing vehicle deliveries and 
expansion into new markets globally.

Sources I used:
  Tesla Financial Reports
  Tesla Q4 2023 Earnings
============================================================
```

### Voice Mode Example

```
============================================================
Company Research Agent - Voice Mode
Say 'quit' when you're done
============================================================

Setting up microphone...
All set! I'm ready to listen. Ask me about any company!

🎤 Listening...
You said: Tell me about Microsoft

🔍 Let me find that information for you...

Here's what I found:
Microsoft is a major technology company founded in 1975, known for Windows, Office, 
and Azure cloud services. It's one of the world's largest tech companies with strong 
enterprise focus and significant presence in cloud computing.
```

## Project Structure

```
Company research assitant/
├── src/
│   ├── main.py              # Main entry point
│   ├── research_agent.py    # Core research agent
│   ├── wikipedia_agent.py   # Wikipedia integration
│   ├── news_agent.py         # News API integration
│   ├── linkedin_agent.py     # LinkedIn scraping
│   ├── web_search_agent.py  # Web search integration
│   └── account_plan.py       # Account plan generation
├── requirements.txt          # Python dependencies
├── .env                      # API keys (create this)
└── README.md                # This file
```

## Requirements

- Python 3.9+
- OpenAI API key (required)
- News API key (optional, for news sources)
- Internet connection

## Troubleshooting

**OpenAI API quota error**: Check your OpenAI account billing and add credits.

**Voice mode not working**: Make sure `portaudio` is installed (macOS) and all voice dependencies are installed.

**No results found**: Try rephrasing your query or check if the company name is spelled correctly.

## License

This project is for educational purposes.

