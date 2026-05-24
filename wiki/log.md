---
type: log
total_entries: 2
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-24] ingest | Wasserman + MFW + Newcomer portfolio pass

Three importer/source portfolios processed in one pass:

- **Becky Wasserman (US importer)**: tagged `importer_us: ["Becky Wasserman"]` on 13 confirmed producer pages already in the vault (Arnoux-Lachaux, Denis Bachelet, Berthaut-Gerbet, Chanterêves, Rudolf Fürst, Lignier-Michelot, Gérard Mugneret, Georges Noëllat, Sylvain Pataille, Simon Bize, Jean-Marc & Thomas Bouley, David Moreau, Pavelot). Created `wiki/importers/Wasserman.md`. ~91 portfolio producers without existing pages parked for future curation passes — not auto-created per source-attribution rule.
- **MFW Wine Co. (US importer)**: full portfolio audit from mfwwineco.com (May 2026). Tagged 6 existing producers (Saint Pierre, La Grolet, Peybonhomme, Chanterêves, Elian Da Ros, Hofgut Falkenstein), created 25 stub pages across France, Italy, California, and Mendoza. Created `wiki/importers/MFW_Wine_Co.md`. Skipped Eclectik (cider) + Michel Couvreur (whisky) as out of scope.
- **Newcomer Wines (Vienna + London, EU-only)**: curated subset of 18 stub pages created — Burgenland (Preisinger, Tschida, Nittnaus, Weninger), Styria (Werlitsch, Muster, Strohmeier), Wachau/Kamptal (Nikolaihof, Muthenthaler, Jurtschitsch), Moravia (Nestarec), French naturals (Carmarans, Matassa, Texier, Morel, Léclapart), Italian (Foradori, Vodopivec). No `importer_us` tagging — Newcomer is EU/UK, not US; recorded in body + `_sources`. Created `wiki/importers/Newcomer_Wines.md` and added to `wiki/_resources.md`.

Taxonomy extended: added Austria (Burgenland, Styria, Wachau, Kamptal, Kremstal, Wagram, Wien), Czechia (Moravia), and United States (California, Oregon, Washington, New York) to `wiki/_TAXONOMY.md`.

Net result: +43 producer pages, +3 importer rollups, +13 producer-page importer tags. Lint: 51 region issues unchanged net (pre-existing).


## [2026-05-24] ingest | Newcomer Wines — German producers

Extended the Newcomer Wines portfolio coverage to the German section:

- Created 5 new producer stubs: Rita & Rudolf Trossen (Mosel/Kinheim), Moritz & Jasmin Kissinger-Bähr (Rheinhessen), Carsten Saalwächter (Rheinhessen/Ingelheim), Jonas Dostert (Mosel/Obermosel/Nittel), Roterfaden (Württemberg).
- Tagged 3 existing German pages with `_sources: newcomer_wines:portfolio_2026-05`: Wasenhaus, Melsheimer, Enderle & Moll.
- Updated `wiki/importers/Newcomer_Wines.md` notable_producers + body list with the 5 new + 3 existing names.

Net +5 producer pages, +3 source-tag updates. Lint unchanged.
