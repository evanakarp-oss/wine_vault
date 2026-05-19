"""
Price out single-bottle "ladder style" wood racking for a 2,000 bottle home cellar.

Ladder racking = vertical 2x rails with horizontal wood dowels/cleats; each
bottle rests neck-out single-deep, label visible. This is the highest-density
visible-label format and the de-facto standard for serious home cellars.

Two sections, both regenerable into `wiki/_views/racking_2k_cellar.md`:

  1. PROVIDERS: global builders ranked by all-in cost per bottle
     (kit/material + estimated freight to NYC, USD). Domestic, European,
     Asian OEM, custom carpentry.

  2. ALTERNATIVES: products and materials NOT marketed as wine racking
     that achieve the same single-bottle ladder geometry. DIY, IKEA hacks,
     sauna/marine ladder kits, CNC kits, library shelving.

Numbers are 2026-05 field estimates from public price lists, retailer
quote ranges, Alibaba FOB pricing, and lumber yard rates. Treat as an
order-of-magnitude shortlist for quote-gathering, not a binding bid.

Run:
    python scripts/price_racking_2k_cellar.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

VAULT = Path(__file__).resolve().parent.parent
OUT = VAULT / "wiki" / "_views" / "racking_2k_cellar.md"

TARGET_BOTTLES = 2000
TODAY = date.today().isoformat()


@dataclass
class Provider:
    name: str
    country: str
    region: Literal["NA", "EU", "UK", "ASIA", "OCE"]
    # Per-bottle kit/material cost in USD, low-high range.
    usd_per_bottle: tuple[float, float]
    # Freight estimate to NYC for the full 2,000-bottle order, USD.
    freight_to_nyc_usd: tuple[int, int]
    # Domestic install/finishing labor *not* included in kit price; rough USD.
    install_labor_usd: tuple[int, int]
    lead_weeks: tuple[int, int]
    wood: str
    notes: str
    sourcing: str

    def all_in_low(self) -> int:
        return int(self.usd_per_bottle[0] * TARGET_BOTTLES
                  + self.freight_to_nyc_usd[0]
                  + self.install_labor_usd[0])

    def all_in_high(self) -> int:
        return int(self.usd_per_bottle[1] * TARGET_BOTTLES
                  + self.freight_to_nyc_usd[1]
                  + self.install_labor_usd[1])

    def all_in_per_bottle_low(self) -> float:
        return self.all_in_low() / TARGET_BOTTLES

    def all_in_per_bottle_high(self) -> float:
        return self.all_in_high() / TARGET_BOTTLES


@dataclass
class Alternative:
    name: str
    category: str
    usd_per_bottle: tuple[float, float]
    labor: Literal["none", "light", "moderate", "heavy"]
    aesthetic: str  # one-line look description
    materials: str
    why_it_works: str
    caveats: str


# ---------------------------------------------------------------------------
# PROVIDERS — sorted is handled at render time. Capture raw data only here.
# Prices are field estimates as of 2026-05; rerun quotes before committing.
# ---------------------------------------------------------------------------

PROVIDERS: list[Provider] = [
    # ── North America ──────────────────────────────────────────────────────
    Provider(
        name="Wine Racks America (Ponderosa Pine, Individual)",
        country="USA (UT)",
        region="NA",
        usd_per_bottle=(3.20, 5.00),
        freight_to_nyc_usd=(450, 900),
        install_labor_usd=(0, 0),  # self-assembly kit
        lead_weeks=(2, 4),
        wood="Ponderosa pine (premium redwood +30%, mahogany +60%)",
        notes="Modular 12-high columns; standard 750ml bore. Unfinished kit; "
              "stain on site. Volume discount tier at 1,500+ bottles.",
        sourcing="wineracks.com — direct kit order",
    ),
    Provider(
        name="Vinrac Modular Pine",
        country="USA (CA)",
        region="NA",
        usd_per_bottle=(3.80, 5.50),
        freight_to_nyc_usd=(500, 950),
        install_labor_usd=(0, 0),
        lead_weeks=(3, 5),
        wood="Knotty pine, optional redwood",
        notes="Cheaper than WCI/Vintage Cellars for the same geometry. "
              "Less polished finish; budget pick if hiring a finish carpenter.",
        sourcing="vinrac.com / Wayfair",
    ),
    Provider(
        name="Kessick Wine Cellars (Traditional Individual)",
        country="USA (VA)",
        region="NA",
        usd_per_bottle=(8.00, 13.00),
        freight_to_nyc_usd=(300, 600),
        install_labor_usd=(2500, 5000),
        lead_weeks=(6, 10),
        wood="Premium mahogany, sapele, or all-heart redwood",
        notes="Architect-grade finish, splined joinery. Pricing on the high "
              "end but eastern-seaboard freight is cheap.",
        sourcing="kessick.com — quote required",
    ),
    Provider(
        name="Wine Cellar Innovations (Designer Series Individual)",
        country="USA (OH)",
        region="NA",
        usd_per_bottle=(7.50, 12.00),
        freight_to_nyc_usd=(350, 700),
        install_labor_usd=(2000, 4500),
        lead_weeks=(5, 9),
        wood="Premium redwood, mahogany, knotty alder",
        notes="Most-quoted US premium. Free design service. Watch the upcharges "
              "(arched displays, crown molding) — they push $/bottle fast.",
        sourcing="winecellarinnovations.com",
    ),
    Provider(
        name="Vigilant Inc (Traditional Series)",
        country="USA (NH)",
        region="NA",
        usd_per_bottle=(7.00, 10.50),
        freight_to_nyc_usd=(200, 500),
        install_labor_usd=(2000, 4500),
        lead_weeks=(4, 8),
        wood="Mahogany or pine; African or Honduran",
        notes="NH-based, easy NYC freight. Standardized SKUs keep cost down vs "
              "WCI's bespoke quoting. Strong fit for a clean traditional look.",
        sourcing="vigilantinc.com",
    ),
    Provider(
        name="IronWine Cellars (hybrid metal-frame + wood crossbars)",
        country="USA (FL)",
        region="NA",
        usd_per_bottle=(9.00, 14.00),
        freight_to_nyc_usd=(400, 800),
        install_labor_usd=(1500, 3500),
        lead_weeks=(5, 8),
        wood="Walnut/cherry/maple crossbars on powder-coated steel ladders",
        notes="Not pure wood, but the visual ladder rhythm is identical and "
              "metal frame trims wood cost. Include for comparison only.",
        sourcing="ironwinecellars.com",
    ),
    Provider(
        name="Rosehill Wine Cellars (cross-border CA)",
        country="Canada (ON)",
        region="NA",
        usd_per_bottle=(6.50, 11.00),
        freight_to_nyc_usd=(600, 1100),
        install_labor_usd=(2000, 4500),
        lead_weeks=(6, 10),
        wood="Mahogany, pine, sapele",
        notes="Toronto-based. CAD weakness vs USD typically lands all-in 10-15% "
              "below Vigilant/WCI. Add USMCA paperwork friction.",
        sourcing="rosehillwinecellars.com",
    ),
    Provider(
        name="Local NYC/Brooklyn finish-carpenter custom build",
        country="USA (NY)",
        region="NA",
        usd_per_bottle=(8.00, 16.00),
        freight_to_nyc_usd=(0, 0),
        install_labor_usd=(0, 0),  # baked into per-bottle
        lead_weeks=(8, 16),
        wood="Whatever you spec — white oak, walnut, mahogany",
        notes="Hire a millwork shop in Greenpoint/Gowanus. Variance is wide: "
              "wood choice + joinery drive cost. You own the design IP.",
        sourcing="referrals via AGA / Bldg-NYC / Sweeten",
    ),

    # ── Europe ─────────────────────────────────────────────────────────────
    Provider(
        name="Bordex Cantinetta (Italian modular pine)",
        country="Italy",
        region="EU",
        usd_per_bottle=(3.50, 5.50),
        freight_to_nyc_usd=(800, 1500),
        install_labor_usd=(1000, 2500),
        lead_weeks=(4, 8),
        wood="Italian pine, oiled finish",
        notes="The European answer to Wine Racks America. Sold via UK/DE/IT "
              "distributors — buy from a UK reseller for English support, ship "
              "consolidated. Famously honest pine ladders, light visual weight.",
        sourcing="winerack.it / wineware.co.uk (resells Bordex)",
    ),
    Provider(
        name="Esigo (Italian designer)",
        country="Italy",
        region="EU",
        usd_per_bottle=(18.00, 35.00),
        freight_to_nyc_usd=(900, 1700),
        install_labor_usd=(1500, 3500),
        lead_weeks=(6, 12),
        wood="Solid oak, walnut, designer veneer panels",
        notes="Architect bait, not budget. Listed for completeness — these are "
              "the people doing the Milan-Design-Week cellars. Skip for 2k cap "
              "unless you're styling the room.",
        sourcing="esigo.com",
    ),
    Provider(
        name="Wineware UK (Traditional Pine self-assembly)",
        country="UK",
        region="UK",
        usd_per_bottle=(4.50, 6.50),
        freight_to_nyc_usd=(1100, 2000),
        install_labor_usd=(0, 0),
        lead_weeks=(3, 6),
        wood="Scandinavian pine",
        notes="GBP weakness post-2025 makes UK kits competitive even with "
              "Atlantic freight. Self-assembly, flat-pack — fits a 20ft container.",
        sourcing="wineware.co.uk",
    ),
    Provider(
        name="La Cave Tonneau / French cellar resellers",
        country="France",
        region="EU",
        usd_per_bottle=(6.00, 10.00),
        freight_to_nyc_usd=(900, 1700),
        install_labor_usd=(1000, 2500),
        lead_weeks=(5, 9),
        wood="French oak, pine",
        notes="Romantic, expensive, slow. French oak is gorgeous but you pay for "
              "the brand and 'fait main' framing.",
        sourcing="lacavetonneau.fr / cavavin.fr",
    ),
    Provider(
        name="Polish custom carpentry (Allegro / Olx workshops)",
        country="Poland",
        region="EU",
        usd_per_bottle=(2.50, 4.50),
        freight_to_nyc_usd=(900, 1600),
        install_labor_usd=(500, 1500),
        lead_weeks=(6, 12),
        wood="Pine, oak, beech — Polish lumber is cheap and excellent",
        notes="HIDDEN GEM. Polish carpenters on Allegro/OLX will build custom "
              "ladder racks to drawing at a third of US pricing. Communication "
              "via translator + dimensioned CAD. Has become standard for UK "
              "wine merchants building back-room storage. Container ship LCL "
              "via Gdansk/Hamburg.",
        sourcing="allegro.pl 'regał na wino', search 'stojak na wino dębowy'",
    ),
    Provider(
        name="Czech custom carpentry (Heureka.cz workshops)",
        country="Czech Republic",
        region="EU",
        usd_per_bottle=(2.80, 5.00),
        freight_to_nyc_usd=(900, 1600),
        install_labor_usd=(500, 1500),
        lead_weeks=(6, 12),
        wood="Beech, oak",
        notes="Same playbook as Poland; slightly higher prices, slightly "
              "better English. Searches: 'regál na víno' / 'vinotéka dřevěná'.",
        sourcing="heureka.cz / firmy.cz",
    ),
    Provider(
        name="German Schreinerei (regional joinery)",
        country="Germany",
        region="EU",
        usd_per_bottle=(7.00, 12.00),
        freight_to_nyc_usd=(900, 1700),
        install_labor_usd=(1000, 2500),
        lead_weeks=(6, 14),
        wood="Eiche (oak), Buche (beech), Fichte (spruce)",
        notes="Search 'Weinregal Eiche Schreiner'. Quality is exceptional; "
              "price is comparable to US mid-tier. Hamburg/Bremen freight to NYC.",
        sourcing="myhammer.de / handwerkerangebote",
    ),
    Provider(
        name="Spanish carpentry (Galicia / Rioja workshops)",
        country="Spain",
        region="EU",
        usd_per_bottle=(3.50, 6.00),
        freight_to_nyc_usd=(900, 1700),
        install_labor_usd=(800, 2000),
        lead_weeks=(6, 12),
        wood="Iberian pine, chestnut, oak",
        notes="'Botellero de madera a medida'. Many Rioja-region shops already "
              "build winery-cellar racks at scale. Direct enquiry via Milanuncios.",
        sourcing="milanuncios.com / vibbo.com",
    ),

    # ── Asia (cost-leaders) ────────────────────────────────────────────────
    Provider(
        name="Alibaba — Vietnamese rubberwood OEM",
        country="Vietnam",
        region="ASIA",
        usd_per_bottle=(1.50, 2.80),
        freight_to_nyc_usd=(2200, 3500),
        install_labor_usd=(1500, 3500),
        lead_weeks=(10, 16),
        wood="Rubberwood, acacia (FSC available)",
        notes="LOWEST FOB COST. Ho Chi Minh / Hai Phong cluster. Order ~1.5 "
              "TEU (20-ft container) for 2,000 bottles + framing waste. Use a "
              "sourcing agent (Dragon Sourcing, Eastbridge) to vet factory + QC. "
              "Add ~$200-400 customs broker + 0-5% duty (HS 9403).",
        sourcing="alibaba.com — filter Trade Assurance + Gold Supplier 5+ yrs",
    ),
    Provider(
        name="Alibaba — Chinese factory (Foshan/Cixi furniture cluster)",
        country="China",
        region="ASIA",
        usd_per_bottle=(1.80, 3.50),
        freight_to_nyc_usd=(2400, 3800),
        install_labor_usd=(1500, 3500),
        lead_weeks=(10, 18),
        wood="Pine, rubberwood, bamboo composite",
        notes="Higher base than Vietnam in 2026 due to Sec 301 tariffs (often "
              "25% on HS 9403.60.80). Bake duty into your spreadsheet. Quality "
              "ceiling is high — Foshan furniture is what most US 'designer' "
              "brands rebadge.",
        sourcing="alibaba.com / 1688.com (agent required for 1688)",
    ),
    Provider(
        name="Indonesian teak workshop (Jepara cluster)",
        country="Indonesia",
        region="ASIA",
        usd_per_bottle=(4.50, 7.50),
        freight_to_nyc_usd=(2400, 3800),
        install_labor_usd=(1500, 3500),
        lead_weeks=(12, 20),
        wood="FSC teak, mahogany",
        notes="Premium tropical hardwood at sub-US prices. Jepara has built "
              "teak for European markets for 30+ years; bottle-rack builds are "
              "well within wheelhouse. Watch CITES/Lacey Act docs on teak.",
        sourcing="indonesia-furniture.com / direct Jepara agents",
    ),

    # ── Oceania ────────────────────────────────────────────────────────────
    Provider(
        name="Wine Stash (Australia)",
        country="Australia",
        region="OCE",
        usd_per_bottle=(5.00, 8.00),
        freight_to_nyc_usd=(2800, 4500),
        install_labor_usd=(0, 0),
        lead_weeks=(8, 14),
        wood="Tasmanian oak, pine",
        notes="Best-in-class AU brand; price-competitive in AUD but Pacific "
              "freight kills the math for NYC. Listed for completeness.",
        sourcing="winestash.com.au",
    ),
]


# ---------------------------------------------------------------------------
# ALTERNATIVES — products not marketed as wine racking that achieve
# ladder-style single-bottle geometry. Sorted by render-time cost.
# ---------------------------------------------------------------------------

ALTERNATIVES: list[Alternative] = [
    Alternative(
        name="DIY 2x4 + hardwood dowel ladder",
        category="Pure DIY from lumber yard",
        usd_per_bottle=(1.20, 2.20),
        labor="heavy",
        aesthetic="Honest workshop — pine rails, oiled oak dowels. Reads "
                  "'serious cellar', not 'showroom'.",
        materials="Construction-grade 2x4 SPF or kiln-dried pine for rails; "
                  "5/8\" or 3/4\" red-oak dowel rod (Home Depot $4-6 / 48\" "
                  "stick); 1/4\" lag screws; Danish oil + wax.",
        why_it_works="Ladder geometry is mechanically trivial: two parallel "
                     "rails, dowels through pre-drilled holes spaced 3.5\" "
                     "vertically (750ml bottle pitch). One column = ~$15 "
                     "materials for 12 bottles. ~$2,500 materials for the "
                     "whole 2k cellar. The cost is your weekends.",
        caveats="3-5 weekends of milling, drilling, sanding, finishing. Need "
                "a drill press for clean dowel holes. Unforgiving of sloppy "
                "layout — print a drilling template.",
    ),
    Alternative(
        name="IKEA IVAR pine shelving + drilled dowels",
        category="IKEA hack",
        usd_per_bottle=(1.80, 2.80),
        labor="moderate",
        aesthetic="Pine warmth, modular. IVAR's untreated pine takes Danish "
                  "oil beautifully. Cellar 'Scandinavian study' look.",
        materials="IVAR side-units ($40-60 each, 50/83/124cm wide) as the "
                  "ladder rails; remove shelves, drill 5/8\" dowel holes "
                  "directly through the upright. Add 3/4\" oak dowel rod.",
        why_it_works="IVAR uprights are 30mm solid pine — strong enough to "
                     "host dowels. One 124cm-wide IVAR side ≈ 1 ladder column "
                     "= 12-14 bottles. ~$3,500 for the whole cellar including "
                     "dowels. Disassembles for moving.",
        caveats="IVAR is 50/83/124cm tall; you'll stack two high (~7ft) for "
                "cellar density. Check ceiling. Less rigid than 2x4 build — "
                "anchor to wall studs.",
    ),
    Alternative(
        name="Sauna ladder kit (Finnish aspen/cedar bench rails)",
        category="Sauna supply",
        usd_per_bottle=(2.50, 4.50),
        labor="moderate",
        aesthetic="Pale Nordic aspen or western red cedar. Very clean, very "
                  "spa. Cedar adds a subtle aroma — debate if that's a feature.",
        materials="Pre-milled sauna bench slats (Tylö, Harvia, SaunaCore) used "
                  "as ladder rails. Sold by linear foot. Pair with dowels.",
        why_it_works="Sauna lumber is kiln-dried to ~8% MC, dimensionally "
                     "stable in high-humidity rooms — exactly cellar conditions. "
                     "Already milled to consistent thickness and crack-free. "
                     "Costs less than premium furniture-grade lumber yards.",
        caveats="Cedar's aromatic oils may transfer through corks over years; "
                "many cellar people consider this a no-go. Aspen is odorless "
                "and the safer pick. Color stays pale even with finish.",
    ),
    Alternative(
        name="CNC plywood ladder kit (Etsy / local maker / SendCutSend wood)",
        category="Digital fabrication",
        usd_per_bottle=(2.00, 4.00),
        labor="light",
        aesthetic="Baltic-birch plywood end-grain edges, very modern. CNC "
                  "joinery means precise circular cradles, not dowels — bottles "
                  "rest in laser-cut half-moons.",
        materials="3/4\" Baltic birch ply ($60-90 / 4x8 sheet). CNC cut by "
                  "Etsy shop or local maker space.",
        why_it_works="DXF the design once, cut N copies. Tab-and-slot assembly, "
                     "no fasteners. Baltic birch laminations are dimensionally "
                     "stable in cellar humidity. A 4x8 sheet yields ~80 bottle "
                     "cradles — ~25 sheets total + cutting fee.",
        caveats="Plywood edges need oil/wax sealing or they wick humidity. "
                "Visual is divisive — looks great in modern rooms, fights "
                "Burgundy-cellar vibes.",
    ),
    Alternative(
        name="Pegboard French-cleat system + custom bottle cradles",
        category="Garage-organization hack",
        usd_per_bottle=(2.50, 4.50),
        labor="moderate",
        aesthetic="Pegboard wall + scattered ladders reads workshop, not "
                  "cellar. Use sparingly or commit to the look.",
        materials="3/4\" pegboard or French-cleat strips wall-mounted, with "
                  "wood-block bottle cradles that hang from the cleats.",
        why_it_works="Reconfigurable: bottle count and rack geometry can shift "
                     "as the cellar evolves. Common in tool-storage / garage "
                     "build circles, ~80% of geometry maps over to bottles.",
        caveats="Not the look most wine collectors want. Better for a back-room "
                "annex than a display cellar.",
    ),
    Alternative(
        name="Marine teak boat-ladder treads (chandlery suppliers)",
        category="Marine supply",
        usd_per_bottle=(6.00, 10.00),
        labor="moderate",
        aesthetic="Heirloom: oiled Burmese teak, brass hardware. Reads like "
                  "a 1920s yacht cellar.",
        materials="Pre-milled teak ladder rungs from West Marine / Defender / "
                  "Whitworths. Pair with teak rails or stainless rod.",
        why_it_works="Teak is dimensionally bombproof at any humidity. Marine "
                     "suppliers carry it pre-finished and pre-drilled at "
                     "fractions of furniture-grade teak prices.",
        caveats="Still ~2-3x the cost of pine DIY. Justified only if you want "
                "the marine aesthetic specifically.",
    ),
    Alternative(
        name="Library / archive shelving (Spacesaver, Montel) + dowel inserts",
        category="Institutional library supply",
        usd_per_bottle=(4.50, 8.00),
        labor="light",
        aesthetic="Industrial-archive: powder-coated steel uprights + warm "
                  "wood shelves. Reads 'serious archive' if that's the vibe.",
        materials="Cantilever library shelving uprights (Spacesaver, Aurora "
                  "Steel) with custom-cut wood shelf inserts drilled for dowels.",
        why_it_works="Library shelving is engineered for dense, heavy book "
                     "loads — a 2k bottle wall is well within spec. Steel "
                     "frames are cheaper than equivalent millwork.",
        caveats="Used market is gold (university surplus). New is overkill on "
                "spec and price for residential use.",
    ),
    Alternative(
        name="Closet/wardrobe systems (IKEA PAX, Elfa) re-purposed",
        category="Closet system",
        usd_per_bottle=(3.50, 6.00),
        labor="moderate",
        aesthetic="Built-in cabinetry look. PAX with custom-drilled side panels "
                  "+ dowels can pass for a designer wine wardrobe.",
        materials="IKEA PAX frames + custom drilled MDF/pine shelf inserts. "
                  "Elfa drawer frames similarly adapt.",
        why_it_works="Cabinet ecosystem is mass-priced. Half the work is "
                     "already done — you provide bottle-bore inserts, the "
                     "frame ships flat.",
        caveats="PAX is melamine-faced particleboard; doesn't take stain. Live "
                "with the factory finish or veneer over it.",
    ),
    Alternative(
        name="Reclaimed wine-crate / OWC slats (free-to-cheap)",
        category="Upcycle",
        usd_per_bottle=(0.50, 1.50),
        labor="heavy",
        aesthetic="Bordeaux-château chic: château logos branded into pine. "
                  "Genuinely beautiful, genuinely rustic.",
        materials="Disassembled OWCs (original wood cases) — 6-pack and "
                  "12-pack. Available free-to-$10 from local wine shops, "
                  "especially after en primeur deliveries. CSW alone discards "
                  "thousands annually.",
        why_it_works="Pine is the right wood, the dimensions are remarkably "
                     "consistent (OWC slats are ~7-10mm × 80-120mm), and the "
                     "branding is a feature. Build ladder rails from 2x4 and "
                     "use OWC slats as the bottle cradles.",
        caveats="Inconsistent stock — gather over 6-12 months. Some OWCs are "
                "spruce/poplar; sort. Labor-intensive denailing and milling. "
                "Best as accent walls, not full cellar.",
    ),
    Alternative(
        name="Stair-tread blanks (oak/maple from lumber yard)",
        category="Stair-supply",
        usd_per_bottle=(3.00, 5.50),
        labor="light",
        aesthetic="Solid, warm. Stair-tread oak is what high-end cellars look "
                  "like under a different name.",
        materials="Pre-milled oak/maple stair treads, 11.25\" × 36-72\" — "
                  "stocked at every lumber yard. Use as ladder rails directly.",
        why_it_works="Stair treads are kiln-dried hardwood, pre-finished or "
                     "ready-to-finish, sized within 1/64\". Cheaper per board "
                     "foot than buying furniture-grade hardwood in shorts.",
        caveats="Cuts must be precise — stair-tread oak shows every flaw "
                "under finish. Better for someone with a chop saw and patience.",
    ),
]


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def fmt_usd(n: float) -> str:
    return f"${n:,.0f}"


def fmt_usd_precise(n: float) -> str:
    return f"${n:,.2f}"


def fmt_range(lo: float, hi: float, dollars: bool = True, decimals: int = 2) -> str:
    if dollars:
        if decimals == 0:
            return f"${lo:,.0f}–${hi:,.0f}"
        return f"${lo:,.{decimals}f}–${hi:,.{decimals}f}"
    return f"{lo}–{hi}"


def render_providers_table(provs: list[Provider]) -> str:
    # Sort by midpoint of all-in per-bottle.
    ranked = sorted(provs, key=lambda p: (p.all_in_per_bottle_low() + p.all_in_per_bottle_high()) / 2)
    lines = [
        "| Rank | Provider | Country | Wood | Kit $/btl | Freight NYC | Install labor | All-in 2k cellar | $/btl all-in | Lead (wk) |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for i, p in enumerate(ranked, 1):
        kit = fmt_range(p.usd_per_bottle[0], p.usd_per_bottle[1], decimals=2)
        freight = fmt_range(p.freight_to_nyc_usd[0], p.freight_to_nyc_usd[1], decimals=0)
        labor = fmt_range(p.install_labor_usd[0], p.install_labor_usd[1], decimals=0) if p.install_labor_usd[1] else "—"
        allin = f"{fmt_usd(p.all_in_low())}–{fmt_usd(p.all_in_high())}"
        per = f"${p.all_in_per_bottle_low():.2f}–${p.all_in_per_bottle_high():.2f}"
        wk = f"{p.lead_weeks[0]}–{p.lead_weeks[1]}"
        lines.append(f"| {i} | {p.name} | {p.country} | {p.wood} | {kit} | {freight} | {labor} | {allin} | {per} | {wk} |")
    return "\n".join(lines)


def render_provider_notes(provs: list[Provider]) -> str:
    ranked = sorted(provs, key=lambda p: (p.all_in_per_bottle_low() + p.all_in_per_bottle_high()) / 2)
    out = []
    for i, p in enumerate(ranked, 1):
        out.append(f"### {i}. {p.name} — {p.country}")
        out.append("")
        out.append(f"- **Wood:** {p.wood}")
        out.append(f"- **All-in 2k cellar:** {fmt_usd(p.all_in_low())}–{fmt_usd(p.all_in_high())} "
                   f"({fmt_usd_precise(p.all_in_per_bottle_low())}–{fmt_usd_precise(p.all_in_per_bottle_high())}/bottle)")
        out.append(f"- **Lead time:** {p.lead_weeks[0]}–{p.lead_weeks[1]} weeks")
        out.append(f"- **Sourcing:** {p.sourcing}")
        out.append(f"- **Notes:** {p.notes}")
        out.append("")
    return "\n".join(out)


def render_alternatives_table(alts: list[Alternative]) -> str:
    ranked = sorted(alts, key=lambda a: (a.usd_per_bottle[0] + a.usd_per_bottle[1]) / 2)
    lines = [
        "| Rank | Alternative | Category | $/btl materials | Total materials (2k) | Labor | Aesthetic |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    for i, a in enumerate(ranked, 1):
        per = f"${a.usd_per_bottle[0]:.2f}–${a.usd_per_bottle[1]:.2f}"
        total = f"{fmt_usd(a.usd_per_bottle[0] * TARGET_BOTTLES)}–{fmt_usd(a.usd_per_bottle[1] * TARGET_BOTTLES)}"
        lines.append(f"| {i} | {a.name} | {a.category} | {per} | {total} | {a.labor} | {a.aesthetic.split('.')[0]}. |")
    return "\n".join(lines)


def render_alternative_notes(alts: list[Alternative]) -> str:
    ranked = sorted(alts, key=lambda a: (a.usd_per_bottle[0] + a.usd_per_bottle[1]) / 2)
    out = []
    for i, a in enumerate(ranked, 1):
        out.append(f"### {i}. {a.name}")
        out.append("")
        out.append(f"- **Category:** {a.category}")
        out.append(f"- **Materials cost:** ${a.usd_per_bottle[0]:.2f}–${a.usd_per_bottle[1]:.2f}/bottle "
                   f"= {fmt_usd(a.usd_per_bottle[0] * TARGET_BOTTLES)}–{fmt_usd(a.usd_per_bottle[1] * TARGET_BOTTLES)} for 2k cellar")
        out.append(f"- **Labor:** {a.labor}")
        out.append(f"- **Aesthetic:** {a.aesthetic}")
        out.append(f"- **Materials:** {a.materials}")
        out.append(f"- **Why it works:** {a.why_it_works}")
        out.append(f"- **Caveats:** {a.caveats}")
        out.append("")
    return "\n".join(out)


def summary_stats(provs: list[Provider], alts: list[Alternative]) -> dict:
    cheapest_prov = min(provs, key=lambda p: p.all_in_per_bottle_low())
    priciest_prov = max(provs, key=lambda p: p.all_in_per_bottle_high())
    cheapest_alt = min(alts, key=lambda a: a.usd_per_bottle[0])
    return {
        "cheapest_provider": cheapest_prov,
        "priciest_provider": priciest_prov,
        "cheapest_alternative": cheapest_alt,
        "n_providers": len(provs),
        "n_alternatives": len(alts),
    }


def render_view() -> str:
    s = summary_stats(PROVIDERS, ALTERNATIVES)
    cp = s["cheapest_provider"]
    pp = s["priciest_provider"]
    ca = s["cheapest_alternative"]

    frontmatter = "\n".join([
        "---",
        "type: build_view",
        f"updated: {TODAY}",
        f"target_bottles: {TARGET_BOTTLES}",
        "format: ladder_style_single_bottle",
        f"n_providers: {s['n_providers']}",
        f"n_alternatives: {s['n_alternatives']}",
        f"cheapest_provider_all_in_low: {cp.all_in_low()}",
        f"cheapest_provider_all_in_high: {cp.all_in_high()}",
        f"cheapest_alternative_low: {int(ca.usd_per_bottle[0] * TARGET_BOTTLES)}",
        f"cheapest_alternative_high: {int(ca.usd_per_bottle[1] * TARGET_BOTTLES)}",
        "generator: scripts/price_racking_2k_cellar.py",
        "---",
        "",
    ])

    body = f"""# Racking the 2,000-Bottle Cellar — Ladder-Style Single-Bottle

Cost evaluation for a custom home cellar built around **ladder-style
single-bottle wood racking** — vertical rails with horizontal dowels/cleats,
neck-out, label-forward, one bottle deep. This is the densest visible-label
format and the working standard for serious home cellars.

Two passes below: (1) **global providers** of this exact rack style, ranked
all-in to NYC; (2) **alternatives** using products NOT marketed as wine
racking that achieve the same geometry. Numbers are 2026-05 field estimates
— treat as a quote-gathering shortlist, not a binding bid.

---

## Section 1 — Global providers, ranked by all-in $/bottle

{s['n_providers']} providers across North America, Europe, Asia, and Oceania.
"All-in" = kit/material cost + estimated freight to NYC + estimated install
labor (where applicable) for the full 2,000-bottle order.

**Cheapest all-in:** {cp.name} — {fmt_usd(cp.all_in_low())}–{fmt_usd(cp.all_in_high())}
({fmt_usd_precise(cp.all_in_per_bottle_low())}–{fmt_usd_precise(cp.all_in_per_bottle_high())}/bottle).
**Priciest all-in:** {pp.name} — {fmt_usd(pp.all_in_low())}–{fmt_usd(pp.all_in_high())}.

The Asian OEM lane wins on FOB cost; container freight + duty + the cost of
a sourcing agent narrow but don't close the gap with US/EU domestic kits.
The most interesting middle path is **Polish/Czech custom carpentry** — sub
$3/bottle materials, comparable freight to Italy, and you get a custom build
to drawing instead of a stock SKU.

{render_providers_table(PROVIDERS)}

### Provider notes (in ranked order)

{render_provider_notes(PROVIDERS)}

---

## Section 2 — Alternative products achieving ladder geometry

{s['n_alternatives']} routes to single-bottle ladder racking using products
not marketed as wine racking. Ranked by materials cost per bottle.

**Cheapest:** {ca.name} — \\${ca.usd_per_bottle[0]:.2f}–\\${ca.usd_per_bottle[1]:.2f}/bottle
({fmt_usd(ca.usd_per_bottle[0] * TARGET_BOTTLES)}–{fmt_usd(ca.usd_per_bottle[1] * TARGET_BOTTLES)} for 2k cellar).

The geometry is mechanically trivial — two parallel rails, dowels through
pre-drilled holes — so the "wine rack" markup is mostly brand and finish.
Anywhere you can buy good wood at scale (lumber yard, IKEA, sauna supply,
marine chandlery, stair supply), you can build the same rack for a fraction
of branded pricing. Trade is labor and finish-quality risk.

{render_alternatives_table(ALTERNATIVES)}

### Alternative notes (in ranked order)

{render_alternative_notes(ALTERNATIVES)}

---

## Recommendation framework

For a 2,000-bottle home cellar build, the sensible shortlist by budget:

- **Under $6k all-in** → DIY 2x4 + dowel ladder, or IKEA IVAR hack, or
  reclaimed OWC slat build. You contribute the labor.
- **$6k–$15k** → Polish/Czech custom carpentry (drawing → build → ship LCL),
  or Wine Racks America self-assembly kit, or Bordex via UK reseller.
- **$15k–$30k** → Vigilant or Wine Cellar Innovations professional install,
  or Rosehill cross-border with bonded carrier.
- **$30k+** → Kessick or local NYC millwork custom; you're buying design,
  joinery, and a name on the bill of sale.

The cost-curve discontinuity is at the labor handoff. Materials are ~$3k
either way; everything above that is installation, finish, and brand.

---

_Regenerate with `python scripts/price_racking_2k_cellar.py`. Prices are
2026-05 field estimates; get three quotes before committing._
"""
    return frontmatter + body


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render_view(), encoding="utf-8")
    s = summary_stats(PROVIDERS, ALTERNATIVES)
    print(f"Wrote {OUT.relative_to(VAULT)}")
    print(f"  {s['n_providers']} providers, {s['n_alternatives']} alternatives")
    print(f"  cheapest provider all-in: {s['cheapest_provider'].name}")
    print(f"    {fmt_usd(s['cheapest_provider'].all_in_low())}–{fmt_usd(s['cheapest_provider'].all_in_high())}")
    print(f"  cheapest alternative: {s['cheapest_alternative'].name}")
    print(f"    ${s['cheapest_alternative'].usd_per_bottle[0]:.2f}–${s['cheapest_alternative'].usd_per_bottle[1]:.2f}/bottle")


if __name__ == "__main__":
    main()
