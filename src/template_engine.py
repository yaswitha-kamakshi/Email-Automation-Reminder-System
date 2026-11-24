"""Load email templates and fill in the $placeholders for each person."""
from string import Template
from .config import TEMPLATES_DIR


def load_template(filename: str):
    """Template file format:  'Subject: ...' first line, a '---' line, then the body."""
    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {filename}")
    text = path.read_text(encoding="utf-8")
    header, _, body = text.partition("\n---\n")
    if not header.lower().startswith("subject:"):
        raise ValueError(f"{filename}: first line must start with 'Subject:'")
    return header.split(":", 1)[1].strip(), body.strip()


def render(subject_tpl: str, body_tpl: str, context: dict):
    """Replace $name, $title, ... Raises KeyError if a placeholder has no value."""
    subject = Template(subject_tpl).substitute(context)
    body = Template(body_tpl).substitute(context)
    return subject, body
