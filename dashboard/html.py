"""HTML generation helpers."""

import html
from datetime import datetime


def status_icon(status: str) -> str:
    return {
        "complete": "&#x2705;",       # green check
        "in-progress": "&#x1F504;",   # arrows
        "planned": "&#x1F4CB;",       # clipboard
        "blocked": "&#x1F6D1;",       # stop sign
        "deferred": "&#x23F8;&#xFE0F;",  # pause
        "draft": "&#x1F4DD;",         # memo
        "active": "&#x1F504;",
        "approved": "&#x2705;",
        "archived": "&#x1F4E6;",
    }.get(status, "&#x1F4CB;")


def badge_html(status: str) -> str:
    label = status.replace("-", " ").replace("_", " ").title()
    return f'<span class="badge badge-{status}">{label}</span>'


def nav_html(config: dict, breadcrumbs: list[tuple[str, str]]) -> str:
    title = config.get("title", "Project Planner")
    crumbs = []
    for name, url in breadcrumbs:
        if url:
            crumbs.append(f'<a href="{url}">{html.escape(name)}</a>')
        else:
            crumbs.append(f'<span>{html.escape(name)}</span>')

    return f'''<nav class="nav">
    <div class="nav-content">
        <span class="nav-brand">{html.escape(title)}</span>
        <span class="nav-sep">/</span>
        <div class="breadcrumb">
            {' <span class="nav-sep">/</span> '.join(crumbs)}
        </div>
    </div>
</nav>'''


def page_html(title: str, body: str, config: dict,
              breadcrumbs: list[tuple[str, str]], depth: int = 0) -> str:
    css_path = "../" * depth + "styles.css"
    site_title = config.get("title", "Project Planner")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - {html.escape(site_title)}</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
    {nav_html(config, breadcrumbs)}
    <div class="container">
        {body}
        <p class="generated">Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>'''
