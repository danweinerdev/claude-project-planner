"""Main orchestration for dashboard generation."""

import shutil
from pathlib import Path

from .config import load_config, apply_config_to_plans
from .css import CSS
from .models import Artifact
from .parsing import parse_plan, scan_artifacts
from .progress import plan_progress, overall_plan_status
from .pages import (
    generate_index,
    generate_plan_page,
    generate_phase_page,
    generate_knowledge_page,
    generate_retros_page,
    generate_artifact_list_page,
    generate_artifact_detail_page,
)


def main(planning_root: Path = None):
    if planning_root is None:
        planning_root = Path(__file__).parent.parent

    plans_dir = planning_root / "Plans"
    output_dir = planning_root / "Dashboard"

    if not plans_dir.exists():
        print("No Plans/ directory found — creating empty dashboard.")
        plans_dir.mkdir(exist_ok=True)

    # Load configuration (planning-config.json, with dashboard-config.json fallback)
    config_path = planning_root / "planning-config.json"
    if not config_path.exists():
        config_path = planning_root / "dashboard-config.json"
    config = load_config(config_path)

    # Check if dashboard generation is disabled
    if config.get("dashboard") is False:
        print("Dashboard generation is disabled (dashboard: false in config)")
        return

    # Load local config (for repo paths, not committed)
    local_config_path = planning_root / "planning-config.local.json"
    if local_config_path.exists():
        local_config = load_config(local_config_path)
        for repo_key, repo_data in local_config.get("repositories", {}).items():
            if repo_key in config.get("repositories", {}):
                config["repositories"][repo_key].update(repo_data)
            else:
                config.setdefault("repositories", {})[repo_key] = repo_data

    if config.get("repositories"):
        print(f"Loaded config with {len(config['repositories'])} repositories")

    # Clean and recreate output
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Write CSS
    (output_dir / "styles.css").write_text(CSS)

    # Parse all plans
    plans = []
    for plan_path in sorted(plans_dir.iterdir()):
        if plan_path.is_dir():
            plan = parse_plan(plan_path)
            if plan:
                plans.append(plan)

    print(f"Parsed {len(plans)} plans")

    # Apply config to plans (target repos, etc.)
    apply_config_to_plans(plans, config)

    # Parse all artifact types
    all_artifacts: dict[str, list[Artifact]] = {}
    for category in ("Research", "Brainstorm", "Specs", "Designs", "Retro"):
        items = scan_artifacts(planning_root, category)
        if items:
            all_artifacts[category] = items
            print(f"  {category}: {len(items)} artifacts")

    # Generate index
    (output_dir / "index.html").write_text(
        generate_index(plans, config, all_artifacts))

    total_pages = 1

    # Generate plan + phase pages
    for plan in plans:
        plan_out = output_dir / plan.slug
        plan_out.mkdir(parents=True, exist_ok=True)

        (plan_out / "index.html").write_text(generate_plan_page(plan, config))
        total_pages += 1

        for phase in plan.phases:
            (plan_out / f"{phase.slug}.html").write_text(
                generate_phase_page(plan, phase, config))
            total_pages += 1

        pc, _, pt = plan_progress(plan)
        status = overall_plan_status(plan)
        print(f"  {plan.name}: {status} ({pc}/{pt} phases)")

    # Generate knowledge base page (research + brainstorm)
    research = all_artifacts.get("Research", [])
    brainstorm = all_artifacts.get("Brainstorm", [])
    if research or brainstorm:
        (output_dir / "knowledge.html").write_text(
            generate_knowledge_page(research, brainstorm, config))
        total_pages += 1

        # Detail pages
        knowledge_dir = output_dir / "knowledge"
        knowledge_dir.mkdir(exist_ok=True)
        for art in research + brainstorm:
            (knowledge_dir / f"{art.slug}.html").write_text(
                generate_artifact_detail_page(art, "Knowledge", "knowledge.html", config))
            total_pages += 1

    # Generate specs pages
    specs = all_artifacts.get("Specs", [])
    if specs:
        (output_dir / "specs.html").write_text(
            generate_artifact_list_page(specs, "Specs", "Feature specifications", config))
        total_pages += 1
        specs_dir = output_dir / "specs"
        specs_dir.mkdir(exist_ok=True)
        for art in specs:
            (specs_dir / f"{art.slug}.html").write_text(
                generate_artifact_detail_page(art, "Specs", "specs.html", config))
            total_pages += 1

    # Generate designs pages
    designs = all_artifacts.get("Designs", [])
    if designs:
        (output_dir / "designs.html").write_text(
            generate_artifact_list_page(designs, "Designs", "Technical architecture documents", config))
        total_pages += 1
        designs_dir = output_dir / "designs"
        designs_dir.mkdir(exist_ok=True)
        for art in designs:
            (designs_dir / f"{art.slug}.html").write_text(
                generate_artifact_detail_page(art, "Designs", "designs.html", config))
            total_pages += 1

    # Generate retros pages
    retros = all_artifacts.get("Retro", [])
    if retros:
        (output_dir / "retros.html").write_text(
            generate_retros_page(retros, config))
        total_pages += 1
        retros_dir = output_dir / "retros"
        retros_dir.mkdir(exist_ok=True)
        for art in retros:
            (retros_dir / f"{art.slug}.html").write_text(
                generate_artifact_detail_page(art, "Retros", "retros.html", config))
            total_pages += 1

    print(f"\nGenerated {total_pages} pages in {output_dir}/")
