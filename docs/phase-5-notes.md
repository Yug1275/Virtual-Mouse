# Phase 5 — Robustness & Polish Notes

## What I learned
- logging module replaces print() with leveled, timestamped, filterable output
- try/except/finally guarantees cleanup code runs no matter how the loop exits
- "Fail fast" principle: validate config BEFORE the main loop starts
- Graceful degradation: tolerate occasional bad frames, but give up after
  too many consecutive failures (camera likely disconnected)
- Per-frame try/except prevents one bad frame from crashing the whole app
- Separated run_app() from main() so main() handles only top-level
  setup/teardown and exception routing
- README.md is for USERS; how_it_works.md is for DEVELOPERS — different audiences
- logs/ folder is gitignored, just like venv/ — machine-specific, not source code

## Final architecture principle applied throughout
Every module does ONE thing and has NO knowledge of modules above it
in the pipeline. GestureEngine doesn't know about cameras. MouseController
doesn't know about MediaPipe. This is why each one is independently testable.
q
drag, scroll, FPS display, landmark visualization, configurable sensitivity,
error handling, and documentation.