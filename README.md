# Project Planner Marketplace

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin marketplace for structured project planning.

## Installation

```bash
# Add the marketplace
/plugin marketplace add danweinerdev/project-planner

# Install the planner plugin
/plugin install planner
```

## Plugins

| Plugin | Description |
|--------|-------------|
| [planner](./project-planner/) | Structured project planning with lifecycle skills, review agents, and an HTML dashboard |

## Manual Usage

You can also load the plugin directly:

```bash
claude --plugin-dir /path/to/project-planner/project-planner
```

See the [plugin README](./project-planner/README.md) for full documentation.

## License

MIT
