<!--
Manual-paste fallback for a Wine Berserkers thread.

Use this ONLY if the browser-console fetcher (scripts/wb_browser_fetch.js) isn't
an option. Copy each post from your logged-in browser and format it below.

Format the parser (parse_wb_thread.py -> parse_raw_markdown) expects:

  - One `## <Username> — <date>` header per post. The dash may be em (—),
    en (–), or hyphen (-). Date is either `2013-08` or `Aug 2013`.
  - The post body follows on the next lines. Producer-list posts should put
    one producer per line (bullets, numbers, and a trailing "- 12%" / "3 btls"
    suffix are all stripped automatically).
  - Only posts with >= 3 short producer-name lines are counted as list posts;
    prose replies are ignored, so you can paste them verbatim without harm.

Save the real file as  raw/berserkers/threads/top10_in_cellar.raw.md  (drop the
_TEMPLATE / delete the examples below) and run:

  python scripts/parse_wb_thread.py raw/berserkers/threads/top10_in_cellar.raw.md \
    --slug top10_in_cellar \
    --title "Top 10 Producers in your cellar?" \
    --thread-url https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370 \
    --merge-with raw/berserkers/threads/top10_in_cellar.json

Delete everything from the first example header down before you paste real posts.
-->

## exampleuser — 2013-08

Bedrock
Rhys
Ridge
Rivers-Marie
JJ Prum
Produttori
Donnhoff
Jadot
Carlisle
Goodfellow

## anotheruser — Mar 2026

1. Bruno Giacosa - 3 btls
2. Huet
3. Saxum
4. Dujac
5. Willi Schaefer
6. Lopez de Heredia
7. Chevillon
8. Williams Selyem
9. Krug
10. Burlotto
