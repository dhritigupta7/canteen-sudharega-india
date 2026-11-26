/**
 * Canteen Sudharega India — Google Sheets backend
 * Paste into Extensions → Apps Script of your Google Sheet, run setup() once,
 * then Deploy → Web app (Execute as: Me, Who has access: Anyone). See SETUP.md.
 *
 * Sheet columns: Timestamp | Type | Institution | City | Grade | Reason | Tags | Photos | Hide
 * Fully anonymous: no names, emails or phone numbers are collected.
 * Photos are saved privately to a Google Drive folder in your account; only links go in the sheet.
 * Put an "x" in the Hide column to remove a row from the public list (spam, abuse, duplicates).
 */

const SHEET_NAME = 'Signatures';
const HEADERS = ['Timestamp', 'Type', 'Institution', 'City', 'Grade', 'Reason', 'Tags', 'Photos', 'Hide'];
const PHOTO_FOLDER = 'Canteen Sudharega India – Photos';
const POINTS = { A: 4, B: 3, C: 2, D: 1, F: 0 };
const CACHE_SECONDS = 30;

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
  }
  return sh;
}

function getFolder_() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('photoFolderId');
  if (id) { try { return DriveApp.getFolderById(id); } catch (e) {} }
  const folder = DriveApp.createFolder(PHOTO_FOLDER); // private to you by default
  props.setProperty('photoFolderId', folder.getId());
  return folder;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Trim, collapse spaces, cap length, and stop spreadsheet formula injection.
function clean_(v, max) {
  let s = String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, max);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function key_(s) {
  return String(s || '').toLowerCase().replace(/^'/, '').replace(/[^a-z0-9ऀ-ॿ]+/g, ' ').trim();
}

/** Public list: campus name, city, type, signature count and grade totals. Never reasons or photos. */
function doGet() {
  const cache = CacheService.getScriptCache();
  const hit = cache.get('stats');
  if (hit) return ContentService.createTextOutput(hit).setMimeType(ContentService.MimeType.JSON);

  const values = getSheet_().getDataRange().getValues();
  const map = {};
  for (let i = 1; i < values.length; i++) {
    const [ts, type, inst, city, grade, , , , hide] = values[i];
    if (!inst || !city || String(hide).trim()) continue;
    const k = key_(city) + '|' + key_(inst);
    // [name, city, type, signatures, gradePointsSum, gradeCount]
    if (!map[k]) map[k] = [String(inst).replace(/^'/, ''), String(city).replace(/^'/, ''), type || 'College', 0, 0, 0];
    map[k][3]++;
    const g = String(grade).trim().toUpperCase();
    if (g in POINTS) { map[k][4] += POINTS[g]; map[k][5]++; }
  }
  const body = JSON.stringify({ ok: true, updated: new Date().toISOString(), list: Object.values(map) });
  try { cache.put('stats', body, CACHE_SECONDS); } catch (e) { /* over 100 KB: skip cache */ }
  return ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
}

/** New petition signature. */
function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: 'Bad request.' }); }

  if (d.website) return json_({ ok: true });                       // honeypot filled = bot; pretend success
  if (Number(d.elapsed) < 2500) return json_({ ok: false, error: 'That was quick! Please try again.' });

  const type = d.type === 'School' ? 'School' : 'College';
  const inst = clean_(d.institution, 120);
  const city = clean_(d.city, 60);
  const grade = String(d.grade || '').toUpperCase();
  const reason = clean_(d.reason, 1000);
  const tags = clean_(d.tags, 200);

  if (inst.length < 3) return json_({ ok: false, error: 'Please enter your college or school name.' });
  if (city.length < 2) return json_({ ok: false, error: 'Please enter your city.' });
  if (!(grade in POINTS)) return json_({ ok: false, error: 'Please give your canteen a grade.' });
  if (reason.length < 10) return json_({ ok: false, error: 'Tell us what is wrong in a few words.' });

  // Optional photos: up to 3 JPEGs (already resized and stripped of location data by the website).
  const links = [];
  const photos = Array.isArray(d.photos) ? d.photos.slice(0, 3) : [];
  if (photos.length) {
    try {
      const folder = getFolder_();
      const stamp = Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyyyMMdd-HHmmss');
      photos.forEach((b64, i) => {
        if (typeof b64 !== 'string' || b64.length > 2500000) return; // ~1.8 MB cap per photo
        const blob = Utilities.newBlob(Utilities.base64Decode(b64), 'image/jpeg', `${stamp}_${key_(inst).slice(0, 40)}_${i + 1}.jpg`);
        links.push(folder.createFile(blob).getUrl());
      });
    } catch (err) { /* photo failed: still record the signature */ }
  }

  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(15000);
    getSheet_().appendRow([new Date(), type, inst, city, grade, reason, tags, links.join('\n'), '']);
  } catch (err) {
    return json_({ ok: false, error: 'Lots of people signing right now! Please try again in a moment.' });
  } finally {
    lock.releaseLock();
  }
  return json_({ ok: true });
}

/** Run once from the editor: creates the sheet and photo folder, and approves permissions. */
function setup() {
  getSheet_();
  getFolder_();
}
