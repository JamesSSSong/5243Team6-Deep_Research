import json
import time
from typing_extensions import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from email.mime.text import MIMEText
from email.header import Header

from assistant.configuration import Configuration, SearchAPI
from assistant.utils import (
    deduplicate_and_format_sources,
    tavily_search,
    format_sources,
    perplexity_search,
    youtube_search,  # new import for YouTube search
    fetch_wikipedia, 
    fetch_arxiv, 
    send_discord_message,
    semantic_recall,
    upsert_to_pinecone
)
from assistant.state import SummaryState, SummaryStateInput, SummaryStateOutput
from assistant.prompts import (
    query_writer_instructions,
    summarizer_instructions,
    reflection_instructions,
)


# Nodes
def generate_query(state: SummaryState, config: RunnableConfig):
    """Generate a query for web search"""
    
    # start overall research timer
    state.timings['start'] = time.time()

    # Format the prompt
    query_writer_instructions_formatted = query_writer_instructions.format(
        research_topic=state.research_topic
    )

    # Generate a query
    configurable = Configuration.from_runnable_config(config)
    llm_json_mode = ChatOllama(
        model=configurable.local_llm, temperature=0, format="json"
    )
    result = llm_json_mode.invoke(
        [
            SystemMessage(content=query_writer_instructions_formatted),
            HumanMessage(content=f"Generate a query for web search:"),
        ]
    )
    query = json.loads(result.content)

    return {"search_query": query["query"]}


def web_research(state: SummaryState, config: RunnableConfig):
    """Gather information from the web"""
    
    start = time.time()
    
    # Configure
    configurable = Configuration.from_runnable_config(config)

    # Handle both cases for search_api:
    # 1. When selected in Studio UI -> returns a string (e.g. "tavily")
    # 2. When using default -> returns an Enum (e.g. SearchAPI.TAVILY)
    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    # Search the web
    if search_api == "tavily":
        search_results = tavily_search(
            state.search_query, include_raw_content=True, max_results=1
        )
        search_str = deduplicate_and_format_sources(
            search_results, max_tokens_per_source=1000, include_raw_content=True
        )
    elif search_api == "perplexity":
        search_results = perplexity_search(
            state.search_query, state.research_loop_count
        )
        search_str = deduplicate_and_format_sources(
            search_results, max_tokens_per_source=1000, include_raw_content=False
        )
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    state.web_research_results.append(search_str)
    state.sources_gathered.append(format_sources(search_results))

    # record web step duration
    state.timings['web_research'] = time.time() - start
    
    upsert_to_pinecone(
        source_id=f"web_{state.research_loop_count}",
        text=search_str,
        topic=state.research_topic,
        config=Configuration.from_runnable_config(config),
    )

    return {
        "web_research_results": state.web_research_results,
        "research_loop_count": state.research_loop_count + 1,
    }


def youtube_research(state: SummaryState, config: RunnableConfig):
    """Gather information from YouTube videos, including transcripts."""

    start = time.time()

    configurable = Configuration.from_runnable_config(config)
    if not configurable.youtube_api_key:
        raise ValueError("YouTube API key not configured in Configuration.")

    youtube_results = youtube_search(
        state.search_query, configurable.youtube_api_key, max_results=3
    )
    youtube_str = deduplicate_and_format_sources(
        youtube_results, max_tokens_per_source=500, include_raw_content=True
    )
    state.youtube_research_results.append(youtube_str)
    state.sources_gathered.append(format_sources(youtube_results))

    # record YouTube step duration
    state.timings['youtube_research'] = time.time() - start

    upsert_to_pinecone(
        source_id=f"yt_{state.research_loop_count}",
        text=youtube_str,
        topic=state.research_topic,
        config=Configuration.from_runnable_config(config),
    )

    return {"youtube_research_results": state.youtube_research_results}


def wikipedia_research(state: SummaryState, config: RunnableConfig):
    """Gather intro extracts from Wikipedia."""
    
    start = time.time()
    
    wiki_results = fetch_wikipedia(state.search_query, limit=3)
    wiki_str = deduplicate_and_format_sources(
        {"results": wiki_results},
        max_tokens_per_source=500,
        include_raw_content=True
    )
    state.wikipedia_research_results.append(wiki_str)
    state.sources_gathered.append(format_sources({"results": wiki_results}))

    # record Wikipedia step duration
    state.timings['wikipedia_research'] = time.time() - start

    upsert_to_pinecone(
        source_id=f"wiki_{state.research_loop_count}",
        text=wiki_str,
        topic=state.research_topic,
        config=Configuration.from_runnable_config(config),
    )

    return {"wikipedia_research_results": state.wikipedia_research_results}



def arxiv_research(state: SummaryState, config: RunnableConfig):
    start = time.time()
    arxiv_results = fetch_arxiv(state.search_query, max_results=3)
    arxiv_str = deduplicate_and_format_sources(
        {"results": arxiv_results},
        max_tokens_per_source=500,
        include_raw_content=True
    )
    state.arxiv_research_results.append(arxiv_str)
    state.sources_gathered.append(format_sources({"results": arxiv_results}))
    
    # record arXiv step duration
    state.timings['arxiv_research'] = time.time() - start

    upsert_to_pinecone(
        source_id=f"arxiv_{state.research_loop_count}",
        text=arxiv_str,
        topic=state.research_topic,
        config=Configuration.from_runnable_config(config),
    )
    
    return {"arxiv_research_results": state.arxiv_research_results}



def summarize_sources(state: SummaryState, config: RunnableConfig):
    """Summarize the gathered sources, including both web and YouTube research"""

    # Existing summary
    existing_summary   = state.running_summary or ""
    wiki_block         = state.wikipedia_research_results[-1] if state.wikipedia_research_results else ""
    arxiv_block        = state.arxiv_research_results[-1]    if state.arxiv_research_results    else ""
    web_block          = state.web_research_results[-1]      if state.web_research_results      else ""
    youtube_block      = "\n".join(state.youtube_research_results) if state.youtube_research_results else ""
    memory_block     = "\n".join(state.memory)             if state.memory                  else ""

    start = time.time()

    # Build a single labeled prompt for the LLM
    human_message_content = f"""
<User Input>
{state.research_topic}
</User Input>

<Memory>
{memory_block}
</Memory>

<Existing Summary>
{existing_summary}
</Existing Summary>

<Background (Wikipedia)>
{wiki_block}
</Background (Wikipedia)>

<Academic Findings (arXiv)>
{arxiv_block}
</Academic Findings (arXiv)>

<Industry Examples (Web)>
{web_block}
</Industry Examples (Web)>

<Industry Examples (YouTube)>
{youtube_block}
</Industry Examples (YouTube)>
"""

    # Run the LLM to generate an updated summary
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0)
    result = llm.invoke(
        [
            SystemMessage(content=summarizer_instructions),
            HumanMessage(content=human_message_content),
        ]
    )

    running_summary = result.content

    # Remove any <think> tags if present
    while "<think>" in running_summary and "</think>" in running_summary:
        start = running_summary.find("<think>")
        end = running_summary.find("</think>") + len("</think>")
        running_summary = running_summary[:start] + running_summary[end:]

    state.running_summary = running_summary
    state.timings['summarize_sources'] = time.time() - start
    
    return {"running_summary": running_summary}


def reflect_on_summary(state: SummaryState, config: RunnableConfig):
    """Reflect on the summary and generate a follow-up query"""

    configurable = Configuration.from_runnable_config(config)
    llm_json_mode = ChatOllama(
        model=configurable.local_llm, temperature=0, format="json"
    )
    result = llm_json_mode.invoke(
        [
            SystemMessage(
                content=reflection_instructions.format(
                    research_topic=state.research_topic
                )
            ),
            HumanMessage(
                content=f"Identify a knowledge gap and generate a follow-up web search query based on our existing knowledge: {state.running_summary}"
            ),
        ]
    )
    follow_up_query = json.loads(result.content)

    query = follow_up_query.get("follow_up_query")
    if not query:
        return {"search_query": f"Tell me more about {state.research_topic}"}

    return {"search_query": follow_up_query["follow_up_query"]}


def finalize_summary(state: SummaryState):
    if 'start' in state.timings:
        state.timings['total_research_time'] = time.time() - state.timings['start']
        
    # Format all accumulated sources into a single bulleted list
    all_sources = "\n".join(source for source in state.sources_gathered)
    title = f"# Research Topic: {state.research_topic}\n\n"
    state.running_summary = (
        f"{title}"
        f"## Summary\n\n"
        f"{state.running_summary}\n\n"
        f"### Sources:\n{all_sources}"
    )

    # Append Timings section
    if state.timings:
        timing_lines = "\n".join(f"* {step}: {secs:.2f}s"
                                 for step, secs in state.timings.items())
        state.running_summary += f"\n\n### Timings (s)\n{timing_lines}"

    # return both the markdown and the raw timings dict
    return {
        "running_summary": state.running_summary,
        "timings": state.timings
    }


def send_email(state: SummaryState, config: RunnableConfig):
    """Send the final summary via email."""
    configurable = Configuration.from_runnable_config(config)
    if not configurable.email_recipient:
        raise ValueError("Email recipient not configured in Configuration.")

    subject = f"Research Summary: {state.research_topic}"
    body = state.running_summary
    from_email = configurable.smtp_username if configurable.smtp_username else "no-reply@example.com"
    to_email = configurable.email_recipient

    # Create a MIMEText object to handle UTF-8 encoding
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = from_email
    msg["To"] = to_email

    import smtplib
    smtp_server = configurable.smtp_server or "smtp.gmail.com"
    smtp_port = configurable.smtp_port or 587

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        if configurable.smtp_username and configurable.smtp_password:
            server.login(configurable.smtp_username, configurable.smtp_password)
        server.sendmail(from_email, [to_email], msg.as_string())

    return {"email_sent": True}


def send_to_discord(state: SummaryState, config: RunnableConfig):
    """Post the final summary to a Discord channel via webhook."""
    send_discord_message(state.running_summary)
    return {"discord_sent": True}


def route_research(
    state: SummaryState, config: RunnableConfig
) -> Literal["finalize_summary", "web_research"]:
    """Route the research based on the follow-up query"""

    configurable = Configuration.from_runnable_config(config)
    if state.research_loop_count <= configurable.max_web_research_loops:
        return "web_research"
    else:
        return "finalize_summary"


def recall_memory(state: SummaryState, config: RunnableConfig):
    """Fetch relevant past chunks from Pinecone memory."""
    cfg = Configuration.from_runnable_config(config)
    recalls = semantic_recall(state.search_query, top_k=5, config=cfg)
    state.memory = recalls
    return {"memory": state.memory}




# Add nodes and edges
builder = StateGraph(
    SummaryState,
    input=SummaryStateInput,
    output=SummaryStateOutput,
    config_schema=Configuration,
)

builder.add_node("generate_query", generate_query)
builder.add_node("recall_memory", recall_memory)
builder.add_node("web_research", web_research)
builder.add_node("youtube_research", youtube_research)  # new node for YouTube research
builder.add_node("wikipedia_research", wikipedia_research)
builder.add_node("arxiv_research", arxiv_research)
builder.add_node("summarize_sources", summarize_sources)
builder.add_node("reflect_on_summary", reflect_on_summary)
builder.add_node("finalize_summary", finalize_summary)
builder.add_node("send_email", send_email)
builder.add_node("send_to_discord", send_to_discord)

# Add edges
builder.add_edge(START, "generate_query")
builder.add_edge("generate_query", "recall_memory")
builder.add_edge("recall_memory", "web_research")
builder.add_edge("web_research", "youtube_research")  # route to YouTube research after web research
builder.add_edge("youtube_research", "wikipedia_research")
builder.add_edge("wikipedia_research", "arxiv_research")
builder.add_edge("arxiv_research", "summarize_sources")
builder.add_edge("summarize_sources", "reflect_on_summary")
builder.add_conditional_edges("reflect_on_summary", route_research)
builder.add_edge("finalize_summary", "send_email")
builder.add_edge("send_email", "send_to_discord")
builder.add_edge("send_to_discord", END)

graph = builder.compile()