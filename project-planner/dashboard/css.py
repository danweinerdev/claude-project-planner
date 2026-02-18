"""CSS styles for the dashboard."""

CSS = """\
:root {
    --bg: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --yellow: #d29922;
    --orange: #db6d28;
    --red: #f85149;
    --purple: #a371f7;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.container { max-width: 1400px; margin: 0 auto; padding: 2rem; }

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Navigation */
.nav {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.nav-brand { font-weight: 600; color: var(--text); }
.nav-sep { color: var(--text-muted); }
.breadcrumb { display: flex; align-items: center; gap: 0.5rem; }

/* Header */
header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
h1 { font-size: 1.75rem; font-weight: 600; margin-bottom: 0.5rem; }
.subtitle { color: var(--text-muted); }

/* Stats bar */
.stats { display: flex; gap: 2rem; margin-top: 1rem; flex-wrap: wrap; }
.stat { display: flex; align-items: baseline; gap: 0.5rem; }
.stat-value { font-size: 1.5rem; font-weight: 600; }
.stat-label { color: var(--text-muted); }
.stat-complete .stat-value { color: var(--green); }
.stat-progress .stat-value { color: var(--yellow); }
.stat-planned .stat-value { color: var(--text-muted); }

/* Sections */
section { margin-bottom: 2rem; }
h2 { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; }

/* Cards */
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
}

/* In-progress section */
.in-progress-section { margin-bottom: 2rem; }
.work-list { display: flex; flex-direction: column; gap: 0.75rem; }
.work-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    background: var(--bg-tertiary);
    border-radius: 6px;
    text-decoration: none;
    color: var(--text);
}
.work-item:hover { border: 1px solid var(--accent); margin: -1px; text-decoration: none; }
.work-plan {
    background: var(--yellow);
    color: var(--bg);
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}
.work-phase { font-weight: 500; }
.work-progress { color: var(--text-muted); font-size: 0.875rem; margin-left: auto; }

/* Plans grid */
.plans-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1rem;
}

.plan-card { transition: border-color 0.2s; }
.plan-card:hover { border-color: var(--accent); }
.plan-card.status-in-progress { border-left: 3px solid var(--yellow); }
.plan-card.status-complete { border-left: 3px solid var(--green); }
.plan-card.status-planned, .plan-card.status-draft { border-left: 3px solid var(--text-muted); }
.plan-card.status-blocked { border-left: 3px solid var(--red); }
.plan-card.status-deferred, .plan-card.status-archived { border-left: 3px solid var(--orange); }

.plan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}
.plan-header h3 { font-size: 1.1rem; font-weight: 600; }
.plan-header a { color: var(--text); }
.plan-header a:hover { color: var(--accent); text-decoration: none; }

/* Badges */
.badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    white-space: nowrap;
}
.badge-complete, .badge-approved, .badge-implemented { background: var(--green); color: var(--bg); }
.badge-in-progress, .badge-active, .badge-review { background: var(--yellow); color: var(--bg); }
.badge-planned, .badge-draft { background: var(--bg-tertiary); color: var(--text-muted); }
.badge-blocked { background: var(--red); color: var(--bg); }
.badge-deferred, .badge-archived, .badge-superseded { background: var(--orange); color: var(--bg); }

/* Progress bar */
.progress-bar {
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    display: flex;
    overflow: hidden;
    margin-bottom: 0.25rem;
}
.progress-complete { background: var(--green); }
.progress-active { background: var(--yellow); }
.progress-text {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

/* Phase / task list in cards */
.phase-list { margin-bottom: 0.75rem; }
.phase-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.875rem;
}
.phase-item:last-child { border-bottom: none; }
.phase-item:hover { background: var(--bg-tertiary); }
.phase-icon { flex-shrink: 0; }
.phase-name { flex: 1; }
.phase-name a { color: var(--text); }
.phase-name a:hover { color: var(--accent); }
.phase-progress-text { color: var(--text-muted); font-size: 0.75rem; }

.plan-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: var(--text-muted);
    padding-top: 0.5rem;
    border-top: 1px solid var(--border);
}

/* Plan detail page */
.plan-detail-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
}

/* Phase detail page */
.task-table { width: 100%; border-collapse: collapse; }
.task-table th {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 2px solid var(--border);
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-muted);
}
.task-table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.task-table tr:hover { background: var(--bg-tertiary); }

/* Checklist progress */
.checklist-bar {
    width: 80px;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    overflow: hidden;
    display: inline-block;
    vertical-align: middle;
    margin-right: 0.5rem;
}
.checklist-fill { height: 100%; background: var(--green); display: block; }

/* Content area */
.content {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
}
.content h1, .content h2, .content h3, .content h4 {
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}
.content h1:first-child, .content h2:first-child { margin-top: 0; }
.content p { margin-bottom: 0.75rem; }
.content ul, .content ol {
    margin-bottom: 0.75rem;
    padding-left: 1.5rem;
}
.content li { margin-bottom: 0.25rem; }
.content pre {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
    margin-bottom: 1rem;
}
.content code {
    font-family: 'SF Mono', Consolas, monospace;
    font-size: 0.875rem;
}
.content p code, .content li code {
    background: var(--bg-tertiary);
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
}
.content input[type="checkbox"] { margin-right: 0.5rem; }

/* Tags */
.tags { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem; }
.tag {
    font-size: 0.7rem;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    background: var(--bg-tertiary);
    color: var(--text-muted);
}

/* Meta grid */
.meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.meta-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
}
.meta-card h4 {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

/* Navigation link cards */
.nav-links {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.nav-link-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    font-weight: 500;
    color: var(--text);
    text-decoration: none;
    transition: border-color 0.2s;
}
.nav-link-card:hover { border-color: var(--accent); color: var(--accent); text-decoration: none; }
.nav-link-count {
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    background: var(--bg-tertiary);
    color: var(--text-muted);
}

/* Quick links (repo links, source links) */
.quick-links {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.quick-link {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    font-size: 0.8125rem;
    color: var(--accent);
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    text-decoration: none;
    transition: border-color 0.2s;
}
.quick-link:hover { border-color: var(--accent); text-decoration: none; }

.generated {
    margin-top: 2rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.75rem;
}
"""
