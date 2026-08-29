"""
Regenerate sitemap.xml from metadata.json.
Run this from the repo root any time you add/remove chapters:
    python3 generate_sitemap.py

IMPORTANT: set SITE_URL to your real domain/GitHub Pages URL first.
"""
import json

SITE_URL = "https://cgcb-01.github.io/Englishopeadia/"  # <-- change this once you have a domain

def main():
    with open("metadata.json") as f:
        data = json.load(f)

    urls = [f"""  <url>
    <loc>{SITE_URL}</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>"""]

    for item in data.values():
        urls.append(f"""  <url>
    <loc>{SITE_URL}?chapter={item['id']}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )

    with open("sitemap.xml", "w") as f:
        f.write(xml)

    print(f"sitemap.xml written with {len(data)} chapter URLs + homepage.")

if __name__ == "__main__":
    main()
