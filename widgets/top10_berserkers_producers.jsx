import { useState } from "react";

const THREAD = {
  title: "Top 10 Producers in Your Cellar?",
  url: "https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370",
  posts: 1089,
  unique_producers: 1115,
  total_mentions: 4999,
  span: "2013 – 2026",
};

const PRODUCERS = [
  {
    rank: 1,
    name: "Bedrock Wine Co.",
    mentions: 98,
    country: "USA",
    region: "Sonoma, CA",
    varietal: "Old-Vine Zinfandel / Heritage Blends",
    note: "Morgan Twain-Peterson. Reclaims pre-Prohibition field blends from ancient Sonoma vineyards. Terroir-obsessed, farming-first.",
    in_cellar: false,
  },
  {
    rank: 2,
    name: "Rhys Vineyards",
    mentions: 94,
    country: "USA",
    region: "Santa Cruz Mtns, CA",
    varietal: "Pinot Noir / Chardonnay",
    note: "Biodynamic estate in the mountains. Extreme site selectivity; each vineyard bottled separately. Among the most serious CA Pinot programs.",
    in_cellar: false,
  },
  {
    rank: 3,
    name: "Ridge Vineyards",
    mentions: 80,
    country: "USA",
    region: "Santa Cruz Mtns, CA",
    varietal: "Cabernet Sauvignon / Zinfandel",
    note: "Monte Bello is one of California's canonical Cabs. Minimal intervention since the 1960s — ingredients list on every label.",
    in_cellar: false,
  },
  {
    rank: 4,
    name: "Rivers-Marie",
    mentions: 74,
    country: "USA",
    region: "Sonoma Coast, CA",
    varietal: "Pinot Noir / Cabernet Sauvignon",
    note: "Thomas Brown. Small-production, site-expressive Sonoma Pinots and a Howell Mountain Cab that punches far above its price.",
    in_cellar: false,
  },
  {
    rank: 5,
    name: "J.J. Prüm",
    mentions: 74,
    country: "Germany",
    region: "Mosel",
    varietal: "Riesling",
    note: "Wehlen Sonnenuhr. Multi-decade cellaring potential. The sweet-spot between tension and petrol that defines great Mosel Riesling.",
    in_cellar: false,
  },
  {
    rank: 6,
    name: "Produttori del Barbaresco",
    mentions: 68,
    country: "Italy",
    region: "Barbaresco, Piedmont",
    varietal: "Nebbiolo",
    note: "A cooperative that outperforms estates twice its size. Single-vineyard Riservas are among Piedmont's best values. Importer: Polaner.",
    in_cellar: false,
  },
  {
    rank: 7,
    name: "Dönnhoff",
    mentions: 52,
    country: "Germany",
    region: "Nahe",
    varietal: "Riesling",
    note: "Helmut & Cornelius Dönnhoff. The Nahe's defining estate. Oberhäuser Brücke GG is ethereal; the entry-level Riesling is one of the world's great QPR wines. Importers: Skurnik / Theise.",
    in_cellar: false,
  },
  {
    rank: 8,
    name: "Louis Jadot",
    mentions: 52,
    country: "France",
    region: "Burgundy",
    varietal: "Pinot Noir / Chardonnay",
    note: "Négociant and estate. Reliable across a wide Burgundy range; Clos Saint-Jacques and Chambertin Clos de Bèze among top reds.",
    in_cellar: false,
  },
  {
    rank: 9,
    name: "Carlisle Winery",
    mentions: 48,
    country: "USA",
    region: "Russian River Valley, CA",
    varietal: "Zinfandel / Syrah / Petite Sirah",
    note: "Mike Officer. Focuses on old-vine sites across Sonoma. Among the most serious Zinfandel programs anywhere; Syrahs are world-class.",
    in_cellar: false,
  },
  {
    rank: 10,
    name: "Goodfellow Family Cellars",
    mentions: 48,
    country: "USA",
    region: "Willamette Valley, OR",
    varietal: "Pinot Noir / Chardonnay",
    note: "Winemaker-driven; extremely vineyard-specific single-site Pinots from the Chehalem Mountains and Ribbon Ridge AVAs.",
    in_cellar: false,
  },
];

const MAX_MENTIONS = PRODUCERS[0].mentions;

const FLAG = { USA: "🇺🇸", Germany: "🇩🇪", France: "🇫🇷", Italy: "🇮🇹" };

const REGION_COLOR = {
  "Sonoma, CA":              "#b45309",
  "Santa Cruz Mtns, CA":    "#92400e",
  "Sonoma Coast, CA":       "#a16207",
  "Russian River Valley, CA": "#b45309",
  Mosel:                    "#1d4ed8",
  Nahe:                     "#1e40af",
  "Barbaresco, Piedmont":   "#991b1b",
  Burgundy:                 "#6d28d9",
  "Willamette Valley, OR":  "#065f46",
};

export default function Top10BerserkersWidget() {
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("All");

  const countries = ["All", ...Array.from(new Set(PRODUCERS.map((p) => p.country)))];

  const visible = filter === "All"
    ? PRODUCERS
    : PRODUCERS.filter((p) => p.country === filter);

  const prod = selected !== null ? PRODUCERS.find((p) => p.rank === selected) : null;

  return (
    <div style={{ fontFamily: "Georgia, serif", maxWidth: 720, margin: "0 auto", padding: "24px 16px", color: "#1a1a1a" }}>

      {/* Header */}
      <div style={{ borderBottom: "2px solid #7c3aed", paddingBottom: 12, marginBottom: 20 }}>
        <div style={{ fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", color: "#7c3aed", marginBottom: 4 }}>
          WineBerserkers · Community Thread
        </div>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, lineHeight: 1.2 }}>
          Top 10 Producers in Your Cellar?
        </h1>
        <div style={{ marginTop: 8, fontSize: 12, color: "#6b7280", display: "flex", gap: 16, flexWrap: "wrap" }}>
          <span>{THREAD.posts.toLocaleString()} posts</span>
          <span>{THREAD.unique_producers.toLocaleString()} producers named</span>
          <span>{THREAD.total_mentions.toLocaleString()} total mentions</span>
          <span>{THREAD.span}</span>
        </div>
      </div>

      {/* Country filter */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        {countries.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            style={{
              padding: "4px 12px",
              borderRadius: 20,
              border: "1px solid",
              borderColor: filter === c ? "#7c3aed" : "#d1d5db",
              background: filter === c ? "#7c3aed" : "white",
              color: filter === c ? "white" : "#374151",
              fontSize: 12,
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            {c}
          </button>
        ))}
      </div>

      {/* List */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {visible.map((p) => {
          const isSelected = selected === p.rank;
          const barPct = Math.round((p.mentions / MAX_MENTIONS) * 100);
          const color = REGION_COLOR[p.region] ?? "#4b5563";

          return (
            <div
              key={p.rank}
              onClick={() => setSelected(isSelected ? null : p.rank)}
              style={{
                border: `1px solid ${isSelected ? color : "#e5e7eb"}`,
                borderRadius: 8,
                padding: "12px 14px",
                cursor: "pointer",
                background: isSelected ? "#faf5ff" : "white",
                transition: "border-color 0.15s, background 0.15s",
              }}
            >
              {/* Row */}
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                {/* Rank badge */}
                <div style={{
                  width: 28, height: 28, borderRadius: "50%",
                  background: p.rank <= 3 ? "#7c3aed" : "#f3f4f6",
                  color: p.rank <= 3 ? "white" : "#374151",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, fontWeight: 700, flexShrink: 0,
                }}>
                  {p.rank}
                </div>

                {/* Name + region */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 15, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {FLAG[p.country] ?? ""} {p.name}
                  </div>
                  <div style={{ fontSize: 11, color: "#6b7280", marginTop: 1 }}>
                    {p.region} · {p.varietal}
                  </div>
                </div>

                {/* Mentions + bar */}
                <div style={{ textAlign: "right", flexShrink: 0, minWidth: 70 }}>
                  <div style={{ fontSize: 15, fontWeight: 700, color }}>{p.mentions}</div>
                  <div style={{ fontSize: 10, color: "#9ca3af" }}>mentions</div>
                  <div style={{ marginTop: 3, height: 4, width: 70, background: "#f3f4f6", borderRadius: 2 }}>
                    <div style={{ height: "100%", width: `${barPct}%`, background: color, borderRadius: 2 }} />
                  </div>
                </div>
              </div>

              {/* Expanded note */}
              {isSelected && (
                <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid #e5e7eb", fontSize: 13, color: "#374151", lineHeight: 1.6 }}>
                  {p.note}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{ marginTop: 20, fontSize: 11, color: "#9ca3af", textAlign: "center" }}>
        Source: <a href={THREAD.url} style={{ color: "#7c3aed" }} target="_blank" rel="noopener noreferrer">WineBerserkers thread #{THREAD.url.split("/").pop()}</a>
        {" · "}vault snapshot 2026-06-29
      </div>
    </div>
  );
}
