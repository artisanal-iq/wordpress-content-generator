"""Utility functions for Markdown conversion."""

import html
import re


def markdown_to_html(markdown_text: str) -> str:
    """Convert a small subset of Markdown to HTML for WordPress."""
    if not markdown_text:
        return ""

    lines = markdown_text.splitlines()
    html_lines = []
    list_open = False
    for line in lines:
        if line.startswith("### "):
            html_lines.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("- "):
            if not list_open:
                html_lines.append("<ul>")
                list_open = True
            item = html.escape(line[2:].strip())
            item = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item)
            html_lines.append(f"<li>{item}</li>")
        else:
            if list_open:
                html_lines.append("</ul>")
                list_open = False
            escaped = html.escape(line.strip())
            escaped = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped)
            if escaped:
                html_lines.append(f"<p>{escaped}</p>")
            else:
                html_lines.append("")

    if list_open:
        html_lines.append("</ul>")

    return "\n".join(html_lines)
