import operator
from dataclasses import dataclass, field
from typing_extensions import TypedDict, Annotated


@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None)  # Report topic
    search_query: str = field(default=None)  # Search query
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    youtube_research_results: list = field(default_factory=list)  # New field for YouTube results
    wikipedia_research_results: list = field(default_factory=list)
    arxiv_research_results: list = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)  # Research loop count
    running_summary: str = field(default=None)  # Final report
    memory: list = field(default_factory=list)  # retrieved embeddings
    timings: dict = field(default_factory=dict)  # record duration per step and total


@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None)  # Report topic


@dataclass(kw_only=True)
class SummaryStateOutput:
    running_summary: str = field(default=None)  # Final report
    timings: dict = field(default_factory=dict)  # Per-step and total durations in seconds