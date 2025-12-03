<!--
path: CONTRIBUTING.md
component_id: contributing_guide
kind: doc
area: meta
status: stable
authority_level: 3
version: 2.0.0
license: Apache-2.0
purpose: Contribution guidelines for maintainers and external collaborators.
-->

# **Contributing to PLD**

Thank you for your interest in contributing to Phase Loop Dynamics (PLD).  
Whether you're improving runtime behavior, adding documentation, or experimenting with new repair strategies — contributions are welcome.  
PLD is early-stage and evolving, so the goal is clarity, collaboration, and shared learning — not perfection.

## **🧭 Before You Start**

PLD is used across research, experimental runtimes, and applied systems.  
To keep things understandable as it grows, we rely on:

* clear structure  
* traceable changes  
* consistent metadata

Please skim the following (not required to memorize):

| Topic | File |
| :---- | :---- |
| Repo structure overview | SUMMARY.md |
| Component metadata format | meta/METADATA\_MANIFEST\_SPEC.md |
| Manifest example | meta/manifest.example.yaml |
| Roadmap (where the project is heading) | meta/ROADMAP.md |

## **🧩 Metadata & Manifest Rules**

We have two tiers of contribution complexity:

### **🟢 Fast Track (Docs, Examples, Pitch, Analytics)**
For contributions to `docs/`, `examples/`, `pitch/`, or `analytics/`:
* **No manifest update required.** (These folders are automatically tracked).
* **No metadata headers required** inside the files (optional).
* Just add your files and submit a PR.

### **🔴 Core Track (Runtime Code, Governance)**
For contributions to `pld_runtime/` or `meta/` (Level 4-5):
* **Manifest Update Required:** You MUST add a specific entry to `manifest.yaml`.
* **Metadata Headers Required:** Python files must include `# component_id: ...` headers.
* **Strict Validation:** Changes must pass `python validate_manifest.py --level L2`.

### **How to validate**

Run the included validator to check integrity:

    python validate_manifest.py

Optional stricter mode (Required for Core Runtime code):

    python validate_manifest.py --level L2

Metadata is not bureaucracy — it’s how we keep the system explorable and maintainable.

## **🧪 Code Contributions**

If your work touches runtime code (especially Python files):

1. **Follow Naming Patterns:** Use snake_case and explicit function intent.
2. **Add Metadata Headers (Crucial):**
   To pass L2 validation, Python files (.py) MUST include a metadata block in the first 50 lines matching the manifest entry.

   ```python
   # component_id: my_new_detector
   # status: experimental
   # authority_level: 5

3. **Label Experimental Logic:** Use `status: experimental` in metadata.  
4. **Prioritize Clarity:** PLD is meant to be studied and adapted.

If relevant, include a minimal runnable example under:

quickstart/

Examples help others understand the intent behind behavior.

## **📚 Documentation Contributions**

Documentation, diagrams, and conceptual clarifications are valued equally to code.

Guidelines:

* Keep tone exploratory, not absolute  
* Note uncertainty when applicable  
* Attribute sources, references, or field observations when relevant

Documentation lives under:

docs/

## **🔁 Pull Request Process**

1. Fork the repository (or branch if contributor access is granted)
2. Make changes in small, intentional commits
3. **Check Metadata Requirements:**
   * If touching `pld_runtime/`: Update `manifest.yaml` and add headers.
   * If touching `docs/` or `examples/`: **Skip this step.**
4. Run validation (`python validate_manifest.py`)
5. Submit PR with a short summary explaining **"why"**, not just "what changed".

## **🤝 Collaboration Philosophy**

PLD is not a finished product — it’s a shared exploration of how to govern multi-turn agents.  
That means contributions are evaluated based on:

* clarity of intent  
* usefulness to others  
* alignment with the runtime model  
* operational implications (when known)

"Document reality — don’t legislate ahead of it."

If you're unsure whether something belongs here, small experiments and drafts are welcome.  
We iterate together.

## **📩 Questions & Discussion**

If you're considering a larger contribution or want guidance, open a:

* **Discussion** (best for ideas)  
* **Issue** (best for concrete problems)  
* **Draft PR** (best for work-in-progress)

Thank you again for helping shape the future of PLD.

— Maintainer: **Kiyoshi Sasano**
