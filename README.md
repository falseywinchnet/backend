# File Manager backend

The Go search engine and Rust Orchestrator share this repository and a tested
native bundle. Their language builds, executable boundaries, contracts and
capability gates remain separate. Frontend changes do not rebuild this repository.

Run `python3 tools/build_bundle.py --jobs 4` with Go, Rust, Clang, CMake and Ninja
installed. It runs Go tests/vet and Rust format/tests/Clippy before producing a
platform archive with both executables, source revision and SHA-256 manifest.
It does not install, launch or assign a filesystem root to either service.

The canonical cross-project registry remains
`orchestrator/spec/CONTRACT_REGISTRY.md`. Parent planning and decisions were
preserved as migration context; their historical sibling paths are not new
runtime dependencies. The owner approved this repository extraction on
2026-10-07. Source history was filtered from `falseywinchnet/file_manager` at
`0dc39f989f2d077d5485027dba9046f884e43bc7`, retaining both component paths.

First-party authored changes follow `planning/PROGRAMMING_HOUSE_STYLE.md`.
Component-local `AGENTS.md` instructions still govern component implementation.
