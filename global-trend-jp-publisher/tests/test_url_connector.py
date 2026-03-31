from global_trend_jp_publisher.connectors.url_article import extract_article_text_from_html


def test_extract_article_text_from_html_uses_og_title_and_paragraphs() -> None:
    html = """
    <html>
      <head>
        <title>Fallback Title</title>
        <meta property=\"og:title\" content=\"Preferred OG Title\" />
      </head>
      <body>
        <article>
          <p>Short.</p>
          <p>This is a long paragraph with enough characters to be included in the snippet output one.</p>
          <p>This is another long paragraph with enough characters to be included in the snippet output two.</p>
        </article>
      </body>
    </html>
    """
    title, snippet = extract_article_text_from_html(html)
    assert title == "Preferred OG Title"
    assert "included in the snippet output one" in snippet
    assert "included in the snippet output two" in snippet


def test_extract_article_text_from_html_falls_back_to_og_description() -> None:
    html = """
    <html>
      <head>
        <meta property=\"og:description\" content=\"Fallback description from og meta\" />
      </head>
      <body></body>
    </html>
    """
    _, snippet = extract_article_text_from_html(html)
    assert snippet == "Fallback description from og meta"
