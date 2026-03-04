# Semantic Cache Behavior Evaluation

> **Status:** Experimental / Lab
> **Scope:** Observational study of semantic caching behavior in RAG systems
> **PLD Relevance:** Potential drift sources during retrieval and response reuse
> **Normative Status:** Non-normative (exploratory lab note)

This lab explores a potential failure mode in **semantic caching systems** used in retrieval-augmented generation (RAG): cached responses may propagate across different user intents when semantic similarity thresholds allow reuse.

The experiment evaluates whether such propagation occurs under typical configurations and examines how semantic caching interacts with **PLD Drift detection**.

This document is **exploratory** and **does not introduce new PLD lifecycle phases, taxonomy codes, or schema elements**.

---

# Relevance to PLD

PLD identifies **drift** as deviations from the intended conversational trajectory, typically observed through D-family taxonomy signals.

Semantic caching introduces an additional system state:

query → embedding → cache lookup → cached response

Under certain conditions, cached responses may propagate interpretations created during earlier queries.

Such behavior may produce **effects consistent with drift-like behavior**, particularly when:

* queries are semantically adjacent but differ in intent
* the original cached answer contains interpretive assumptions
* similarity thresholds permit reuse beyond strict paraphrases

Understanding these conditions helps clarify **when drift signals might originate from cache behavior rather than model reasoning**.

---

# Background

Semantic caching systems store responses keyed by **query embeddings**.

When a new query's embedding is sufficiently similar to a cached entry, the cached response may be returned without invoking the LLM.

While this improves latency and cost, it introduces a potential risk:

> If an ambiguous query seeds the cache with an interpretive response,
> subsequent queries may inherit that interpretation even when their intent differs.

This experiment evaluates whether such **cross-intent reuse** occurs under practical configurations.

---

# Experimental Context

| Attribute          | Description                                        |
| ------------------ | -------------------------------------------------- |
| Application domain | Local help-assistant scenario                      |
| Architecture       | Retrieval-augmented generation with semantic cache |
| Cache type         | Embedding-based semantic cache                     |
| LLM backend        | LLM response generation                            |
| Embedding model    | Sentence embedding model                           |
| Cache threshold    | Similarity-based reuse trigger                     |

The cache operates before the LLM invocation stage.

---

# Evaluation Scope

The evaluation probes several query categories designed to test cache reuse boundaries.

| Category                    | Description                                 |
| --------------------------- | ------------------------------------------- |
| Same-intent paraphrases     | Sanity validation                           |
| Neighboring intents         | Semantically adjacent queries               |
| Same domain, different task | Overlapping topic but distinct intent       |
| Ambiguous queries           | Mixed-intent phrasing                       |
| Adversarial probes          | Queries designed to induce unintended reuse |

---

# Primary Criterion

**Cross-intent reuse**

A cross-intent reuse event is defined as:

1. A **cache hit** occurs
2. The **intended task differs** from the seed query
3. The **returned answer matches the cached response**

Such behavior could represent a potential **system-level drift source**.

---

# Key Findings

## Safety Behavior

| Observation        | Result                                    |
| ------------------ | ----------------------------------------- |
| Cross-intent reuse | **Not observed**                          |
| Cache hits         | Limited to paraphrases of the same intent |
| Adversarial probes | Did not trigger unintended reuse          |

Within the tested configuration, the semantic cache behaved as a **conservative reuse mechanism**.

Cache reuse remained bounded to closely related paraphrases.

---

# Operational Impact

| Metric         | Without Cache | With Cache | Improvement    |
| -------------- | ------------- | ---------- | -------------- |
| Median latency | ~3,200 ms     | ~200 ms    | ≈16× faster    |
| LLM calls      | 100%          | 40%        | ≈60% reduction |
| Cache hit rate | —             | ~60%       | —              |

See: `benchmark_visual.svg`

---

# Interpretation for PLD

## When Drift Risk Appears Low

Under the tested conditions:

* cache reuse remained within paraphrase boundaries
* no cross-intent propagation occurred
* adversarial prompts did not trigger reuse

This suggests that **semantic caching does not inherently introduce drift** when thresholds and embeddings are conservative.

---

## When Drift Risk May Increase

Exploratory observations suggest risk may increase when:

* retrieval confidence is low
* query intent is ambiguous
* similarity thresholds are permissive
* cached responses encode interpretive assumptions

In such cases, cache state may influence later responses.

---

# Implications for PLD Observability

PLD systems monitoring RAG pipelines may benefit from including **cache context** in observability signals, such as:

* cache hit / miss
* similarity score
* seed query identifier
* reuse distance between queries

These signals may help distinguish between:

model-generated drift
vs
cache-propagated responses

---

# Limitations

* Evaluation scope is limited to a bounded domain
* Results depend on similarity threshold and embedding configuration
* Not a formal safety proof

Further experiments may explore:

* different embedding models
* higher similarity thresholds
* larger query diversity

---

# Files

| File                   | Description                          |
| ---------------------- | ------------------------------------ |
| `README.md`            | Experimental description             |
| `benchmark_visual.svg` | Visual summary of operational impact |

---

# References

PLD Drift Detection
`/docs/concepts/operator_primitives/01_detect_drift.md`

PLD Taxonomy
`/docs/specifications/level_3_standards/PLD_taxonomy_v2.0.md`

---

### Notes on PLD Alignment

* Avoids introducing new taxonomy codes or lifecycle phases.
* Treats cache behavior as a potential **source of drift-like behavior** rather than defining a new drift category.
* Explicitly marked as **non-normative experimental documentation** within the labs layer.
