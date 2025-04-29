# Ollama-Local-Deep-Researcher
 
##  Quickstart

### Mac 

1. Download the Ollama app for Mac [here](https://ollama.com/download).

2. Pull a local LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b): 
```bash
ollama pull deepseek-r1:8b
```

3. Clone the repository:
```bash
git clone https://github.com/JamesSSSong/5243Team6-Deep_Research.git
cd 5243Team6-Deep_Research
```

4. Select a web search tool:

* [Tavily API](https://tavily.com/)
* [Perplexity API](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api)
* [YouTube API](https://www.getphyllo.com/post/how-to-get-youtube-api-key)

5. Copy the example environment file:
```bash
cp .env.example .env
```

6. Edit the `.env` file with your preferred text editor and add your API keys:
```bash
# Required: Choose one search provider and add its API key
TAVILY_API_KEY=tvly-xxxxx      # Get your key at https://tavily.com
PERPLEXITY_API_KEY=pplx-xxxxx  # Get your key at https://www.perplexity.ai
PERPLEXITY_API_KEY=pplx-xxxxx  # Get your key at https://www.perplexity.ai
SMTP_USERNAME=xxxx@gmail.com   # The email you will send from
SMTP_PASSWORD=xxxx             # Get your app password from https://myaccount.google.com/apppasswords
EMAIL_RECIPIENT=xxxx@gmail.com  # The email that will receive the summary
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=xxxx               # Port for Email Application
YOUTUBE_API_KEY=xxxx          # Get your key at https://www.getphyllo.com/post/how-to-get-youtube-api-key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1364074501989601341/3ehk0Nhl3v8XnKDrbxS9Qcb6jj2YBUG4OqQ4JgNX1qbu9Zwkd6835EDVFanOLxBfaCLQ
PINECONE_API_KEY=pcsk_6aiQXm_G61irwpEJv3Va7ytW4KWD63kFf2BaPjr2Egcpf5iFHibmjbe8Gk1hDpPRPcgxf
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=research-index
``` 

Note: If you prefer using environment variables directly, you can set them in your shell:
```bash
export TAVILY_API_KEY=tvly-xxxxx
# OR
export PERPLEXITY_API_KEY=pplx-xxxxx
```

After setting the keys, verify they're available:
```bash
echo $TAVILY_API_KEY  # Should show your API key
```

7. (Recommended) Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

8. Launch the assistant with the LangGraph server:

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

### Windows 

1. Download the Ollama app for Windows [here](https://ollama.com/download).

2. Pull a local LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b): 
```powershell
ollama pull deepseek-r1:8b
```

3. Clone the repository:
```bash
git clone https://github.com/JamesSSSong/5243Team6-Deep_Research.git
cd ollama-deep-web-yt-email-researcher
```
 
4. Select a web search tool:

* [Tavily API](https://tavily.com/)
* [Perplexity API](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api)

5. Copy the example environment file:
```bash
cp .env.example .env
```

Edit the `.env` file with your preferred text editor and add your API keys:
```bash
# Required: Choose one search provider and add its API key
TAVILY_API_KEY=tvly-xxxxx      # Get your key at https://tavily.com
PERPLEXITY_API_KEY=pplx-xxxxx  # Get your key at https://www.perplexity.ai
PERPLEXITY_API_KEY=pplx-xxxxx  # Get your key at https://www.perplexity.ai
SMTP_USERNAME=xxxx@gmail.com   # The email you will send from
SMTP_PASSWORD=xxxx             # Get your app password from https://myaccount.google.com/apppasswords
EMAIL_RECIPIENT=xxxx@gmail.com  # The email that will receive the summary
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=xxxx               # Port for Email Application
YOUTUBE_API_KEY=xxxx          # Get your key at https://www.getphyllo.com/post/how-to-get-youtube-api-key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1364074501989601341/3ehk0Nhl3v8XnKDrbxS9Qcb6jj2YBUG4OqQ4JgNX1qbu9Zwkd6835EDVFanOLxBfaCLQ
PINECONE_API_KEY=pcsk_6aiQXm_G61irwpEJv3Va7ytW4KWD63kFf2BaPjr2Egcpf5iFHibmjbe8Gk1hDpPRPcgxf
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=research-index
```

Note: If you prefer using environment variables directly, you can set them in Windows (via System Properties or PowerShell):

```bash
export TAVILY_API_KEY=<your_tavily_api_key>
export PERPLEXITY_API_KEY=<your_perplexity_api_key>
```

Crucially, restart your terminal/IDE (or sometimes even your computer) after setting it for the change to take effect. After setting the keys, verify they're available:
```bash
echo $TAVILY_API_KEY  # Should show your API key
```

7. (Recommended) Create a virtual environment: Install `Python 3.11` (and add to PATH during installation). Restart your terminal to ensure Python is available, then create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

8. Launch the assistant with the LangGraph server:

```powershell
# Install dependencies 
pip install -e .
pip install langgraph-cli[inmem]

# Start the LangGraph server
langgraph dev
```

### Using the LangGraph Studio UI 

When you launch LangGraph server, you should see the following output and Studio will open in your browser:
> Ready!
> 
> API: http://127.0.0.1:2024
> 
> Docs: http://127.0.0.1:2024/docs
> 
> LangGraph Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

Open `LangGraph Studio Web UI` via the URL in the output above. 

In the `configuration` tab:
* Pick your web search tool (Tavily or Perplexity) (it will by default be `Tavily`) 
* Set the name of your local LLM to use with Ollama (it will by default be `llama3.2`) 
* You can set the depth of the research iterations (it will by default be `2`)

Give the assistant a topic for research, and you can visualize its process!


## How it Works

1. **Session Start & Memory Recall**  
   - Timestamp the start of the run.  
   - Query Pinecone for the top K most relevant “memory” chunks from past runs.

2. **Query Generation**  
   - Use your local LLM (Ollama) to turn the user’s topic (plus recalled memory) into a tight search query.

3. **Multi-Source Retrieval & Persistence**  
   - **Web Search** (Tavily or Perplexity) → dedupe & format → upsert raw text into Pinecone.  
   - **YouTube Transcripts** → fetch, format → upsert into Pinecone.  
   - **Wikipedia Extracts** → pull intro paragraphs → format → upsert into Pinecone.  
   - **arXiv Abstracts** → retrieve, format → upsert into Pinecone.  
   - Record each step’s duration.

4. **Summarization**  
   - Invoke the LLM with clearly labeled blocks for Memory, Wikipedia, arXiv, Web, and YouTube content.  
   - Produce a concise summary organized into four sections:  
     1. **Background** (Wikipedia context)  
     2. **Academic Findings** (arXiv insights)  
     3. **Industry Examples** (Web & YouTube)  
     4. **Recommendations** (actionable next steps)

5. **Reflection & Follow-Up**  
   - Ask the LLM to analyze the running summary, spot knowledge gaps, and generate a new follow-up query.

6. **Iteration**  
   - Repeat steps **2–5** for a configurable number of loops, each time building on memory and refining the summary.

7. **Finalization**  
   - Compute total elapsed time.  
   - Prepend the research topic as a top-level heading.  
   - Append the full list of sources and a “Timings (s)” section showing per-step and total durations.

8. **Delivery**  
   - **Email**: send the Markdown summary via SMTP.  
   - **Discord**: post the same report (and raw timing JSON) into your channel via webhook.  

This pipeline combines iterative LLM-driven query refinement, multi-source retrieval, persistent semantic memory, structured summarization, and transparent performance metrics—delivering richer research faster over repeated runs.

## Outputs

- **Markdown Summary**  
  A finalized research report in Markdown, prefaced by  
  `# Research Topic: <your topic>`, with four structured sections (Background, Academic Findings, Industry Examples, Recommendations), followed by a bulleted “Sources” list and a “Timings (s)” table showing per‐step and total durations.

- **Email Delivery**  
  The full Markdown summary is sent via SMTP under the subject  
  `Research Summary: <your topic>`.

- **Discord Post**  
  The same Markdown report (and raw `timings` JSON) is posted to your configured Discord channel via webhook.

- **Persistent Memory**  
  All fetched chunks (web, YouTube, Wikipedia, arXiv) are upserted into Pinecone so that subsequent runs recall and build on past research.

- **LangGraph Studio State**  
  You can inspect the live graph state in Studio, including:  
  - `web_research_results`, `youtube_research_results`, `wikipedia_research_results`, `arxiv_research_results` lists  
  - `memory` (the top‐k recalled snippets)  
  - `sources_gathered`  
  - `timings` (per‐node and total run time)  
  - `running_summary`


