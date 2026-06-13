---
type: gap_view
title: "Raeder's — Sub-$20 Summer House White Picks"
question: "What sub-$20 white at Raeder's can be my house wine for the summer?"
raeders_snapshot: raw/raeders/master_2026-04-25.csv
candidates_screened: 158
curated_shortlist: 9
updated: 2026-05-21
---

# Raeder's — Sub-$20 Summer House White Picks (2026)

Screened **158 sub-$20 whites in stock** at Raeder's (per `raw/raeders/master_2026-04-25.csv`); filtered against Evan's curation taste from `CLAUDE.md` (terroir-driven, biodynamic-leaning, grower-scale; skip mass-market). Picks lean toward European fresh-mineral styles that work as a daily drinker but won't bore.

## Top pick — buy a case

### ★ Pieropan Soave Classico — $19.99

Leonildo Pieropan's family domain, the benchmark Soave producer in Italy. Traditional Garganega from Soave's volcanic hills, fermented in old casks (no oak influence), bottled without filtration. Drinks like a much more serious wine — mineral, almond, salt-driven, with real persistence. Cult cellar-favorite at this price point.

**Pairs with**: anything from a tomato salad to grilled branzino to herbed roast chicken to lighter pastas.

## Strong alternates

| Wine | Price | Region | Why it works as a house white |
|---|---:|---|---|
| **Bonnet-Huteau "Les Bonnets" Muscadet** | $15.99 | Loire — Muscadet-Sèvre-et-Maine | Grower Muscadet from the Bonnet family — organic, lees-aged, lean mineral profile. Oyster + shellfish pairing classic. Lighter than Soave but with similar pedigree-to-price ratio. |
| **Hugues Beaulieu Picpoul de Pinet** | $16.99 | Languedoc — Coteaux du Languedoc | Briny, lemon-zest, sea breeze in a glass. The platonic summer-on-a-patio wine. Perfect for raw bar / oysters / ceviche / poolside. |
| **Dr. Loosen "Dr. L" Riesling Mosel** | $13.99 | Mosel — Mosel-Saar-Ruwer | Most reliable cheap German Riesling on earth. Off-dry, ~9% ABV, kabinett-leaning profile. Best house wine if you cook spicy food regularly — Thai, Sichuan, Indian. Loosen the producer is rock-solid (he also makes the cult Erdener Prälat Riesling). |
| **Argiolas "Costamolino" Vermentino di Sardegna** | $16.99 | Sardinia | Cult Sardinian estate. Vermentino with citrus, salt, garrigue herbs — lighter and more energetic than mainland-Italian Vermentinos. |
| **Pierre Sparr Pinot Blanc Grande Réserve** | $17.99 | Alsace | Soft, broad, food-friendly Alsace Pinot Blanc — works as the white you can pour for anyone without thinking. Note: Pierre Sparr is also on the Wilson Daniels portfolio. |

## Wildcards — if you want something off-radar

- **Hermes Assyrtiko (Peloponnese) — $14.99** — Greek volcanic-style white, saline + structured. Closer to Santorini Assyrtiko (which would be 2-3× the price).
- **Formentini Collio Sauvignon — $19.99** — Friulian Sauvignon Blanc, textured, more body than Loire SB. Note: Formentini is on the Wildman portfolio.
- **Broadbent Vinho Verde — $11.99** — Slightly spritzy, ~9% ABV, the "porch wine" answer. Buy as a sub-$15 by-the-case crusher.

## What to skip

| Category | Examples to avoid |
|---|---|
| Mass-market Pinot Grigio | Cavit, Santa Margherita, Ruffino Lumina, Riff, Santi Sortesele |
| Off-dry / sweet "Riesling" (not a house white) | Heinz Eifel Auslese 2023 (Auslese = dessert sweetness) |
| Negoce Languedoc whites | Laroche "Mas La Chevalière" Sauvignon Blanc (fine but boring; the entry-level Laroche wholesale line) |
| Sketchy old vintages of crisp whites | Leo Hillinger Welschriesling 2002 (~24 years old; not a crisp-fresh proposition) |

## Methodology

```
filter: wine_type contains "White" AND 0 < price_usd <= 20
        AND producer NOT IN { Josh Cellars, Kendall, Yellow Tail, Sutter Home,
                              Barefoot, Cupcake, Stella Rosa, La Marca, ... }
        AND NOT (country == "United States" AND varietal == "Chardonnay")
        # ↑ skip the oaky California Chardonnay segment

score:  +2 if varietal in fresh-mineral set (SB, Riesling, Albariño, Vermentino,
            Picpoul, Pinot Blanc, Soave, Chenin, Grüner, Verdicchio, Assyrtiko,
            Vinho Verde, Falanghina, Pecorino, Fiano, Greco, Sylvaner)
        +2 if region matches Loire/Galicia/Friuli/Mosel/Alto Adige/Languedoc-Picpoul/
            Greek islands/Vinho Verde/Alsace
        +1 if European
        +1 if has a tasting note (signals retailer curation)
```

Top-15 score-5 candidates manually audited against producer reputation (per general wine literature + the importer cross-checks in [[raeders_importer_overview]]).

## Notes on availability

Most of these are NV / large-production wines, so case-quantity buys are realistic. Prices in `raw/raeders/master_2026-04-25.csv` reflect the 2026-04-25 snapshot — confirm at order time. The mixed-case price column on the source CSV (`mixed_case_usd`) typically shaves 10% off; worth asking about for any of these as a house-wine candidate.

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`. Re-run whenever Raeder's posts a fresh inventory snapshot.*
