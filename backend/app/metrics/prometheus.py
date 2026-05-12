from prometheus_client import Counter, Histogram

reviews_total = Counter(
    "pr_reviews_total",
    "Total PR reviews by status",
    ["status"],
)

review_latency_ms = Histogram(
    "pr_review_latency_ms",
    "End-to-end review latency in milliseconds",
    buckets=[500, 1000, 2000, 5000, 10000, 30000, 60000],
)

tokens_used_total = Counter(
    "pr_tokens_total",
    "OpenAI tokens consumed",
    ["type"],  # input | output
)

cost_usd_total = Counter(
    "pr_cost_usd_total",
    "Total USD spent on LLM calls",
)

issues_found_total = Counter(
    "pr_issues_total",
    "Issues found in reviews",
    ["category", "severity"],
)

rag_chunks_indexed_total = Counter(
    "rag_chunks_indexed_total",
    "Total code chunks indexed into pgvector",
)
