#!/usr/bin/env python3
"""Generate the office and hospital petition pages from index.html.

index.html is the single source of truth. Edit it, run `python3 build.py`,
and the other petition pages pick the change up.
"""
import io, sys, re

SRC = "index.html"

VARIANTS = {
 "office.html": dict(
    KIND="Office", NOUN="office", NOUNS="offices", NOUN_C="Office", NOUNS_C="Offices",
    WHO="employees", WHO_LONG="employees and staff", TAG="National workplace petition",
    H1="We are demanding <em>clean and healthy</em> food options in every office canteen in India.",
    TITLE="Canteen Sudharega India — Office canteens",
    DESC="We are demanding clean and healthy food in every office canteen in India. Sign the petition anonymously and grade your canteen.",
 ),
 "hospital.html": dict(
    KIND="Hospital", NOUN="hospital", NOUNS="hospitals", NOUN_C="Hospital", NOUNS_C="Hospitals",
    WHO="patients and staff", WHO_LONG="patients, visitors and staff", TAG="National hospital petition",
    H1="We are demanding <em>clean and healthy</em> food options in every hospital canteen in India.",
    TITLE="Canteen Sudharega India — Hospital canteens",
    DESC="We are demanding clean and healthy food in every hospital canteen in India. Sign the petition anonymously and grade your canteen.",
 ),
}

def active(s, page):
    """Mark the current tab, clearing the one index.html ships with."""
    s = s.replace('<a href="index.html" aria-current="page">', '<a href="index.html">')
    return s.replace('<a href="%s">' % page, '<a href="%s" aria-current="page">' % page)

def rep(s, old, new, label, required=True):
    n = s.count(old)
    if n != 1:
        if required: print("  MISS[%s] count=%d" % (label, n)); sys.exit(1)
        return s
    return s.replace(old, new)

def build(out, V):
    s = io.open(SRC, encoding="utf-8").read()
    K, N, NS, NC, NSC = V["KIND"], V["NOUN"], V["NOUNS"], V["NOUN_C"], V["NOUNS_C"]

    # ---- head ----
    s = rep(s, "<title>Canteen Sudharega India — Sign the petition</title>",
               "<title>%s</title>" % V["TITLE"], "title")
    s = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="%s">' % V["DESC"], s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">',
               '<meta property="og:description" content="%s">' % V["DESC"], s, count=1)
    s = re.sub(r'<meta name="twitter:description" content="[^"]*">',
               '<meta name="twitter:description" content="%s">' % V["DESC"], s, count=1)

    # ---- hide the two school/college toggles, mark the active tab ----
    s = rep(s, ".tapHint{margin:2px 0 8px}",
               ".tapHint{margin:2px 0 8px}\n.seg[aria-label=\"Institution type\"],.segboard{display:none!important}",
               "hide toggles")
    s = active(s, out)

    # ---- copy ----
    s = rep(s, "<span class=\"tag\">📣 National student petition</span>",
               "<span class=\"tag\">📣 %s</span>" % V["TAG"], "tag")
    s = rep(s, "<h1>We are demanding <em>clean and healthy</em> food options in every school and college canteen in India.</h1>",
               "<h1>%s</h1>" % V["H1"], "h1")
    s = rep(s, '<div class="lbl">students and parents have signed</div>',
               '<div class="lbl">Indians have signed</div>', "counter who")
    s = rep(s, '<div><b id="sCampus">0</b><span>campuses on the list</span></div>',
               '<div><b id="sCampus">0</b><span>%s on the list</span></div>' % NS, "counter label")
    s = rep(s, "<p class=\"board-sub\">Schools and colleges ranked by the number of people who signed, with the average report-card grade students and parents gave their canteen.</p>",
               "<p class=\"board-sub\">%s ranked by the number of people who signed, with the average report-card grade %s gave their canteen.</p>" % (NSC, V["WHO"]), "board sub")
    s = rep(s, 'placeholder="Search your school, college or city…"',
               'placeholder="Search your %s or city…"' % N, "search placeholder")
    s = rep(s, "Public voices backing the demand for hygienic, healthy canteens in every school and college.",
               "Public voices backing the demand for hygienic, healthy canteens in every %s." % N, "celebs sub")
    s = rep(s, "We publish only campus names, cities, counts and average grades.",
               "We publish only %s names, cities, counts and average grades." % N, "footer privacy")
    s = rep(s, '<p class="sub">Sign the petition for your campus. Takes under a minute.</p>',
               '<p class="sub">Sign the petition for your %s. Takes under a minute.</p>' % N, "sheet sub")
    s = rep(s, '<label class="f" for="inst" id="instLbl">College name</label>',
               '<label class="f" for="inst" id="instLbl">%s name</label>' % NC, "inst label")
    s = rep(s, 'placeholder="Start typing your college name"',
               'placeholder="Start typing your %s name"' % N, "inst placeholder")
    s = rep(s, '<label class="f" for="wish" id="wishLbl">If you could change one thing in your college canteen, what would it be? <small>(optional)</small></label>',
               '<label class="f" for="wish" id="wishLbl">If you could change one thing in your %s canteen, what would it be? <small>(optional)</small></label>' % N, "wish label")
    s = rep(s, "a movement holding schools and colleges accountable for clean, healthy food.",
               "a movement holding %s accountable for clean, healthy food." % NS, "done copy")
    s = rep(s, "<div><dt>Campus</dt><dd id=\"cInst\"></dd></div>",
               "<div><dt>%s</dt><dd id=\"cInst\"></dd></div>" % NC, "done campus label")
    s = rep(s, "<p>Every signature is counted against your campus. We reach out to the campuses on\n           this list as part of a nationwide student movement for better canteens.</p>",
               "<p>Every signature is counted against your %s. We reach out to the %s on\n           this list as part of a nationwide movement for better canteens.</p>" % (N, NS), "next copy")

    # ---- behaviour ----
    s = rep(s, 'const S = { type:"College", kind:"College",',
               'const S = { type:"%s", kind:"%s",' % (K, K), "state")
    s = s.replace('rpc("board", { max_rows: 400 })', 'rpc("board", { max_rows: 400, kinds: ["%s"] })' % K)
    s = rep(s, 'S.data.list.filter(r => +r[3] > 0 && (r[2] || "College") === S.kind)',
               'S.data.list.filter(r => +r[3] > 0 && (r[2] || "%s") === S.kind)' % K, "board filter")
    s = rep(s, 'const noun = S.kind === "School" ? "school" : "college";',
               'const noun = "%s";' % N, "status noun")
    s = rep(s, '(S.kind === "School" ? "No schools on the list yet. Yours could be first." : "No colleges on the list yet. Yours could be first.")',
               '"No %s on the list yet. Yours could be first."' % NS, "empty state")
    s = rep(s, '${items.length} ${S.kind === "School" ? "school" : "college"}',
               '${items.length} ${"%s"}' % N, "city header noun")
    s = rep(s, '<span>${S.kind === "School" ? "School" : "College"}</span>',
               '<span>%s</span>' % NC, "column header")
    s = rep(s, '✍️ Sign for my campus', '✍️ Sign for my %s' % N, "empty cta")
    s = rep(s, 'const school = S.type === "School";', 'const school = false;', "syncWording flag")
    s = rep(s, 'if (lbl) lbl.textContent = school ? "School name" : "College name";',
               'if (lbl) lbl.textContent = "%s name";' % NC, "syncWording label")
    s = rep(s, '''  if (inst) inst.placeholder = school
    ? "Start typing your school name" : "Start typing your college name";''',
               '  if (inst) inst.placeholder = "Start typing your %s name";' % N, "syncWording placeholder")
    s = rep(s, '''    wishLbl.innerHTML = (school
      ? "If you could change one thing in this school canteen, what would it be? "
      : "If you could change one thing in your college canteen, what would it be? ")
      + "<small>(optional)</small>";''',
               '    wishLbl.innerHTML = "If you could change one thing in your %s canteen, what would it be? <small>(optional)</small>";' % N,
               "syncWording wish")
    s = rep(s, '''  if (w) w.placeholder = school
    ? "e.g. fresh fruit instead of packaged snacks, or clean drinking water"
    : "e.g. a proper fruit and salad counter, or clean drinking water";''',
               '  if (w) w.placeholder = "e.g. a proper fruit and salad counter, or clean drinking water";',
               "syncWording wish placeholder")
    s = rep(s, 'SITE_URL: "https://dhritigupta7.github.io/canteen-sudharega-india"',
               'SITE_URL: "https://dhritigupta7.github.io/canteen-sudharega-india/%s"' % out, "site url")
    s = s.replace("gave our canteen at ${p.institution}", "gave our canteen at ${p.institution}")

    io.open(out, "w", encoding="utf-8").write(s)
    print("  wrote", out, len(s), "bytes")

if __name__ == "__main__":
    for out, V in VARIANTS.items():
        print("building", out)
        build(out, V)
    print("done")
