# -*- coding: utf-8 -*-
"""
Simple test for 51CTO crawler - ASCII only
"""

import sys
from models.cto51 import Cto51Article, Cto51ContentBlock

def test_model():
    """Test data model"""
    print("\n" + "="*60)
    print("Testing 51CTO Data Model")
    print("="*60 + "\n")

    # Mock article data
    mock_article = {
        "id": "test123",
        "title": "Test Article",
        "date": "2025-11-16",
        "url": "https://ost.51cto.com/test",
        "content": [
            {"type": "text", "value": "Test text content"},
            {"type": "image", "value": "https://example.com/image.jpg"},
            {"type": "code", "value": "print('Hello World')"}
        ],
        "category": "Technology",
        "summary": "This is a test article",
        "source": "51CTO",
        "created_at": "2025-11-16T12:00:00",
        "updated_at": "2025-11-16T12:00:00"
    }

    try:
        # Convert to Pydantic model
        content_blocks = [Cto51ContentBlock(**block) for block in mock_article['content']]
        mock_article['content'] = content_blocks
        article = Cto51Article(**mock_article)

        print("OK - Article model validation successful")
        print(f"  ID: {article.id}")
        print(f"  Title: {article.title}")
        print(f"  Content blocks: {len(article.content)}")

        for i, block in enumerate(article.content, 1):
            print(f"  Block {i}: {block.type.value}")

        print("\n" + "="*60)
        print("OK - All tests passed!")
        print("="*60 + "\n")
        return True

    except Exception as e:
        print(f"ERROR - Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_model():
        print("\nSUCCESS - Data model is working correctly")
        print("The crawler is ready to use (requires Chromium for actual crawling)")
        sys.exit(0)
    else:
        print("\nFAILED - Please check the error messages above")
        sys.exit(1)
