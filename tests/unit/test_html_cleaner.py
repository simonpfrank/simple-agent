"""
Unit tests for HTMLCleaner helper.

TDD: Tests written first, implementation follows.
"""

import pytest
from simple_agent.tools.helpers.html import HTMLCleaner


class TestHTMLCleanerMinimal:
    """Test minimal strip_level: Remove only scripts, styles, svg, images"""

    def test_removes_script_tags(self):
        """Should remove <script> tags"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = "<p>Content</p><script>alert('test')</script><p>More</p>"
        result, stats = cleaner.clean(html)
        assert "<script>" not in result
        assert "alert" not in result
        assert "Content" in result
        assert "More" in result

    def test_removes_style_tags(self):
        """Should remove <style> tags"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = "<p>Content</p><style>.bg { color: red; }</style>"
        result, stats = cleaner.clean(html)
        assert "<style>" not in result
        assert "color: red" not in result
        assert "Content" in result

    def test_removes_svg_tags(self):
        """Should remove <svg> tags"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = "<p>Content</p><svg><circle /></svg>"
        result, stats = cleaner.clean(html)
        assert "<svg>" not in result
        assert "circle" not in result
        assert "Content" in result

    def test_removes_img_tags(self):
        """Should remove <img> tags"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = '<p>Content</p><img src="test.jpg" /><p>More</p>'
        result, stats = cleaner.clean(html)
        assert "img" not in result.lower()
        assert "test.jpg" not in result
        assert "Content" in result
        assert "More" in result

    def test_preserves_main_content(self):
        """Should preserve main content"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = "<h1>Title</h1><p>Content here</p><table><tr><td>Data</td></tr></table>"
        result, stats = cleaner.clean(html)
        assert "Title" in result
        assert "Content here" in result
        assert "Data" in result

    def test_preserves_links(self):
        """Should preserve href links"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = '<p>Check <a href="https://example.com">this link</a></p>'
        result, stats = cleaner.clean(html)
        assert "https://example.com" in result
        assert "this link" in result

    def test_returns_stats(self):
        """Should return cleaning statistics"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = "<p>Content</p><script>test</script>"
        result, stats = cleaner.clean(html)
        assert "original_size" in stats
        assert "cleaned_size" in stats
        assert "reduction_percent" in stats
        assert stats["original_size"] > 0
        assert stats["cleaned_size"] > 0
        assert stats["reduction_percent"] >= 0


class TestHTMLCleanerModerate:
    """Test moderate strip_level: Remove nav/footer/ads/sidebars/comments"""

    def test_removes_nav_id(self):
        """Should remove elements with id='nav' or 'navigation'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<nav id='nav'>Navigation</nav>"
            "<p>Content</p>"
        )
        result, stats = cleaner.clean(html)
        assert "Navigation" not in result
        assert "Content" in result

    def test_removes_footer_id(self):
        """Should remove elements with id='footer'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<p>Content</p>"
            "<footer id='footer'>Footer content</footer>"
        )
        result, stats = cleaner.clean(html)
        assert "Footer content" not in result
        assert "Content" in result

    def test_removes_header_id(self):
        """Should remove elements with id='header'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<header id='header'>Header content</header>"
            "<p>Content</p>"
        )
        result, stats = cleaner.clean(html)
        assert "Header content" not in result
        assert "Content" in result

    def test_removes_sidebar_class(self):
        """Should remove elements with class='sidebar'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<p>Content</p>"
            "<div class='sidebar'>Sidebar stuff</div>"
        )
        result, stats = cleaner.clean(html)
        assert "Sidebar stuff" not in result
        assert "Content" in result

    def test_removes_ads_class(self):
        """Should remove elements with class='ad' or 'advertisement'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<p>Content</p>"
            "<div class='ad'>Buy now!</div>"
        )
        result, stats = cleaner.clean(html)
        assert "Buy now" not in result
        assert "Content" in result

    def test_removes_widget_class(self):
        """Should remove elements with class='widget'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<p>Content</p>"
            "<div class='widget'>Widget content</div>"
        )
        result, stats = cleaner.clean(html)
        assert "Widget content" not in result
        assert "Content" in result

    def test_removes_comments_class(self):
        """Should remove elements with class='comments' or 'disqus'"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<p>Content</p>"
            "<div class='comments'>Comment section</div>"
        )
        result, stats = cleaner.clean(html)
        assert "Comment section" not in result
        assert "Content" in result


class TestHTMLCleanerAggressive:
    """Test aggressive strip_level: Remove forms, iframes, tracking"""

    def test_removes_forms(self):
        """Should remove <form> tags"""
        cleaner = HTMLCleaner(strip_level="aggressive")
        html = (
            "<p>Content</p>"
            "<form><input type='text' /></form>"
        )
        result, stats = cleaner.clean(html)
        assert "form" not in result.lower()
        assert "input" not in result.lower()
        assert "Content" in result

    def test_removes_iframes(self):
        """Should remove <iframe> tags"""
        cleaner = HTMLCleaner(strip_level="aggressive")
        html = (
            "<p>Content</p>"
            "<iframe src='https://example.com'></iframe>"
        )
        result, stats = cleaner.clean(html)
        assert "iframe" not in result.lower()
        assert "example.com" not in result
        assert "Content" in result

    def test_removes_noscript(self):
        """Should remove <noscript> tags"""
        cleaner = HTMLCleaner(strip_level="aggressive")
        html = (
            "<p>Content</p>"
            "<noscript>JavaScript required</noscript>"
        )
        result, stats = cleaner.clean(html)
        assert "noscript" not in result.lower()
        assert "JavaScript required" not in result
        assert "Content" in result

    def test_preserves_important_content_aggressively(self):
        """Even with aggressive, should preserve main content"""
        cleaner = HTMLCleaner(strip_level="aggressive")
        html = (
            "<h1>Title</h1>"
            "<p>Important content</p>"
            "<table><tr><td>Data</td></tr></table>"
            "<code>code_snippet</code>"
            "<form>form</form>"
        )
        result, stats = cleaner.clean(html)
        assert "Title" in result
        assert "Important content" in result
        assert "Data" in result
        assert "code_snippet" in result
        # Form should be removed
        assert "form" not in result.lower()


class TestHTMLCleanerEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_html(self):
        """Should handle empty HTML"""
        cleaner = HTMLCleaner(strip_level="moderate")
        result, stats = cleaner.clean("")
        assert isinstance(result, str)
        assert stats["original_size"] == 0

    def test_html_with_only_scripts(self):
        """Should handle HTML with only scripts/styles"""
        cleaner = HTMLCleaner(strip_level="minimal")
        html = "<script>test</script><style>.a{}</style>"
        result, stats = cleaner.clean(html)
        # Result should be mostly empty but still valid
        assert isinstance(result, str)

    def test_nested_tags(self):
        """Should handle nested HTML correctly"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<div class='sidebar'>"
            "<div><p>Sidebar content with nested</p></div>"
            "</div>"
            "<p>Main content</p>"
        )
        result, stats = cleaner.clean(html)
        assert "Main content" in result
        assert "Sidebar content" not in result

    def test_markdown_output_format(self):
        """Should return markdown formatted text"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = "<h1>Title</h1><p>Paragraph</p>"
        result, stats = cleaner.clean(html)
        # Should contain markdown-like formatting
        assert isinstance(result, str)
        assert len(result) > 0

    def test_reduction_percentage_calculation(self):
        """Should calculate reduction percentage correctly"""
        cleaner = HTMLCleaner(strip_level="moderate")
        html = (
            "<nav>nav</nav>"
            "<p>Content</p>"
            "<footer>footer</footer>"
        )
        result, stats = cleaner.clean(html)
        assert stats["reduction_percent"] > 0
        assert stats["reduction_percent"] <= 100
        assert stats["original_size"] > stats["cleaned_size"]
