# Synergetic MultiAgent Tool Orchestrator (SMATO)

A sophisticated Python-based tool orchestration system that synergistically combines multiple autonomous agents and specialized tools. SMATO intelligently routes tasks between direct execution and LLM-powered analysis, ensuring optimal performance and accuracy.

---

## Core Architecture

- **🎭 Dual Processing Paths**:
  - Direct Execution Path: Instant tool invocation for known patterns
  - LLM-Powered Path: Intelligent analysis for complex queries
  
- **🛠️ Specialized Tools**:
  - **Calculator**: Advanced mathematical operations with direct execution
  - **Data Analysis**: Statistical processing and visualization
  - **Web Search**: Real-time internet queries via SerpAPI
  - **Wikipedia**: Knowledge base access and summarization
  - **Python REPL**: Dynamic code execution
  - **URL**: Web content processing

- **🧠 Intelligent Orchestration**:
  - Pattern Recognition: Auto-detects direct execution opportunities
  - Tool Selection: Smart routing to appropriate tools
  - Context Awareness: Maintains conversation history
  - Error Recovery: Graceful fallback mechanisms

- **⚡ Performance Features**:
  - Async Operations: Non-blocking execution
  - Memory Management: Efficient context handling
  - Direct Access: Bypass LLM when appropriate
  - Tool Synergy: Coordinated multi-tool operations

---

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for LLM orchestration)
- SerpAPI key (for web search capabilities)
- Required Python packages (see `requirements.txt`):
  ```
  # Core dependencies
  langchain>=0.1.0
  langchain-community>=0.0.10
  langchain-openai>=0.0.2
  langchain-core>=0.1.0
  langchain-experimental>=0.0.6
  openai>=1.6.1
  python-dotenv>=1.0.0

  # Tool-specific dependencies
  wikipedia>=1.4.0
  google-search-results>=2.4.2
  requests>=2.31.0
  beautifulsoup4>=4.10.0
  serpapi>=0.1.5

  # Data analysis dependencies
  pandas>=2.1.0
  numpy>=1.24.0
  matplotlib>=3.7.0
  seaborn>=0.12.0
  ```

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/EsmaeilNarimissa/SMATO.git
   cd SMATO
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Unix/MacOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your API keys
   # OPENAI_API_KEY=your_openai_api_key
   # SERPAPI_API_KEY=your_serpapi_key
   ```

   > ⚠️ **API Key Security**: Never commit your `.env` file or expose your API keys. The `.env` file is listed in `.gitignore` to prevent accidental commits. Always use environment variables or a secure secrets manager in production.

---

## Configuration

The system can be configured through environment variables in `.env`:

```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key-here
SERPAPI_API_KEY=your-serpapi-api-key-here

# Optional Settings
MODEL_NAME=gpt-3.5-turbo    # LLM model to use
TEMPERATURE=0.7             # LLM temperature
MAX_ITERATIONS=5            # Maximum iterations per query

# Tool Settings
WIKI_LANGUAGE=en            # Wikipedia language
MAX_SEARCH_RESULTS=5        # Maximum search results
URL_TIMEOUT=10             # URL request timeout
```

---

## Advanced Configuration

### Memory Settings
```python
# Memory Configuration
memory:
  max_messages: 100          # Maximum conversation history
  memory_key: "chat_history" # Memory storage key
  system_message: null       # Custom system message
```

### LLM Settings
```python
# LLM Configuration
llm:
  model_name: "gpt-3.5-turbo" # LLM model
  temperature: 0.7            # Response creativity
  max_iterations: 15          # Max tool iterations
```

### System Messages
SMATO supports different system messages for specialized contexts:
- **Default**: General-purpose assistant with tool prioritization
- **Scientific**: Specialized for formula explanations and scientific queries

### Tool Capabilities

#### Calculator
- Single expression evaluation
- Supported operations:
  - Basic: +, -, *, /, ^
  - Functions: sin, cos, tan, sqrt, log, exp
  - Constants: pi, e
- Direct execution for efficiency

#### Data Analysis
- Statistical processing
- Data visualization
- Pandas/Numpy operations
- Time series analysis

#### Web Search
- Real-time internet queries
- Multiple result synthesis
- Source verification
- Configurable result limit

#### Wikipedia
- Knowledge base access
- Multi-language support
- Article summarization
- Citation extraction

#### Python REPL
- Code execution
- Variable persistence
- Error handling
- Security restrictions

#### URL Processing
- Web content extraction
- HTML parsing
- Timeout handling
- Response validation

---

## Usage

### Command Line Interface
```bash
# Start with default settings
python main.py

# Start with custom system message
python main.py --system-message "Your custom message"

# Start with debug mode
python main.py --debug

# Start with custom history size
python main.py --max-history 200
```

### Available Commands
- **`/exit`**: End session
- **`/clear`**: Clear conversation history
- **`/history`**: View conversation history
- **`/help`**: Show available commands
- **`/debug`**: Toggle debug mode
- **`/thinking`**: Toggle thinking process display

### Example Interactions
```plaintext
# Direct Path Examples (Instant Execution)
You: 2+2
Assistant: 4

You: factorial(5)
Assistant: 120

# LLM Path Examples (Intelligent Processing)
You: analyze stock market trends for AAPL
Assistant: [Detailed market analysis with data visualization]

You: explain quantum computing
Assistant: [Comprehensive Wikipedia-based explanation]

# Multi-Tool Synergy
You: compare weather in London and New York
Assistant: [Combined weather data and analysis]
```

---

## 🐳 Docker Support

You can run SMATO using Docker. This is the recommended way as it ensures consistent behavior across different environments.

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Git installed ([Download here](https://git-scm.com/downloads))
- OpenAI and SerpAPI keys (see below)

### Quick Start

1. **Get the Code**:
   ```bash
   # Clone SMATO repository
   git clone https://github.com/EsmaeilNarimissa/SMATO.git
   cd SMATO
   ```

2. **Set Up API Keys**:
   ```bash
   # Copy example environment file
   copy .env.example .env   # On Windows
   # OR
   cp .env.example .env     # On Mac/Linux
   ```
   Edit `.env` and add your keys:
   - Get OpenAI key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Get SerpAPI key: [serpapi.com/dashboard](https://serpapi.com/dashboard)

3. **Build and Run**:
   ```bash
   # Build the container
   docker-compose build

   # Run interactively
   docker-compose run --rm smato
   ```

4. **Available Commands**:
   - `/help` - Show all commands
   - `/exit` - Exit the application
   - `/clear` - Clear conversation history
   - `/history` - View conversation history
   - `/debug` - Toggle debug mode

### Troubleshooting

If you encounter issues:
1. Make sure Docker Desktop is running
2. Try cleaning Docker cache:
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose build --no-cache
   ```
3. Verify your `.env` file exists and contains valid API keys

Note: This project is also part of my [AI Projects Collection](https://github.com/EsmaeilNarimissa/AI-Projects-by-EN/tree/main/SMATO).

---

## Project Architecture

```plaintext
smato/
├── core/                   # Core orchestration
│   ├── agent.py           # Main orchestrator
│   ├── memory.py          # Memory management
│   ├── message.py         # Message handling
│   └── __init__.py        # Core exports
├── tools/                  # Specialized tools
│   ├── calculator.py      # Direct computation
│   ├── data_analysis.py   # Data processing
│   ├── serp_search.py     # Web search
│   ├── wikipedia.py       # Knowledge base
│   ├── python_repl.py     # Code execution
│   ├── url.py             # Web processing
│   └── __init__.py        # Tool registration
├── utils/                  # Support utilities
│   ├── error_handlers.py  # Error management
│   ├── formatters.py      # Output formatting
│   ├── validators.py      # Input validation
│   └── __init__.py        # Utility exports
├── config/                # System settings
│   ├── api_keys.py        # API management
│   ├── settings.py        # Configuration
│   └── __init__.py        # Config exports
├── .env                   # Active environment
├── .env.example          # Environment template
├── .gitignore           # Git exclusions
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

---

## Development

### Testing
```bash
pytest  # Run test suite
```

### Code Quality
```bash
black .   # Format code
isort .   # Sort imports
mypy .    # Type checking
```

---

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## Contact

For questions, suggestions, or issues, please contact:
- Email: esmaeil.narimissa@gmail.com
- GitHub: [EsmaeilNarimissa](https://github.com/EsmaeilNarimissa)

---

## License

MIT License. See `LICENSE` file.

---

## Acknowledgments

- Built with LangChain (v0.1.0+)
- Powered by OpenAI's GPT models
- Enhanced with SerpAPI
- Data processing via Pandas/Numpy
