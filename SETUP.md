# Canteen Sudharega India

Live site: https://dhritigupta7.github.io/canteen-sudharega-india/
Video CTA link: https://dhritigupta7.github.io/canteen-sudharega-india/#sign

## How it is put together
- `index.html` — the whole website. Hosted free on GitHub Pages from this repo's `main` branch.
- Backend — Supabase project `canteen-sudharega-india` (region: Mumbai, free plan).
  Project ref `ekvcvnzttxbmkevhjubn`. The old Google Apps Script backend has been removed;
  nothing touches Google Sheets or Drive any more.

Push to `main` and the live site updates within about a minute.

## Where the data lives
Supabase → Table editor:
- **institutions** — one row per campus, with its signature count and grade totals.
- **signatures** — every individual signature, with the reason. Never shown publicly.
- **merge_suggestions** — campus names that look like duplicates and need your eye.

Useful views in the SQL editor:
```sql
select * from admin_signatures limit 100;   -- every signature, newest first, with reasons
select * from pending_merges;               -- duplicate campus names awaiting your decision
```

## Keeping the counts accurate
Campus names are matched on four levels, so "CHRIST UNIVERSITY", "christ university"
and "Christ-University" are all one campus with one count:

1. **Strict key** — case, accents, punctuation, apostrophes and spacing are ignored.
   `St. Xavier's College` = `St Xaviers College`.
2. **Loose key** — abbreviations expanded (`Univ`→`University`, `Clg`→`College`, `St`→`Saint`),
   filler words dropped, initials glued (`I.I.T.`→`IIT`), word order ignored.
   An exact match here is **merged automatically**.
3. **Fuzzy similarity** — anything 82%+ similar is listed in `pending_merges` for you to approve.
   Not automatic, because `St Xaviers Mumbai` and `St Xaviers Kolkata` are different colleges.
4. **Autocomplete** — as someone types, the form offers campus names already on record,
   so they pick the existing spelling instead of inventing a new one. This prevents most duplicates.

Campus names are always matched **within a city**, never across cities.

## Day-to-day jobs (run in Supabase → SQL editor)
```sql
-- approve a suggested merge
select approve_merge(<id from pending_merges>);

-- merge two campuses by hand
select merge_institutions(<keep_id>, <duplicate_id>);

-- undo any merge, exactly
select unmerge_institution(<duplicate_id>);

-- hide spam, abuse or a joke entry
select hide_signature('<signature uuid>');

-- hide an entire fake campus
select hide_institution(<institution id>);

-- fix an ugly or wrong campus name
select rename_institution(<institution id>, 'Christ University');

-- after editing the abbreviation list, re-key everything
select renormalize_all();

-- reconcile counts if anything ever looks off
select recount_all();
```

## Privacy
- No names, emails or phone numbers are collected.
- The device id and IP address are stored only as salted SHA-256 hashes, used for
  "one signature per campus per device" and for rate limiting.
- Run `select purge_old_ip_hashes();` periodically; it clears IP hashes older than 7 days.
- Photos go to a **private** Storage bucket called `evidence`. The website's key can
  upload into it but cannot read it back. View them in Supabase → Storage.
- Reasons are never shown on the website. People sometimes type names into them, so
  do not share the raw table publicly.

## Limits of the free plan
- 500 MB database. A signature is roughly 0.5 KB, so ~1 million signatures.
- **5 GB egress per month.** This is the real ceiling. Every page load fetches the
  board (~25 KB), so roughly 200,000 page loads per month. Watch
  Supabase → Reports → Egress in the first days after the video.
  If it climbs, the fixes in order are: lower `max_rows` in `board()`,
  raise `REFRESH_MS` in `index.html`, then put a Cloudflare Worker cache in front.
- Writes are not the constraint; reads are.

## The four pages
- `index.html` — schools and colleges petition (**the source of truth**)
- `office.html`, `hospital.html` — **generated** from index.html by `build.py`
- `pledge.html` — the institutional pledge, a separate standalone page

**After editing index.html, run `python3 build.py`** to regenerate the office and
hospital pages, then commit all three. Do not edit office.html or hospital.html
by hand; your changes will be overwritten.

Each petition page reads only its own kind: `board()` takes a `kinds` argument,
defaulting to schools and colleges, so the pages never show each other's data.

## Pledges
`pledges` is a separate table. Unlike a signature it is **not anonymous** — it
carries a named contact and email so a pledge cannot be filed in someone else's
name. Contact details are never shown publicly.

```sql
select * from admin_pledges;                     -- everything, newest first
update pledges set verified = true where id='…';  -- after you confirm one
update pledges set hidden = true   where id='…';  -- hide a fake or joke entry
```
Only pledges with `publish_consent = true` appear on the public wall.
