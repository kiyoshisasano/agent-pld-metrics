# **Versioning Policy**

Applies to: PLD repository (code, schema, documentation, and examples)  
Version: 2.0  
Status: Working Draft  
Last Updated: 2025-11  
This document defines how versions are applied, incremented, and interpreted across the PLD repository.  
It is intended to provide consistency as the project evolves and to support future collaboration.  
This policy governs modification of Level 1, Level 2, and Level 3 specification assets and ensures alignment across schema, taxonomy, event semantics, runtime enforcement, and metrics artifacts.

## **1\. Overview**

The PLD project uses **Semantic Versioning (SemVer)** as a guiding model:

MAJOR.MINOR.PATCH

However, because the project is still in an exploratory and refinement stage, versioning rules are applied pragmatically.

* **MAJOR versions** represent conceptual shifts or structural specification changes  
* **MINOR versions** introduce new capabilities or refinements that do not require rework  
* **PATCH versions** capture editorial, formatting, or clarity improvements that do not affect interpretation

## **2\. Scope of Versioning**

Versioning applies across multiple layers of the repository.  
These layers may evolve at different paces, but must remain consistent with one another.

| Layer | Versioned? | Current Ref | Notes |
| :---- | :---- | :---- | :---- |
| PLD Event Schema (schema\_version) | Yes | v2.x | Used for runtime validation |
| Metadata Manifest Spec | Yes | v0.9.x | Defines manifest.yaml structure |
| Repository version (meta) | Yes | v2.0 | Describes documentation and project evolution |
| Examples & quickstart materials | Yes (implicit) | \- | Follow current normative baseline |
| Experimental files (archive/, research/) | No | \- | Optional and non-binding |

## **3\. Relationship Between Repository Version and Schema Version**

Although the repository uses SemVer, event payloads in runtime logs reference a **schema version**, which follows a related but independent lifecycle.

| Case | Expected Behavior |
| :---- | :---- |
| Repository version increases | Schema version MAY or MAY NOT change |
| Schema version increases | Repository version SHOULD reflect the change |

schema\_version: "2.x"

Where:

* The **major number MUST match** the expected validation rules.  
* Minor schema releases SHOULD be forward-compatible within the same major version.

## **4\. Compatibility Rules**

Implementations SHOULD interpret versions as follows:

| Version Change Type | Interpretation | Impact |
| :---- | :---- | :---- |
| PATCH | Editorial or clarity improvement | No action required |
| MINOR | New examples, wording improvements, expanded rules | Optional adoption |
| MAJOR | Specification or schema shift | Migration recommended |

Runtime validation systems MUST treat schema compatibility differently from repository documentation compatibility.

## **5\. Runtime Validation and Version Acceptance**

A runtime validator:

* MUST reject events where the schema major version differs from the expected value  
* SHOULD accept minor schema revisions within the same major version  
* MAY allow forward compatibility if validation mode permits

Examples:

| schema\_version value | Acceptance |
| :---- | :---- |
| 2.0 | ✅ Accept |
| 2.1 | ✅ Accept (forward compatible) |
| 1.9 | ❌ Reject (different major version) |
| 3.0 | ❌ Reject (different major version) |

Validation modes (strict / warn / normalize) influence how version mismatches are handled.

## **6\. When to Increment Versions**

| Change Type | Example | Required Increment |
| :---- | :---- | :---- |
| Structural schema change | modifying required fields | MAJOR |
| Manifest Spec change | adding required fields to manifest.yaml | MINOR |
| New schema rule or enforcement | new lifecycle mapping expectation | MINOR |
| Updated examples | revised event JSON examples | MINOR |
| Clarification or wording refinement | rephrased definitions or grammar | PATCH |

## **6.1 Rules for Metrics, Taxonomy, and Event Matrix Alignment (Added in v2.0 Non-Breaking Update)**

To maintain consistency across the PLD ecosystem:

* Updates involving the Metrics Specification, Metrics Schema, or Traceability Mapping  
  MUST NOT require a version increment unless they alter normative behavior.  
* Alignment changes such as:  
  * consolidating terminology  
  * documenting numeric classifier policy  
  * updating Traceability Maps  
  * clarifying how provisional and pending taxonomy codes are handled  
    count as MINOR changes unless they affect runtime enforcement.

Hybrid Compliance Model Rules:

| Asset | Eligibility Condition Role | Version Impact |
| :---- | :---- | :---- |
| Event Matrix | MUST enforce semantics | MAY trigger MINOR or MAJOR depending on scope |
| Taxonomy Code Prefixes | SHOULD inform grouping | PATCH or MINOR only |
| Numeric Classifier (D1–D5, R-series, etc.) | MAY support segmentation | Never MAJOR (non-binding) |
| Traceability Map | Documentation alignment | PATCH unless behavior changes |

## **7\. Deprecation Process (Early Stage Policy)**

As the project matures, certain schemas, field names, or lifecycle codes may become deprecated.

Deprecation SHOULD follow these phases:

1. **Documented Notice** (non-breaking)  
2. **Marked as Deprecated in Schema**  
3. **Removal in next MAJOR version**

Deprecations SHOULD be recorded in the CHANGELOG.

## **8\. Future Policy Stabilization**

This versioning policy is **not final**.

As the project grows, particularly if external contributors or organizations adopt PLD, this document may evolve into:

* A formal governance model  
* An RFC-based change process  
* A multi-repository ecosystem versioning policy

Such changes will be introduced as MINOR updates unless structural governance changes require a MAJOR revision.

## **9\. Feedback**

Feedback on versioning policy is welcome and encouraged.

Until a formal RFC process exists, proposed changes MAY be submitted via:

* GitHub Issues (planned)  
* Discussion threads (planned)

Maintainer: **Kiyoshi Sasano**
