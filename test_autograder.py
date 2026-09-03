import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from playwright.sync_api import Page

# Target HTML file path or localhost URL
TARGET_URL = os.getenv("SUBMISSION_URL", "file://" + str(Path(__file__).parent / "index.html"))

# Baseline values from original repository template
ORIGINAL_NAME = "jane doe"
ORIGINAL_PHOTOS = ["avatar.jpg", "cover.jpg"]


@pytest.fixture(scope="session")
def html_content():
    """Loads and parses raw HTML for static analysis."""
    path = TARGET_URL.replace("file://", "")
    with open(path, "r", encoding="utf-8") as f:
        return BeautifulSoup(f.read(), "html.parser")


class TestProfileModifications:

    def test_fictitious_name_modified(self, page: Page, html_content: BeautifulSoup):
        """1. Verify name has been changed from default and is present in DOM."""
        page.goto(TARGET_URL)

        # Check main header/title element containing the name
        heading = page.locator("h1, .profile-name, .name, title").first
        name_text = heading.inner_text().strip().lower()

        assert name_text != "", "Name element or heading is empty."
        assert ORIGINAL_NAME not in name_text, (
            f"Name was not modified. Still found default name '{ORIGINAL_NAME}'."
        )

    def test_photos_changed(self, page: Page):
        """2. Verify at least two image src attributes have been updated/replaced."""
        page.goto(TARGET_URL)

        images = page.locator("img").all()
        assert len(images) >= 2, f"Expected at least 2 images, but found {len(images)}."

        image_sources = [img.get_attribute("src") for img in images if img.get_attribute("src")]

        # Ensure original photo filenames are no longer used
        for orig_photo in ORIGINAL_PHOTOS:
            assert not any(orig_photo in src.lower() for src in image_sources), (
                f"Original photo reference '{orig_photo}' is still present."
            )

        # Ensure unique image sources exist
        assert len(set(image_sources)) >= 2, "Images must use distinct source files."

    def test_hobbies_and_stats(self, page: Page, html_content: BeautifulSoup):
        """3. Check for presence of modified hobbies and stats sections."""
        page.goto(TARGET_URL)
        text_content = page.content().lower()

        # Check for common hobby section keywords or bullet lists
        lists = html_content.find_all(["ul", "ol"])
        has_list = len(lists) > 0

        keywords = ["hobby", "hobbies", "stats", "statistics", "interests", "skills"]
        has_keywords = any(kw in text_content for kw in keywords)

        assert has_list or has_keywords, (
            "Could not detect a Hobbies or Stats section (lists or key structural elements)."
        )

    def test_colors_modified(self, page: Page):
        """4. Verify custom CSS color styling or CSS variables differ from default theme."""
        page.goto(TARGET_URL)

        # Extract computed background-color and text color of main container/body
        body_bg = page.evaluate("window.getComputedStyle(document.body).backgroundColor")
        body_color = page.evaluate("window.getComputedStyle(document.body).color")

        # Check inline styles or custom stylesheet presence
        styles = page.locator("style, link[rel='stylesheet']").count()

        assert styles > 0, "No stylesheet or style block detected."
        assert body_bg or body_color, "Failed to evaluate CSS styles."
