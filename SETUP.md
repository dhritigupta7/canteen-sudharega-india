# Canteen Sudharega India: going live in about 15 minutes

Two files:
- `index.html`: the website
- `Code.gs`: the backend, which saves every signature into a Google Sheet you own

## 1. Make the Google Sheet (5 min)
1. Create a new Google Sheet, named e.g. "Canteen Sudharega India – Signatures".
2. **Extensions → Apps Script**. Delete what's there, paste all of `Code.gs`, and click Save.
3. In the function dropdown pick `setup` and click **Run**. Approve the permissions (Sheets and Drive: Drive is where the optional photos are saved). Google shows an "unverified app" warning because you wrote the script yourself; click Advanced → Go to project. This creates the `Signatures` tab and a private Drive folder called "Canteen Sudharega India – Photos".
4. **Deploy → New deployment →** gear icon → **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click Deploy, then copy the **Web app URL** (ends in `/exec`).

## 2. Connect the website (1 min)
Open `index.html` in any text editor and find the SETTINGS block near the bottom:
```js
API_URL: "https://script.google.com/macros/s/XXXX/exec",
SITE_URL: "https://canteensudharega.netlify.app"
```

## 3. Put it online for free (3 min)
The easiest option is **Netlify Drop** (app.netlify.com/drop). Drag the folder containing `index.html` onto the page and you get a live link. Sign up (free) so you can rename it, e.g. `canteensudharega.netlify.app`, and later attach a custom domain.
Alternatives: GitHub Pages, Vercel, Cloudflare Pages. All free.

After you have the link, put it in `SITE_URL` and drag the folder again.

## 4. Links to use in your video and bio
- `yoursite/#sign` opens the petition form straight away, saving one tap. **Use this one in the video CTA.**

## Running it day to day
- **Spam / abuse / joke entries:** type `x` in the **Hide** column. That row disappears from the public list within 30 seconds.
- **Duplicate spellings** ("IIT B" vs "IIT Bombay"): edit the Institution cell so they match. Case and punctuation are already ignored, so "St Xaviers" and "St. Xavier's" merge automatically. The form also autocompletes existing names, which prevents most duplicates.
- **Photos** are saved in your private Drive folder, and the Sheet's Photos column links to them. Location data is removed before upload. Look through them before using any in your content.
- **Grades:** each campus's average grade on the website is worked out from the A–F grades (A=4 … F=0) and rounded to the nearest letter.
- **Reasons** stay only in your Sheet. The website never shows them. No names, emails or phone numbers are collected, so submissions are fully anonymous.
- **Changed `Code.gs`?** Deploy → Manage deployments → pencil icon → Version: *New version* → Deploy. Your URL stays the same.

## Limits worth knowing
- Google Apps Script handles a few thousand signatures a day comfortably. If the video goes truly viral (tens of thousands in an hour), some people will see "try again in a moment". At that point move the backend to Firebase or Supabase. The website needs only the two `fetch` calls changed.
- Spam protection is lightweight: a hidden bot trap, a minimum fill time, a required reason, and one entry per campus per device. It stops casual timepass, but it can't stop a determined person. Watch the sheet in the first few days.
- Submissions are anonymous, but people may still type names into the reason box. Hide any such row and don't share the raw Sheet publicly.
