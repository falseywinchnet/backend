# Backend repository

This repository owns the Rust Orchestrator and Go search engine together.
Read the applicable component AGENTS.md, `planning/PROGRAMMING_HOUSE_STYLE.md`,
and `orchestrator/spec/CONTRACT_REGISTRY.md` before implementation.
The repository extraction changes build ownership, not protocol or capability
semantics. Keep component test fixtures isolated from user data. Do not create
workers or subagents. Preserve historical evidence and source provenance.
