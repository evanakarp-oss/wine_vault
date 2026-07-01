// Wine Berserkers — logged-in browser thread fetcher
// ---------------------------------------------------------------------------
// Wine Berserkers 403s the Python scraper (scrape_wb_thread.py) as a bot, but
// your *logged-in browser* is not blocked. This snippet walks the Discourse
// JSON API from inside your authenticated session and downloads a file in the
// exact shape parse_wb_thread.py consumes ({thread, posts}), so you can go
// straight to the parse step. No cookies or credentials ever leave the browser.
//
// HOW TO USE
//   1. Log in to wineberserkers.com in your browser.
//   2. Open the thread you want, e.g.
//        https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370
//   3. Open DevTools console (F12 / Cmd-Opt-J) and paste this whole file, Enter.
//   4. It walks every post in batches and downloads
//        <slug>.discourse.json   (e.g. top-10-producers-in-your-cellar.discourse.json)
//   5. Move that file to  raw/berserkers/threads/<slug>.discourse.json  and run:
//        python scripts/parse_wb_thread.py \
//          raw/berserkers/threads/<slug>.discourse.json \
//          --slug top10_in_cellar \
//          --title "Top 10 Producers in your cellar?" \
//          --thread-url <the thread URL> \
//          --merge-with raw/berserkers/threads/top10_in_cellar.json
//
// Optional: set WB_INCLUDE_RAW=false below if include_raw 403s for your account
// (cooked HTML is always available and the parser strips tags from it).

(async () => {
  const WB_INCLUDE_RAW = true;   // pull original markdown when your account allows it
  const BATCH_SIZE = 20;         // Discourse caps post_ids[] arrays ~20-30
  const THROTTLE_MS = 300;       // be polite between batches

  const KEEP = ["id", "username", "name", "post_number",
                "created_at", "updated_at", "raw", "cooked"];

  const m = location.pathname.match(/^\/t\/([^/]+)\/(\d+)/);
  if (!m) {
    console.error("Not on a Wine Berserkers /t/<slug>/<id> thread page. " +
                  "Open the thread first, then run this.");
    return;
  }
  const slug = m[1];
  const tid = Number(m[2]);
  const origin = location.origin;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const getJSON = async (url) => {
    const resp = await fetch(url, {
      headers: { "Accept": "application/json" },
      credentials: "include",
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status} for ${url}`);
    return resp.json();
  };

  const rawQ = WB_INCLUDE_RAW ? "?include_raw=true" : "";
  console.log(`Fetching thread ${tid} (${slug})…`);
  const main = await getJSON(`${origin}/t/${slug}/${tid}.json${rawQ}`);

  const title = main.title || main.fancy_title || slug;
  const stream = (main.post_stream && main.post_stream.stream) || [];
  const seed = (main.post_stream && main.post_stream.posts) || [];
  console.log(`Title: ${title}`);
  console.log(`Stream length: ${stream.length} posts`);

  const have = new Map(seed.map((p) => [p.id, p]));
  const missing = stream.filter((id) => !have.has(id));
  console.log(`Have ${have.size} from seed; fetching ${missing.length} more…`);

  for (let i = 0; i < missing.length; i += BATCH_SIZE) {
    const batch = missing.slice(i, i + BATCH_SIZE);
    const params = batch.map((id) => `post_ids[]=${id}`).join("&");
    const url = `${origin}/t/${tid}/posts.json?${params}` +
                (WB_INCLUDE_RAW ? "&include_raw=true" : "");
    try {
      const data = await getJSON(url);
      for (const p of (data.post_stream && data.post_stream.posts) || []) {
        have.set(p.id, p);
      }
    } catch (e) {
      console.warn(`  batch ${i}-${i + batch.length} failed: ${e.message} (retrying once)`);
      await sleep(THROTTLE_MS * 3);
      try {
        const data = await getJSON(url);
        for (const p of (data.post_stream && data.post_stream.posts) || []) {
          have.set(p.id, p);
        }
      } catch (e2) {
        console.error(`  batch ${i}-${i + batch.length} failed again: ${e2.message}`);
      }
    }
    const done = Math.min(i + BATCH_SIZE, missing.length);
    console.log(`  ${have.size}/${stream.length} posts`);
    await sleep(THROTTLE_MS);
  }

  const posts = stream
    .filter((id) => have.has(id))
    .map((id) => {
      const p = have.get(id);
      const out = {};
      for (const k of KEEP) if (k in p) out[k] = p[k];
      return out;
    });

  const payload = {
    thread: {
      title,
      url: `${origin}/t/${slug}/${tid}`,
      thread_id: tid,
      slug,
      post_count: posts.length,
    },
    posts,
  };

  const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"],
                        { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${slug}.discourse.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  console.log(`Done — downloaded ${slug}.discourse.json (${posts.length} posts). ` +
              `Move it to raw/berserkers/threads/ and run parse_wb_thread.py.`);
})();
