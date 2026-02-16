"""YAML frontmatter parser (stdlib only, no PyYAML)."""

import re


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text.

    Returns (metadata_dict, body_text). If no frontmatter found,
    returns ({}, full_text).

    Handles: scalars, lists (inline [...] and block - items),
    nested mappings (for phases/tasks arrays of objects).
    """
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    yaml_str = text[4:end].strip()
    body = text[end + 4:].strip()

    meta = _parse_yaml_block(yaml_str)
    return meta, body


def _parse_yaml_block(text: str) -> dict:
    """Parse a simple YAML block into a dict."""
    result = {}
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        # Key-value pair
        m = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        value_str = m.group(2).strip()

        # Inline list: [item1, item2]
        if value_str.startswith("["):
            result[key] = _parse_inline_list(value_str)
            i += 1

        # Block list starting on next line
        elif value_str == "" and i + 1 < len(lines) and lines[i + 1].strip().startswith("- "):
            items, i = _parse_block_list(lines, i + 1)
            result[key] = items

        # Quoted string
        elif value_str.startswith('"') and value_str.endswith('"'):
            result[key] = value_str[1:-1]
            i += 1

        # Unquoted scalar
        else:
            result[key] = _parse_scalar(value_str)
            i += 1

    return result


def _parse_inline_list(text: str) -> list:
    """Parse an inline YAML list: [item1, item2, ...]."""
    inner = text.strip("[] \t")
    if not inner:
        return []
    items = []
    for item in re.split(r',\s*', inner):
        item = item.strip().strip('"').strip("'")
        if item:
            items.append(_parse_scalar(item))
    return items


def _parse_block_list(lines: list[str], start: int) -> tuple[list, int]:
    """Parse a block-style YAML list starting at `start`.

    Handles both simple items (- value) and object items (- key: value).
    Returns (items, next_line_index).
    """
    items = []
    i = start
    base_indent = len(lines[i]) - len(lines[i].lstrip())

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break

        stripped = line.strip()
        if not stripped.startswith("- "):
            if indent <= base_indent:
                break
            # Continuation of previous object item
            if items and isinstance(items[-1], dict):
                m = re.match(r'\s+(\w[\w_-]*)\s*:\s*(.*)', line)
                if m:
                    k, v = m.group(1), m.group(2).strip()
                    if v.startswith("["):
                        items[-1][k] = _parse_inline_list(v)
                    elif v.startswith('"') and v.endswith('"'):
                        items[-1][k] = v[1:-1]
                    else:
                        items[-1][k] = _parse_scalar(v)
            i += 1
            continue

        # Remove the "- " prefix
        content = stripped[2:].strip()

        # Check if this is an object item (- key: value)
        m = re.match(r'(\w[\w_-]*)\s*:\s*(.*)', content)
        if m:
            obj = {}
            k, v = m.group(1), m.group(2).strip()
            if v.startswith("["):
                obj[k] = _parse_inline_list(v)
            elif v.startswith('"') and v.endswith('"'):
                obj[k] = v[1:-1]
            else:
                obj[k] = _parse_scalar(v)

            # Read continuation lines for this object
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip():
                    i += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= base_indent:
                    break
                next_stripped = next_line.strip()
                if next_stripped.startswith("- "):
                    break
                cm = re.match(r'(\w[\w_-]*)\s*:\s*(.*)', next_stripped)
                if cm:
                    ck, cv = cm.group(1), cm.group(2).strip()
                    if cv.startswith("["):
                        obj[ck] = _parse_inline_list(cv)
                    elif cv.startswith('"') and cv.endswith('"'):
                        obj[ck] = cv[1:-1]
                    else:
                        obj[ck] = _parse_scalar(cv)
                i += 1

            items.append(obj)
        else:
            # Simple list item
            if content.startswith('"') and content.endswith('"'):
                items.append(content[1:-1])
            else:
                items.append(_parse_scalar(content))
            i += 1

    return items, i


def _parse_scalar(text: str) -> object:
    """Parse a YAML scalar value."""
    text = text.strip()
    if text.lower() in ("true", "yes"):
        return True
    if text.lower() in ("false", "no"):
        return False
    if text.lower() in ("null", "~", ""):
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    # Strip quotes
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text
