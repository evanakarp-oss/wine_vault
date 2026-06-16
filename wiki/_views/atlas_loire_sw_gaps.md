---
type: gap_view
source: "World Atlas of Wine (Johnson & Robinson)"
ingested: 2026-05-26
updated: 2026-05-26
---

# Gap: Loire + SW France producers from the Hugh Johnson Atlas

Cross-reference of producers visible on the Atlas's Loire and Bergerac sub-region maps against the current `wiki/producers/` set. The Atlas alone is a single source — none of these should be auto-promoted to producer pages until corroborated by CSW, Raeders, DTE, or an importer portfolio.

Companion editorial pages:
- [[Loire_Muscadet|Muscadet (Sèvre et Maine)]]
- [[Loire_Anjou|Anjou]]
- [[Loire_Saumur|Saumur]]
- [[Loire_Chinon_Bourgueil|Chinon & Bourgueil]]
- [[Loire_Vouvray_Montlouis|Vouvray & Montlouis]]
- [[South_West_Bergerac|Bergerac & Monbazillac]]

## Existing pages confirmed by atlas

| Producer | Sub-region | Atlas confirms |
|---|---|---|
| [[domaine_baudry\|Domaine Baudry]] | Chinon | ✓ (Cravant-les-Coteaux) |
| [[bernard_baudry\|Bernard Baudry]] | Chinon | ✓ (Cravant-les-Coteaux) |
| [[domaine_de_la_chevalerie\|Domaine de la Chevalerie]] | Bourgueil | ✓ (Restigné) |
| [[stephane_guion\|Stéphane Guion]] | Bourgueil | ✓ (Benais) |
| [[clos_rougeard\|Clos Rougeard]] | Saumur-Champigny | ✓ (Chacé) |

## High-priority gaps (canonical names per Atlas)

These are the producers the Atlas singles out by name or by lieu-dit. Tier judged by Atlas editorial emphasis + Evan's curation taste filters.

### Vouvray & Montlouis (highest priority — zero coverage)
- **Domaine Huet** — Vouvray; biodynamic since 1980s; Le Mont / Clos du Bourg / Le Haut-Lieu *(Atlas calls out by name)*
- **Domaine du Clos Naudin** (Philippe Foreau) — Vouvray
- **François Chidaine** — Montlouis; biodynamic benchmark
- **Domaine de la Taille aux Loups** (Jacky Blot) — Montlouis (Husseau)
- **Vincent Carême** — Vouvray (Vernou-sur-Brenne)
- **Domaine Champalou** — Vouvray
- **Domaine des Aubuisières** (Bernard Fouquet) — Vouvray
- **Lise et Bertrand Jousset** — Montlouis (Husseau)

### Saumur (one of one existing; multiple high-tier gaps)
- **Domaine des Roches Neuves** (Thierry Germain) — Varrains; biodynamic, peer-tier to Clos Rougeard
- **Domaine Filliatreau** — Chaintres
- **Château du Hureau** — Dampierre-sur-Loire
- **Château de Villeneuve** — Souzay-Champigny
- **Domaine de Nerleux** — St-Cyr-en-Bourg
- **Château de Brézé** — historic Chenin
- **Langlois-Château** — sparkling
- **Clotilde et René-Noël Legrand**
- **Domaine Lavigne**
- **Château de Parnay**
- **Domaine du Val Brun**

### Chinon, Bourgueil, St-Nicolas-de-Bourgueil
- **Charles Joguet** — Sazilly; historical reference
- **Couly-Dutheil** — Chinon
- **Philippe Alliet** — Cravant
- **Olga Raffault** — Savigny-en-Véron
- **Domaine de la Noblaie** — Ligré
- **Domaine du Roncée** / **Fabrice Gasnier**
- **Catherine et Pierre Breton** — Restigné/Bourgueil; natural
- **Yannick Amirault** — La Coudraye / "La Butte"; St-Nicolas + Bourgueil
- **Lamé Delisle Boucard** — Ingrandes-de-Touraine
- **Jean-Paul & Mathieu Mabileau** — St-Nicolas
- **Domaine de la Butte** (Jacky Blot) — Bourgueil

### Anjou & Savennières
- **Nicolas Joly / Coulée de Serrant** — Savennières; biodynamic icon
- **Domaine du Closel** — Savennières
- **Domaine des Baumard** — Rochefort-sur-Loire (Quarts de Chaume)
- **Château Soucherie** — Beaulieu-sur-Layon
- **Château de Fesles** — Bonnezeaux
- **Domaine Cady** — St-Aubin-de-Luigné
- **Domaine Ogereau** — St-Lambert-du-Lattay
- **Domaine de la Sansonnière** (Mark Angeli) — Bonnezeaux/Thouarcé; natural
- **Domaine de la Bergerie**

### Muscadet (Sèvre et Maine)
- **Domaine Pierre Luneau-Papin** — Le Landreau
- **Domaine de l'Écu** (Guy Bossard) — Le Landreau; biodynamic pioneer
- **Domaine de la Pépière** (Marc Ollivier) — Maisdon-sur-Sèvre
- **Domaine Landron** (Jo Landron) — La Haye-Fouassière area
- **Domaine des Herbauges** — Côtes de Grandlieu side
- **Chéreau-Carré**
- **Famille Lieubeau**
- **Château Thébaud**

### Bergerac / Monbazillac (South West — zero coverage)
- **Château Tour des Gendres** (Luc de Conti) — Bergerac; biodynamic; the modern reference
- **Château Tirecul La Gravière** — Monbazillac; sweet
- **Domaine de l'Ancienne Cure** — Bergerac
- **Cave de Monbazillac** — co-op
- (Other Atlas-keyed estates listed in [[South_West_Bergerac]])

## Recommended next steps

1. **CSW check first** — for the names above, run `grep -ril "<producer>" raw/csw/` (or re-run `scripts/ingest_csw.py` after this gap list is reviewed) to see which are championed by Chambers. CSW-championed names earn pages.
2. **Cellar check** — `grep -i "<producer>" wiki/My\ Cellar.csv` to see which Evan already owns.
3. **Promote in order**: Huet → Foreau → Chidaine → Roches Neuves → Joly → Joguet first; these are the most editorially-loaded names across all sub-regions.
4. **Region `South West`** has zero pages; even Tour des Gendres + Tirecul is enough to seed a producer index rollup once added.

## Provenance

Extracted from photos of the World Atlas of Wine (Johnson & Robinson) — Loire and Bergerac sub-region maps. Some producer names below are best-effort transcriptions from small-print map labels; verify against a clearer source before promotion. The Atlas is published, copyrighted material — use it as a guide to discovery, not a paste-in source.
