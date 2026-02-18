"""Shared fixtures for dashboard tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_frontmatter():
    """Return a sample markdown document with frontmatter."""
    return """\
---
title: Test Plan
status: active
created: 2025-01-15
tags: [infra, networking]
phases:
  - id: 1
    title: Setup
    status: complete
    doc: 01-Setup.md
  - id: 2
    title: Implementation
    status: in-progress
    doc: 02-Implementation.md
    depends_on: [1]
---

This is the plan overview.

Some more content here.
"""


@pytest.fixture
def plan_dir(tmp_path):
    """Create a minimal plan directory structure."""
    plan = tmp_path / "Plans" / "TestPlan"
    plan.mkdir(parents=True)

    (plan / "README.md").write_text("""\
---
title: Test Plan
status: active
created: 2025-01-15
tags: [infra]
phases:
  - id: 1
    title: Setup
    status: complete
    doc: 01-Setup.md
  - id: 2
    title: Build
    status: in-progress
    doc: 02-Build.md
    depends_on: [1]
---

Overview of the test plan.
""")

    (plan / "01-Setup.md").write_text("""\
---
deliverable: Environment ready
tasks:
  - id: "1.1"
    title: Install deps
    status: complete
  - id: "1.2"
    title: Configure env
    status: complete
---

## 1.1: Install deps

- [x] Install Python
- [x] Install Node

## 1.2: Configure env

- [x] Set up .env
- [x] Configure DB
""")

    (plan / "02-Build.md").write_text("""\
---
deliverable: Core module built
tasks:
  - id: "2.1"
    title: Write core
    status: in-progress
    depends_on: ["1.2"]
  - id: "2.2"
    title: Write tests
    status: planned
    depends_on: ["2.1"]
---

## 2.1: Write core

- [x] Create module structure
- [ ] Implement main logic
- [ ] Add error handling

## 2.2: Write tests

- [ ] Unit tests
- [ ] Integration tests
""")

    return tmp_path


@pytest.fixture
def artifacts_dir(tmp_path):
    """Create a directory with various artifact types."""
    # Research (flat layout)
    research = tmp_path / "Research"
    research.mkdir()
    (research / "caching.md").write_text("""\
---
title: Caching Strategies
type: research
status: active
created: 2025-01-10
tags: [performance, caching]
---

Research into various caching strategies for the application.
""")

    # Specs (subdirectory layout)
    specs = tmp_path / "Specs"
    specs.mkdir()
    auth = specs / "Authentication"
    auth.mkdir()
    (auth / "README.md").write_text("""\
---
title: Authentication Spec
type: spec
status: approved
created: 2025-01-12
tags: [auth, security]
---

Authentication specification details.
""")

    # Retro
    retro = tmp_path / "Retro"
    retro.mkdir()
    (retro / "2025-01-20-sprint-1.md").write_text("""\
---
title: Sprint 1 Retro
type: retro
status: complete
created: 2025-01-20
tags: [sprint-1]
---

What went well, what didn't.
""")

    return tmp_path


@pytest.fixture
def planning_root(plan_dir):
    """Create a full planning root with plans, artifacts, and config."""
    root = plan_dir  # Already has Plans/TestPlan/

    # Research (flat layout)
    research = root / "Research"
    research.mkdir()
    (research / "caching.md").write_text("""\
---
title: Caching Strategies
type: research
status: active
created: 2025-01-10
tags: [performance, caching]
---

Research into various caching strategies for the application.
""")

    # Specs (subdirectory layout)
    specs = root / "Specs"
    specs.mkdir()
    auth = specs / "Authentication"
    auth.mkdir()
    (auth / "README.md").write_text("""\
---
title: Authentication Spec
type: spec
status: approved
created: 2025-01-12
tags: [auth, security]
---

Authentication specification details.
""")

    # Retro
    retro = root / "Retro"
    retro.mkdir()
    (retro / "2025-01-20-sprint-1.md").write_text("""\
---
title: Sprint 1 Retro
type: retro
status: complete
created: 2025-01-20
tags: [sprint-1]
---

What went well, what didn't.
""")

    # Add config
    import json
    (root / "planning-config.json").write_text(json.dumps({
        "title": "Test Project",
        "description": "A test project for testing",
        "repositories": {
            "main-repo": {"github": "user/main-repo"}
        },
        "planMapping": {
            "TestPlan": {"repo": "main-repo"}
        },
        "planRepository": "main-repo"
    }))

    return root
