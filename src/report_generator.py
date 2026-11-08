from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.models import Flag


def generate_report(flags: list[Flag], total_users: int, output_path: str) -> None:
    """Render the review report as HTML and write it to output_path."""
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("review_report.html")

    high_count = sum(1 for f in flags if f.risk_level == "high")
    medium_count = sum(1 for f in flags if f.risk_level == "medium")
    low_count = sum(1 for f in flags if f.risk_level == "low")

    html = template.render(
        generated_at=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        total_users=total_users,
        total_flags=len(flags),
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        flags=flags,
    )

    Path(output_path).write_text(html, encoding="utf-8")
