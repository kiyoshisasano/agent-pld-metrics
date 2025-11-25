# Contributing to PLD

Thank you for your interest in contributing to **Phase Loop Dynamics (PLD)**.
Whether you're improving runtime behavior, adding documentation, or experimenting with new repair strategies — contributions are welcome.

PLD is early-stage and evolving, so the goal is clarity, collaboration, and shared learning — not perfection.

---

## 🧭 Before You Start

PLD is used across research, experimental runtimes, and applied systems.
To keep things understandable as it grows, we rely on:

* clear structure
* traceable changes
* consistent metadata

Please skim the following (not required to memorize):

| Topic                                  | File                             |
| -------------------------------------- | -------------------------------- |
| Repo structure overview                | `SUMMARY.md`                     |
| Component metadata format              | `meta/METADATA_MANIFEST_SPEC.md` |
| Manifest example                       | `meta/manifest.example.yaml`     |
| Roadmap (where the project is heading) | `ROADMAP.md`                     |

---

## 🧩 Metadata & Manifest

If your contribution adds or modifies:

* runtime modules
* schemas or evaluation assets
* examples or integration recipes
* documentation that describes behavior or concepts

➡️ **Please update `manifest.yaml`.**

### How to validate

Run the included validator:

```bash
python validate_manifest.py
```

Optional stricter mode:

```bash
python validate_manifest.py --level L2
```

Metadata is not bureaucracy — it’s how we keep the system explorable and maintainable.

---

## 🧪 Code Contributions

If your work touches runtime code:

* Follow existing naming patterns (`snake_case`, explicit function intent)
* Keep experimental logic labeled (`status: experimental` in metadata)
* Prefer clarity over cleverness — PLD is meant to be studied and adapted

If relevant, include a minimal runnable example under:

```
quickstart/
```

Examples help others understand the intent behind behavior.

---

## 📚 Documentation Contributions

Documentation, diagrams, and conceptual clarifications are valued equally to code.

Guidelines:

* Keep tone exploratory, not absolute
* Note uncertainty when applicable
* Attribute sources, references, or field observations when relevant

Documentation lives under:

```
docs/
```

---

## 🔁 Pull Request Process

1. Fork the repository (or branch if contributor access is granted)
2. Make changes in small, intentional commits
3. Update `manifest.yaml` if needed
4. Run validation
5. Submit PR with a short summary explaining **"why"**, not just "what changed".

We prefer pull requests that:

* solve one problem at a time
* come with examples or context
* align with the roadmap — or propose extensions

---

## 🤝 Collaboration Philosophy

PLD is not a finished product — it’s a shared exploration of how to govern multi-turn agents.
That means contributions are evaluated based on:

* clarity of intent
* usefulness to others
* alignment with the runtime model
* operational implications (when known)

> "Document reality — don’t legislate ahead of it."

If you're unsure whether something belongs here, small experiments and drafts are welcome.
We iterate together.

---

## 📩 Questions & Discussion

If you're considering a larger contribution or want guidance, open a:

* **Discussion** (best for ideas)
* **Issue** (best for concrete problems)
* **Draft PR** (best for work-in-progress)

---

Thank you again for helping shape the future of PLD.

— Maintainer: **Kiyoshi Sasano**
