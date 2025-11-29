<!--
path: meta/METADATA_MANIFEST_SPEC.md
component_id: manifest_spec
kind: doc
area: meta
status: candidate
authority_level: 4
version: 0.9.1
license: CC-BY-4.0
purpose: Governing specification for PLD metadata.
-->

# **Metadata Manifest Specification — v0.9.1**

Status: Candidate Specification  
SPDX-License-Identifier: CC-BY-4.0

This specification defines the unified metadata format for the **Phase Loop Dynamics (PLD) Repository**.

## **🎯 Design Philosophy**

* **Centralized Discovery:** A root manifest.yaml acts as the primary inventory.  
* **Distributed Option:** Sub-directories (e.g., field/) may have their own manifests for external collaboration.  
* **Co-location:** Metadata stays with the code (via headers) or near the code (via manifest).

## **📍 File Locations**

1. **Root Manifest:** ./manifest.yaml (Required)  
2. **Sub Manifests:** path/to/folder/manifest.yaml (Optional, for isolated domains)

Path Resolution Rule:  
All paths in a manifest are relative to the directory containing that manifest.

## **🧩 Manifest Structure**

version: 0.9.1  
default\_license: Apache-2.0  
components:  
  \- path: pld\_runtime/03\_detection/drift\_detector.py  
    component\_id: drift\_detector  
    kind: runtime\_module  
    area: detection  
    status: experimental  
    authority\_level: 5  
    purpose: ...

## **📖 Controlled Vocabulary**

### **kind**

|

| Type | Description |  
| code | General source code |  
| runtime\_module | Core PLD logic (detectors, controllers) |  
| schema | Data definitions (JSON, YAML) |  
| config | Configuration files |  
| metric | Datasets, logs, or evaluation metrics |  
| doc | Documentation |  
| example | Demos and samples |

### **status**

| Status | Meaning |  
| experimental | Active development, unstable. |  
| draft | Work in progress (docs/specs). |  
| candidate | Review pending, feature complete. |  
| stable | Production-ready, breaking changes restricted. |

### **authority\_level (1–5)**

| Level | Scope | Governance |  
| 1 | Open / Local | Free to change. (e.g., local experiments, field notes) |  
| 2 | Collaborative | Shared resources. Change with lightweight review. |  
| 3 | Standard | Established patterns. Change requires rationale. |  
| 4 | Governed | Architecture/Spec. Change requires maintainer alignment. |  
| 5 | Critical | Core Runtime/Safety. Strict change control. |

## **🔗 Code Header Standard (L2 Validation)**

For Python (.py) files, metadata MUST appear in the **first 50 lines** using strict \# key: value syntax.

\# component\_id: repair\_detector  
\# status: experimental  
\# authority\_level: 5

**Maintainer:** Kiyoshi Sasano | **Version:** 0.9.1

---

## 📩 Feedback & Contributions

This specification is a candidate. Feedback from integrators, researchers, and runtime implementers is encouraged.

Submit feedback via issues or discussion threads.

> *“Specifications should reflect reality, not precede it.”*

---

**Maintainer:** Kiyoshi Sasano
Copyright © 2025
