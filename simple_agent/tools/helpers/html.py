"""HTML cleaning helper for web content extraction.

Cleans HTML by removing bloat (scripts, styles, ads, nav, etc.) while preserving
main content. Reusable for web tools and future browser automation.
"""

from bs4 import BeautifulSoup
import html2text


class HTMLCleaner:
    """Clean HTML by removing bloat, preserving main content."""

    def __init__(self, strip_level: str = "moderate"):
        """
        Initialize cleaner with strip level.

        Args:
            strip_level: "minimal" | "moderate" | "aggressive"
                - minimal: Remove only scripts, styles, svg, images
                - moderate: + remove nav, footer, sidebars, comments
                - aggressive: + remove forms, iframes, tracking

        Raises:
            ValueError: If strip_level is invalid
        """
        if strip_level not in ("minimal", "moderate", "aggressive"):
            raise ValueError(f"Invalid strip_level: {strip_level}")
        self.strip_level = strip_level

    def clean(self, html: str) -> tuple[str, dict]:
        """
        Clean HTML and convert to markdown.

        Args:
            html: Raw HTML string

        Returns:
            (markdown: str, stats: dict)
            stats = {
                "original_size": bytes,
                "cleaned_size": bytes,
                "reduction_percent": float
            }
        """
        if not html:
            return "", {
                "original_size": 0,
                "cleaned_size": 0,
                "reduction_percent": 0.0,
            }

        original_size = len(html)
        soup = BeautifulSoup(html, "html.parser")

        # Always remove these (all levels)
        self._remove_tags(soup, ["script", "style", "svg", "img", "picture"])

        # Strip level specific removals
        if self.strip_level == "minimal":
            # Minimal: only remove obvious bloat
            pass

        elif self.strip_level == "moderate":
            # Moderate: remove nav, footer, sidebars, comments
            self._remove_by_id(soup, ["nav", "navigation", "footer", "header"])
            self._remove_by_class(soup, ["sidebar", "ad", "widget", "comments", "disqus"])
            self._remove_tags(soup, ["noscript"])

        elif self.strip_level == "aggressive":
            # Aggressive: remove forms, iframes, tracking
            self._remove_by_id(soup, ["nav", "navigation", "footer", "header"])
            self._remove_by_class(
                soup, ["sidebar", "ad", "advertisement", "widget", "comments", "disqus"]
            )
            self._remove_tags(soup, ["noscript", "form", "iframe"])

        # Convert to markdown
        markdown = self._to_markdown(soup)
        cleaned_size = len(markdown)

        # Calculate stats
        reduction_percent = (
            100 * (original_size - cleaned_size) / original_size
            if original_size > 0
            else 0.0
        )

        stats = {
            "original_size": original_size,
            "cleaned_size": cleaned_size,
            "reduction_percent": round(reduction_percent, 2),
        }

        return markdown, stats

    def _remove_tags(self, soup: BeautifulSoup, tags: list[str]) -> None:
        """Remove specified tags from soup."""
        for tag in soup.find_all(tags):
            tag.decompose()

    def _remove_by_id(self, soup: BeautifulSoup, ids: list[str]) -> None:
        """Remove elements with specified IDs."""
        for element_id in ids:
            for element in soup.find_all(id=element_id):
                element.decompose()

    def _remove_by_class(self, soup: BeautifulSoup, classes: list[str]) -> None:
        """Remove elements with specified classes."""
        for class_name in classes:
            # Find all elements with this class
            for element in soup.find_all(class_=class_name):
                element.decompose()

    def _to_markdown(self, soup: BeautifulSoup) -> str:
        """Convert BeautifulSoup to markdown."""
        # Use html2text to convert
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap long lines

        markdown = h.handle(str(soup))

        # Clean up extra whitespace
        lines = [line.rstrip() for line in markdown.split("\n")]
        # Remove excessive blank lines
        cleaned_lines = []
        blank_count = 0
        for line in lines:
            if line.strip():
                cleaned_lines.append(line)
                blank_count = 0
            else:
                blank_count += 1
                if blank_count <= 2:  # Allow max 2 consecutive blank lines
                    cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()
