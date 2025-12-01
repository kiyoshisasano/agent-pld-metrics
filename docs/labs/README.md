# PLD Labs — Experimental Specifications

This directory contains **research proposals, early-stage ideas, and unfinalized extensions** to the Phase Loop Dynamics (PLD) framework.

Files stored here are **NOT part of the official specification** and:

* MAY be revised significantly
* MAY be adopted into the formal specification after review
* MAY be deprecated or removed if they fail evaluation

---

## Purpose of This Folder

PLD Labs exists to:

* Capture emerging design questions before they are ready for standards
* Provide a workspace for evaluating extensions without polluting the core specification
* Support experimentation, prototyping, and feedback cycles
* Preserve conceptual lineage and governance traceability

---

## Status Classification

Each document should declare one of the following labels at the top:

| Status       | Meaning                                            |
| ------------ | -------------------------------------------------- |
| **Draft**    | Initial idea; unstable, under exploration          |
| **Proposal** | Candidate concept under structured review          |
| **RFC**      | Formal request for adoption into the specification |
| **Rejected** | Explored but not adopted (kept for traceability)   |

---

## Usage Guidelines

* Do **NOT reference Labs content in production implementations.
* Do **NOT merge Labs content into the `specifications/` hierarchy without governance approval.
* DO reference Labs files during research, prototyping, or evaluation.

---

## When a Labs File Graduates

A Labs document may move into the main documentation structure when it meets:

* Proven runtime validity
* Semantic alignment with existing taxonomy and loop logic
* Repeatable evaluation results
* Governance approval

Graduated files should include a changelog entry and redirect note.

---

**Maintainer Note:** Labs content is welcome to evolve. Treat this folder as PLD's research sandbox.
