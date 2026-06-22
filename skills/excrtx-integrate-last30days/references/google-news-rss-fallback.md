# Google News RSS Fallback

Use when the last30days engine returns thin results for B2B/industrial/regional topics
and all browser-based searches (Google, Bing, DDG) are blocked by captcha.

## Why It Works

Google News RSS is a legacy endpoint that predates modern bot detection. It returns
clean XML with no JavaScript, no Cloudflare, no captcha. Coverage includes trade
publications, local press, and industry portals — exactly the sources the social
engine misses.

## Query Templates

### Brazilian company (PT-BR)
```bash
curl -s "https://news.google.com/rss/search?q=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("\"Nome da Empresa\""))')&hl=pt-BR&gl=BR&ceid=BR:pt-419"
```

### Industry + region (PT-BR)
```bash
curl -s "https://news.google.com/rss/search?q=ind%C3%BAstria+produtos+limpeza+Santa+Catarina&hl=pt-BR&gl=BR&ceid=BR:pt-419"
```

### Broader term search (English)
```bash
curl -s "https://news.google.com/rss/search?q=%22cleaning+products%22+Brazil+manufacturing&hl=en&gl=US&ceid=US:en"
```

## Parsing Script

```python
import re, html as html_mod

def parse_google_news_rss(xml_content: str, max_items: int = 10):
    """Extract title, date, source, and link from Google News RSS XML."""
    items = re.findall(r'<item>(.*?)</item>', xml_content, re.DOTALL)
    results = []
    for item in items[:max_items]:
        title = re.search(r'<title>(.*?)</title>', item)
        pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
        source = re.search(r'<source[^>]*>(.*?)</source>', item)
        link = re.search(r'<link>(.*?)</link>', item)
        if title:
            results.append({
                'title': html_mod.unescape(title.group(1)).replace('&lt;','<').replace('&gt;','>').replace('&amp;','&'),
                'date': pubdate.group(1) if pubdate else None,
                'source': source.group(1) if source else None,
                'link': link.group(1) if link else None,
            })
    return results

# Usage:
# content = terminal("curl -s 'https://news.google.com/rss/search?q=...'")
# parsed = parse_google_news_rss(content['output'])
# for item in parsed:
#     print(f"[{item['date']}] {item['title']} — {item['source']}")
```

## Limitations

- **No date filter**: The RSS returns all indexed articles, not just recent ones.
  Filter by `<pubDate>` in parsing — items older than 30 days should be flagged `[date:low]`
  and used only for historical context.
- **No content**: Only titles, dates, sources, and links. Full article text requires
  following the link (which may hit the same captcha wall).
- **Brazilian coverage**: Good for companies that appear in indexed news. Regional
  companies without press coverage will still return empty.
- **Google News redirect**: Article links go through `news.google.com/rss/articles/...`
  redirects. Follow with `curl -sL -o /dev/null -w '%{url_effective}'` to resolve.

## Session Example: Guimarães Produtos de Limpeza (2026-06-17)

Engine returned 12 YouTube videos (all 2022-2024) + 12 Reddit threads (none about company).
Google News RSS returned 7 indexed articles spanning 2017-2026, including:
- 2026-02: Amaciante launch (SA+ Ecossistema de Varejo)
- 2025-05: Cashback campaign (Portal G)
- 2023-06: ExpoSuper 2023 coverage (SCC10)
- 2023-05: Anti-mold product launch (SA+)
- 2022-11: Family succession feature (Imprensa News Sul)
