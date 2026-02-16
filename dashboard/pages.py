"""Page generators for the dashboard."""

import html

from .models import PlanData, PhaseData, Artifact
from .progress import plan_progress, phase_progress, overall_plan_status
from .config import get_planning_repo_url
from .html import status_icon, badge_html, page_html
from .markdown import md_to_html
from .parsing import extract_overview


def generate_index(plans: list[PlanData], config: dict,
                   all_artifacts: dict[str, list[Artifact]] = None) -> str:
    """Main dashboard index page."""
    if all_artifacts is None:
        all_artifacts = {}

    # Sort: in-progress first, then planned, then complete
    order = {"in-progress": 0, "active": 0, "approved": 1, "draft": 1,
             "planned": 1, "complete": 2, "archived": 3, "deferred": 3}
    plans = sorted(plans, key=lambda p: (order.get(overall_plan_status(p), 4), p.name))

    # Aggregate stats
    total_phases = sum(len(p.phases) for p in plans)
    complete_phases = sum(1 for p in plans for ph in p.phases if ph.status == "complete")
    ip_phases = sum(1 for p in plans for ph in p.phases if ph.status == "in-progress")
    planned_phases = total_phases - complete_phases - ip_phases

    # In-progress section
    ip_items = []
    for plan in plans:
        for phase in plan.phases:
            if phase.status == "in-progress":
                tc, tip, tt = phase_progress(phase)
                progress_text = f"{tc}/{tt} tasks" if tt > 0 else ""
                ip_items.append(f'''
                    <a href="{plan.slug}/{phase.slug}.html" class="work-item">
                        <span class="work-plan">{html.escape(plan.title)}</span>
                        <span class="work-phase">Phase {phase.id}: {html.escape(phase.title)}</span>
                        <span class="work-progress">{progress_text}</span>
                    </a>''')

    ip_section = ""
    if ip_items:
        ip_section = f'''
        <section class="in-progress-section card">
            <h2>In Progress</h2>
            <div class="work-list">{''.join(ip_items)}</div>
        </section>'''

    # Plan cards
    cards = []
    for plan in plans:
        status = overall_plan_status(plan)
        pc, pip, pt = plan_progress(plan)

        if pt > 0:
            cpct = (pc / pt) * 100
            ipct = (pip / pt) * 100
            progress = f'''
                <div class="progress-bar">
                    <div class="progress-complete" style="width:{cpct}%"></div>
                    <div class="progress-active" style="width:{ipct}%"></div>
                </div>
                <div class="progress-text">{pc}/{pt} phases complete</div>'''
        else:
            progress = '<div class="progress-text">No phases defined</div>'

        phase_items = []
        for phase in plan.phases[:5]:
            icon = status_icon(phase.status)
            phase_items.append(f'''
                <div class="phase-item">
                    <span class="phase-icon">{icon}</span>
                    <span class="phase-name"><a href="{plan.slug}/{phase.slug}.html">{html.escape(phase.title)}</a></span>
                    <span class="phase-progress-text">{badge_html(phase.status)}</span>
                </div>''')
        if len(plan.phases) > 5:
            phase_items.append(f'<div class="phase-item"><a href="{plan.slug}/">+{len(plan.phases) - 5} more</a></div>')

        phases_html = f'<div class="phase-list">{"".join(phase_items)}</div>' if phase_items else ""

        tags_html = ""
        if plan.tags:
            tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in plan.tags)
            tags_html = f'<div class="tags">{tag_spans}</div>'

        cards.append(f'''
            <div class="plan-card card status-{status}">
                <div class="plan-header">
                    <h3><a href="{plan.slug}/">{html.escape(plan.title)}</a></h3>
                    {badge_html(status)}
                </div>
                {f'<div class="subtitle">{html.escape(plan.overview)}</div>' if plan.overview else ''}
                {tags_html}
                {progress}
                {phases_html}
                <div class="plan-footer">
                    <span>{len(plan.phases)} phases</span>
                    {f'<span>Updated {plan.updated}</span>' if plan.updated else ''}
                </div>
            </div>''')

    desc = html.escape(config.get("description", ""))

    # Navigation links to other sections
    nav_links = []
    research = all_artifacts.get("Research", [])
    brainstorm = all_artifacts.get("Brainstorm", [])
    specs = all_artifacts.get("Specs", [])
    designs = all_artifacts.get("Designs", [])
    retros = all_artifacts.get("Retro", [])

    if research or brainstorm:
        count = len(research) + len(brainstorm)
        nav_links.append(f'<a href="knowledge.html" class="nav-link-card card">Knowledge Base <span class="nav-link-count">{count}</span></a>')
    if specs:
        nav_links.append(f'<a href="specs.html" class="nav-link-card card">Specs <span class="nav-link-count">{len(specs)}</span></a>')
    if designs:
        nav_links.append(f'<a href="designs.html" class="nav-link-card card">Designs <span class="nav-link-count">{len(designs)}</span></a>')
    if retros:
        nav_links.append(f'<a href="retros.html" class="nav-link-card card">Retros <span class="nav-link-count">{len(retros)}</span></a>')

    nav_section = ""
    if nav_links:
        nav_section = f'''
        <section>
            <div class="nav-links">{''.join(nav_links)}</div>
        </section>'''

    # Recent activity
    recent_items = []
    for cat_name, items in all_artifacts.items():
        for art in items:
            if art.updated or art.created:
                date = art.updated or art.created
                recent_items.append((date, art.type, art.title, cat_name))

    for plan in plans:
        if plan.updated or plan.created:
            date = plan.updated or plan.created
            recent_items.append((date, "plan", plan.title, "Plans"))

    recent_items.sort(key=lambda x: x[0], reverse=True)
    recent_section = ""
    if recent_items[:5]:
        recent_rows = []
        for date, atype, title, cat in recent_items[:5]:
            recent_rows.append(f'''
                <div class="phase-item">
                    <span class="phase-icon">{status_icon(atype if atype in ("plan",) else "active")}</span>
                    <span class="phase-name">{html.escape(title)}</span>
                    <span class="tag">{html.escape(atype)}</span>
                    <span class="phase-progress-text">{date}</span>
                </div>''')
        recent_section = f'''
        <section>
            <h2>Recent Activity</h2>
            <div class="card">
                <div class="phase-list">{''.join(recent_rows)}</div>
            </div>
        </section>'''

    body = f'''
    <header>
        <h1>{html.escape(config.get("title", "Project Planner"))}</h1>
        {f'<p class="subtitle">{desc}</p>' if desc else ''}
        <div class="stats">
            <div class="stat stat-complete">
                <span class="stat-value">{complete_phases}</span>
                <span class="stat-label">phases complete</span>
            </div>
            <div class="stat stat-progress">
                <span class="stat-value">{ip_phases}</span>
                <span class="stat-label">in progress</span>
            </div>
            <div class="stat stat-planned">
                <span class="stat-value">{planned_phases}</span>
                <span class="stat-label">planned</span>
            </div>
            <div class="stat">
                <span class="stat-value">{len(plans)}</span>
                <span class="stat-label">plans</span>
            </div>
        </div>
    </header>

    {nav_section}
    {ip_section}

    <section>
        <h2>All Plans</h2>
        <div class="plans-grid">{''.join(cards)}</div>
    </section>

    {recent_section}'''

    return page_html("Dashboard", body, config,
                     [("Dashboard", None)], depth=0)


def generate_plan_page(plan: PlanData, config: dict) -> str:
    """Plan detail page with phase table."""
    status = overall_plan_status(plan)
    pc, pip, pt = plan_progress(plan)

    if pt > 0:
        cpct = (pc / pt) * 100
        progress_html = f'''
            <div class="progress-bar" style="height:10px;margin-bottom:0.5rem">
                <div class="progress-complete" style="width:{cpct}%"></div>
            </div>
            <div class="progress-text" style="font-size:0.875rem">{pc}/{pt} phases complete ({cpct:.0f}%)</div>'''
    else:
        progress_html = ""

    tags_html = ""
    if plan.tags:
        tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in plan.tags)
        tags_html = f'<div class="tags">{tag_spans}</div>'

    # Phase table
    rows = []
    for phase in plan.phases:
        tc, tip, tt = phase_progress(phase)
        checklist = f"{tc}/{tt} tasks" if tt > 0 else ""

        # Subtask rollup
        sub_done = sum(t.subtasks.done for t in phase.tasks)
        sub_total = sum(t.subtasks.total for t in phase.tasks)
        subtask_text = ""
        if sub_total > 0:
            pct = (sub_done / sub_total) * 100
            subtask_text = f'''
                <div class="checklist-bar"><span class="checklist-fill" style="width:{pct}%"></span></div>
                {sub_done}/{sub_total}'''

        deps_text = ", ".join(str(d) for d in phase.depends_on) if phase.depends_on else ""

        rows.append(f'''
            <tr>
                <td>{status_icon(phase.status)}</td>
                <td><a href="{phase.slug}.html">Phase {phase.id}: {html.escape(phase.title)}</a></td>
                <td>{badge_html(phase.status)}</td>
                <td>{checklist}</td>
                <td>{subtask_text}</td>
                <td style="color:var(--text-muted)">{html.escape(phase.deliverable)}</td>
            </tr>''')

    # Repo links
    repo_links_html = ""
    links = []
    planning_repo_url = get_planning_repo_url(config)
    if planning_repo_url:
        readme_path = f"Plans/{plan.name}/README.md"
        links.append(f'<a href="{planning_repo_url}/blob/main/{readme_path}" class="quick-link">&#x1F4C4; Plan Source</a>')
    if plan.target_repo_url:
        repo_name = plan.target_repo.split('/')[-1] if '/' in plan.target_repo else plan.target_repo
        links.append(f'<a href="{plan.target_repo_url}" class="quick-link">&#x1F527; {html.escape(repo_name)} Repository</a>')
    if links:
        repo_links_html = f'<div class="quick-links" style="margin-top:0.75rem">{"".join(links)}</div>'

    body = f'''
    <header>
        <div class="plan-detail-header">
            <h1>{html.escape(plan.title)}</h1>
            {badge_html(status)}
        </div>
        {f'<p class="subtitle">{html.escape(plan.overview)}</p>' if plan.overview else ''}
        {tags_html}
        <div style="margin-top:1rem">{progress_html}</div>
        {repo_links_html}
    </header>

    <section>
        <h2>Phases</h2>
        <div class="card" style="padding:0;overflow:hidden">
            <table class="task-table">
                <thead>
                    <tr>
                        <th style="width:40px"></th>
                        <th>Phase</th>
                        <th style="width:120px">Status</th>
                        <th style="width:100px">Tasks</th>
                        <th style="width:140px">Subtasks</th>
                        <th>Deliverable</th>
                    </tr>
                </thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
    </section>'''

    return page_html(plan.title, body, config,
                     [("Dashboard", "../index.html"), (plan.title, None)], depth=1)


def generate_phase_page(plan: PlanData, phase: PhaseData, config: dict) -> str:
    """Phase detail page with tasks and content."""
    tc, tip, tt = phase_progress(phase)

    # Task table
    rows = []
    for task in phase.tasks:
        sub_text = ""
        if task.subtasks.total > 0:
            pct = (task.subtasks.done / task.subtasks.total) * 100
            sub_text = f'''
                <div class="checklist-bar"><span class="checklist-fill" style="width:{pct}%"></span></div>
                {task.subtasks.done}/{task.subtasks.total}'''

        deps_text = ", ".join(task.depends_on) if task.depends_on else ""

        rows.append(f'''
            <tr>
                <td>{status_icon(task.status)}</td>
                <td>{html.escape(task.id)}</td>
                <td>{html.escape(task.title)}</td>
                <td>{badge_html(task.status)}</td>
                <td>{sub_text}</td>
                <td style="color:var(--text-muted)">{deps_text}</td>
            </tr>''')

    task_table = ""
    if rows:
        task_table = f'''
        <section>
            <h2>Tasks</h2>
            <div class="card" style="padding:0;overflow:hidden">
                <table class="task-table">
                    <thead>
                        <tr>
                            <th style="width:40px"></th>
                            <th style="width:60px">ID</th>
                            <th>Task</th>
                            <th style="width:120px">Status</th>
                            <th style="width:140px">Subtasks</th>
                            <th>Depends On</th>
                        </tr>
                    </thead>
                    <tbody>{''.join(rows)}</tbody>
                </table>
            </div>
        </section>'''

    # Content
    content_html = ""
    if phase.content:
        content_html = f'''
        <section>
            <h2>Details</h2>
            <div class="content">{md_to_html(phase.content)}</div>
        </section>'''

    # Meta cards
    meta = []
    meta.append(f'''
        <div class="meta-card">
            <h4>Status</h4>
            <div style="display:flex;align-items:center;gap:0.5rem">
                <span style="font-size:1.5rem">{status_icon(phase.status)}</span>
                {badge_html(phase.status)}
            </div>
        </div>''')

    if tt > 0:
        pct = (tc / tt) * 100
        meta.append(f'''
        <div class="meta-card">
            <h4>Task Progress</h4>
            <div class="progress-bar" style="height:8px;margin-bottom:0.5rem">
                <div class="progress-complete" style="width:{pct}%"></div>
            </div>
            <span>{tc}/{tt} tasks complete</span>
        </div>''')

    if phase.deliverable:
        meta.append(f'''
        <div class="meta-card">
            <h4>Deliverable</h4>
            <p>{html.escape(phase.deliverable)}</p>
        </div>''')

    # Quick links
    links = [f'<a href="index.html" class="quick-link">&#x2190; {html.escape(plan.name)} Overview</a>']
    planning_repo_url = get_planning_repo_url(config)
    if planning_repo_url:
        doc_path = f"Plans/{plan.name}/{phase.doc}" if phase.doc else ""
        if doc_path:
            links.append(f'<a href="{planning_repo_url}/blob/main/{doc_path}" class="quick-link">&#x1F4DD; Phase Source</a>')
    if plan.target_repo_url:
        repo_name = plan.target_repo.split('/')[-1] if '/' in plan.target_repo else plan.target_repo
        links.append(f'<a href="{plan.target_repo_url}" class="quick-link">&#x1F527; {html.escape(repo_name)} Repository</a>')
    if len(links) > 1:
        meta.append(f'''
        <div class="meta-card">
            <h4>Links</h4>
            <div class="quick-links">{"".join(links)}</div>
        </div>''')

    body = f'''
    <header>
        <h1>Phase {phase.id}: {html.escape(phase.title)}</h1>
        <p class="subtitle">Part of <a href="index.html">{html.escape(plan.title)}</a></p>
    </header>

    <div class="meta-grid">{''.join(meta)}</div>

    {task_table}
    {content_html}'''

    return page_html(
        f"Phase {phase.id}: {phase.title} - {plan.title}", body, config,
        [("Dashboard", "../index.html"), (plan.title, "index.html"),
         (f"Phase {phase.id}", None)],
        depth=1)


def generate_knowledge_page(research: list[Artifact], brainstorm: list[Artifact],
                            config: dict) -> str:
    """Knowledge base page: research + brainstorm index."""
    sections = []

    for label, items in [("Research", research), ("Brainstorm", brainstorm)]:
        if not items:
            continue
        cards = []
        for art in sorted(items, key=lambda a: a.created or "", reverse=True):
            tags_html = ""
            if art.tags:
                tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in art.tags)
                tags_html = f'<div class="tags" style="margin-top:0.5rem">{tag_spans}</div>'

            overview = extract_overview(art.content)
            cards.append(f'''
                <div class="card" style="margin-bottom:0.75rem">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                        <h3 style="font-size:1rem"><a href="knowledge/{art.slug}.html">{html.escape(art.title)}</a></h3>
                        {badge_html(art.status)}
                    </div>
                    {f'<p class="subtitle" style="font-size:0.875rem">{html.escape(overview)}</p>' if overview else ''}
                    {tags_html}
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.5rem">{art.created}</div>
                </div>''')

        sections.append(f'''
        <section>
            <h2>{label} ({len(items)})</h2>
            {''.join(cards)}
        </section>''')

    body = f'''
    <header>
        <h1>Knowledge Base</h1>
        <p class="subtitle">Research and brainstorm artifacts</p>
    </header>
    {''.join(sections) if sections else '<p class="subtitle">No research or brainstorm artifacts yet.</p>'}'''

    return page_html("Knowledge Base", body, config,
                     [("Dashboard", "index.html"), ("Knowledge", None)], depth=0)


def generate_retros_page(retros: list[Artifact], config: dict) -> str:
    """Retrospectives index page."""
    cards = []
    for art in sorted(retros, key=lambda a: a.created or "", reverse=True):
        overview = extract_overview(art.content)
        tags_html = ""
        if art.tags:
            tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in art.tags)
            tags_html = f'<div class="tags" style="margin-top:0.5rem">{tag_spans}</div>'

        cards.append(f'''
            <div class="card" style="margin-bottom:0.75rem">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                    <h3 style="font-size:1rem"><a href="retros/{art.slug}.html">{html.escape(art.title)}</a></h3>
                    {badge_html(art.status)}
                </div>
                {f'<p class="subtitle" style="font-size:0.875rem">{html.escape(overview)}</p>' if overview else ''}
                {tags_html}
                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.5rem">{art.created}</div>
            </div>''')

    body = f'''
    <header>
        <h1>Retrospectives</h1>
        <p class="subtitle">Learnings and reflections</p>
    </header>
    <section>
        {''.join(cards) if cards else '<p class="subtitle">No retrospectives yet.</p>'}
    </section>'''

    return page_html("Retrospectives", body, config,
                     [("Dashboard", "index.html"), ("Retros", None)], depth=0)


def generate_artifact_list_page(artifacts: list[Artifact], category: str,
                                subtitle: str, config: dict) -> str:
    """Generic artifact list page for specs/designs."""
    cards = []
    for art in sorted(artifacts, key=lambda a: a.created or "", reverse=True):
        overview = extract_overview(art.content)
        tags_html = ""
        if art.tags:
            tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in art.tags)
            tags_html = f'<div class="tags" style="margin-top:0.5rem">{tag_spans}</div>'

        dir_slug = category.lower()
        cards.append(f'''
            <div class="card" style="margin-bottom:0.75rem">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                    <h3 style="font-size:1rem"><a href="{dir_slug}/{art.slug}.html">{html.escape(art.title)}</a></h3>
                    {badge_html(art.status)}
                </div>
                {f'<p class="subtitle" style="font-size:0.875rem">{html.escape(overview)}</p>' if overview else ''}
                {tags_html}
                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.5rem">{art.created}</div>
            </div>''')

    body = f'''
    <header>
        <h1>{category}</h1>
        <p class="subtitle">{html.escape(subtitle)}</p>
    </header>
    <section>
        {''.join(cards) if cards else f'<p class="subtitle">No {category.lower()} yet.</p>'}
    </section>'''

    return page_html(category, body, config,
                     [("Dashboard", "index.html"), (category, None)], depth=0)


def generate_artifact_detail_page(art: Artifact, category: str,
                                  list_page: str, config: dict) -> str:
    """Detail page for a single artifact (research, brainstorm, spec, design, retro)."""
    # Meta cards
    meta = [f'''
        <div class="meta-card">
            <h4>Status</h4>
            <div style="display:flex;align-items:center;gap:0.5rem">
                <span style="font-size:1.5rem">{status_icon(art.status)}</span>
                {badge_html(art.status)}
            </div>
        </div>''']

    if art.created:
        meta.append(f'''
        <div class="meta-card">
            <h4>Created</h4>
            <p>{html.escape(art.created)}</p>
        </div>''')

    if art.tags:
        tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in art.tags)
        meta.append(f'''
        <div class="meta-card">
            <h4>Tags</h4>
            <div class="tags">{tag_spans}</div>
        </div>''')

    if art.related:
        rel_links = "".join(f'<li>{html.escape(str(r))}</li>' for r in art.related)
        meta.append(f'''
        <div class="meta-card">
            <h4>Related</h4>
            <ul style="list-style:none;font-size:0.875rem">{rel_links}</ul>
        </div>''')

    content_html = ""
    if art.content:
        content_html = f'''
        <section>
            <div class="content">{md_to_html(art.content)}</div>
        </section>'''

    body = f'''
    <header>
        <h1>{html.escape(art.title)}</h1>
        <p class="subtitle"><a href="../{list_page}">{category}</a></p>
    </header>

    <div class="meta-grid">{''.join(meta)}</div>

    {content_html}'''

    dir_slug = category.lower() if category != "Knowledge" else "knowledge"
    return page_html(
        art.title, body, config,
        [("Dashboard", "../index.html"), (category, f"../{list_page}"),
         (art.title, None)],
        depth=1)
