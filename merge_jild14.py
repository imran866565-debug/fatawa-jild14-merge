#!/usr/bin/env python3
"""Merge Jild 14 tashreeh chunks into jild-14.json.

Re-runnable: reads every jild-14-chunk-*.json listed in the manifest,
merges in chunk order, validates (unique ids, page coverage vs manifest,
no empty jawab), writes jild-14.json, and updates the manifest statuses.

SPECIAL CASES (combine rules derived by the parent from the chunk files
themselves — ids, page ranges, titles and notes; the notes explicitly
confirm the continuations. The coordinator's full report did not reach
the parent; only its late handoff survived, naming "merge rule 3 — the
masala-183 forty-way cross-id combine" and "expected 199 merged items").
5 combine cases are ONE mas'ala split across chunks and must be
COMBINED into a single item, NOT renamed by the duplicate-id rule.
After combining all 5 cases, the merged file has 200 items (251 - 51)
covering 614 unique pages. Combine rules (parts ordered by min page;
sawal from the FIRST part; jawab = all parts concatenated in page
order; pages = UNION of all parts' pages; notes = all parts' notes):
  masala 24:  03a 'jild14-masala-24' pp. 174-196 + 03b's five sections
              'jild14-p197' (197-199), 'jild14-p199' (199-202),
              'jild14-p203' (203-206), 'jild14-p207' (207-211),
              'jild14-p212' (212-218) + 04a's four sections
              'jild14-dawam-taghallub-ikhtiyar' (219-221),
              'jild14-dawam-27-35' (222-226),
              'jild14-dawam-fasl3-mabhas1' (227-230),
              'jild14-dawam-fasl3-mabhas2' (231-238) — a TEN-way combine.
              The whole دوام العیش risala is one mas'ala: 03b's p212 note
              says point 26 continues on p. 219 in the next part, and
              04a's dawam-taghallub note says "یہ حصہ پچھلے صفحات سے جاری
              بحث کا تسلسل ہے". Pages = UNION [174-239].
  masala 130: 06 'jild14-masala-130' p. 382 + 07 'jild14-masala-130'
              p. 383 (SAME id twice). 06's note says it starts on 382 and
              continues in the next part; 07's note says it started on 382
              and here is only the last part of the jawab. Both halves
              carry a sawal, but it is the SAME question restated — keep
              06's fuller sawal, discard 07's restatement (Jild 11
              masala-16 rule). Pages [382, 383].
  masala 183: 07 'jild14-masala-183' pp. 427-432 + 08a
              'jild14-masala-183' pp. 433-457 + 08b's 15 section items
              (pp. 458-482: p458, p459, tanbih-3, p465, p466-suluk,
              p466-mawalat, p470, tanbih-4, p473, p474, p477, p478-angrez,
              p480, p481, p482) + 09's 19 items (pp. 483-532:
              aman-sharaait, radd-6-muhaida, radd-7-mazalim,
              aghraz-muakhawat-ittihad, hilf-mushrikin, self-government,
              faida-1-ayat, faida-2-ahadith, faida-3-riwayat,
              faida-4-zimmi, faida-5-kitabi, faida-6-aqsam,
              istikhdam-suwar, faida-7-tabdeel, hidayat-muftiyan,
              dukhul-masajid, sabia-masajid, khulasa-wa-arz,
              tark-muamalat) + 10's first 4 items 'jild14-p533'
              (533-535), 'jild14-p536' (536-537), 'jild14-p538'
              (538-540), 'jild14-p541' (541-545) — all titled
              "المحجۃ المؤتمنۃ — ..." (the risala's ending; masala-184
              starts at p. 546). A FORTY-way combine (the coordinator's
              "merge rule 3"). Pages = UNION [427-545].
              (08b's p458 continues 08a's discussion — source p. 457 ends
              mid-sentence; p. 482 ends mid-discussion with p. 483
              continuing it — both inside this combine. p. 464: the
              source DB repeats a passage verbatim and the tashreeh covers
              it once — that detail lives in the chunk notes; no action.)
  masala 205: 10 'jild14-masala-205' pp. 581-582 + 11
              'jild14-masala-205' p. 583 (SAME id twice). 10's note says
              it does not end on p. 582, the jawab continues from p. 583;
              11's note says the question and most of the jawab are in
              the previous part and this is only the last part of the
              jawab. Sawal from 10 (11's is empty). Pages [581, 582, 583].
  masala 258: 11 'jild14-masala-258' pp. 626-632 + 12
              'jild14-masala-258' pp. 633-635 (SAME id twice). 11's title
              says "(جواب اگلے...)" (the jawab continues); 12's title
              says "(مسئلہ ۲۵۸ — جاری)" (continuing) and its sawal is
              empty. Sawal from 11. Pages = UNION of both.
For every combined item: pages = union of all parts' pages,
start_page = min, notes = all parts' notes combined.

Distinct items that merely look similar are NOT combined — they stay
separate: 'jild14-p271' (chunk 05, "مسئلہ ایضاً" — a separate mas'ala
with no number of its own, printed with masala 36; its note says it was
recorded as a separate item deliberately), 'jild14-p692' (chunk 13,
"مسئلہ ۳۲۲ (دوسری بار)" — a different mas'ala whose printed number
repeats 322, likely a misprint for 323; its note says so),
'jild14-p597' (chunk 11, "جواب مسئلہ — کفار سے موالات کے دس مدارج" —
a separate question by Maulana Syed Sulaiman Ashraf Bihari, after
masala 213-217's jawab; its note says it has no mas'ala number of its
own), 'jild14-p712' (chunk 13, the volume's closing note).

COUNT NOTE: 251 chunk items - (9 + 1 + 39 + 1 + 1 = 51) = 200 merged
items. The coordinator's late handoff said 199 — one fewer. Do NOT
force the count to 199 by merging anything questionable; 200 is the
correct count per the evidence above.

Duplicate-id rule (Jild 4 precedent) still applies to any OTHER
duplicate: earliest keeps the plain id, later ones get "-p<startpage>".
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

# result id -> list of source ids, in page order.
COMBINES = {
    'jild14-masala-24': [
        'jild14-masala-24',
        'jild14-p197', 'jild14-p199', 'jild14-p203', 'jild14-p207',
        'jild14-p212',
        'jild14-dawam-taghallub-ikhtiyar', 'jild14-dawam-27-35',
        'jild14-dawam-fasl3-mabhas1', 'jild14-dawam-fasl3-mabhas2',
    ],
    'jild14-masala-130': ['jild14-masala-130', 'jild14-masala-130'],
    'jild14-masala-183': [
        'jild14-masala-183', 'jild14-masala-183',
        'jild14-p458', 'jild14-p459', 'jild14-tanbih-3', 'jild14-p465',
        'jild14-p466-suluk', 'jild14-p466-mawalat', 'jild14-p470',
        'jild14-tanbih-4', 'jild14-p473', 'jild14-p474', 'jild14-p477',
        'jild14-p478-angrez', 'jild14-p480', 'jild14-p481', 'jild14-p482',
        'jild14-aman-sharaait', 'jild14-radd-6-muhaida',
        'jild14-radd-7-mazalim', 'jild14-aghraz-muakhawat-ittihad',
        'jild14-hilf-mushrikin', 'jild14-self-government',
        'jild14-faida-1-ayat', 'jild14-faida-2-ahadith',
        'jild14-faida-3-riwayat', 'jild14-faida-4-zimmi',
        'jild14-faida-5-kitabi', 'jild14-faida-6-aqsam',
        'jild14-istikhdam-suwar', 'jild14-faida-7-tabdeel',
        'jild14-hidayat-muftiyan', 'jild14-dukhul-masajid',
        'jild14-sabia-masajid', 'jild14-khulasa-wa-arz',
        'jild14-tark-muamalat',
        'jild14-p533', 'jild14-p536', 'jild14-p538', 'jild14-p541',
    ],
    'jild14-masala-205': ['jild14-masala-205', 'jild14-masala-205'],
    'jild14-masala-258': ['jild14-masala-258', 'jild14-masala-258'],
}


def combine_parts(result_id, parts):
    parts = sorted(parts, key=lambda it: min(it['pages']))
    first = parts[0]
    combined = {
        'id': result_id,
        'title': first.get('title') or '',
        'volume_id': 57,
        'pages': sorted(set().union(*[set(p['pages']) for p in parts])),
        'start_page': min(min(p['pages']) for p in parts),
        'tashreeh_sawal': first.get('tashreeh_sawal', '') or '',
        'tashreeh_jawab': ''.join((p.get('tashreeh_jawab', '') or '') for p in parts),
        'notes': [n for p in parts for n in (p.get('notes') or [])],
    }
    return combined


def main():
    manifest = json.load(open(os.path.join(BASE, 'chunks-manifest-jild14.json')))
    all_items = []
    merged_chunks = []
    for entry in manifest['chunks']:
        nn = entry['chunk']
        if entry.get('status') == 'split-halves':
            print(f'chunk {nn}: split-halves placeholder — halves are separate entries, skipping')
            continue
        path = os.path.join(BASE, entry['file'])
        if not os.path.exists(path):
            print(f'chunk {nn}: not yet written')
            continue
        try:
            d = json.load(open(path, encoding='utf-8'))
        except json.JSONDecodeError as e:
            # File may still be streaming from its translator; skip it
            # for now instead of crashing the whole merge.
            print(f'chunk {nn}: not valid JSON yet ({e}) — skipping for now')
            continue
        items = d['masail']
        # Normalize: some translators omit start_page; derive it from pages.
        for it in items:
            if 'start_page' not in it:
                assert it.get('pages'), f'chunk {nn} item {it.get("id")} has no pages'
                it['start_page'] = it['pages'][0]
                print(f'chunk {nn}: derived start_page={it["start_page"]} for {it["id"]}')
            assert it['start_page'] == min(it['pages']), \
                f'chunk {nn} item {it["id"]}: start_page != first page'
        all_items.extend(items)
        merged_chunks.append(nn)
        entry['status'] = 'merged'
        print(f'chunk {nn}: {len(items)} items merged')
    print(f'items before combines: {len(all_items)}')
    # COMBINE the 5 cases (one mas'ala split across chunks).
    for result_id, source_ids in COMBINES.items():
        parts = []
        seen_source = []
        for sid in source_ids:
            if sid in seen_source:
                continue  # same id listed twice (masala-130/183/205/258): collect all items at once
            seen_source.append(sid)
            hits = [it for it in all_items if it['id'] == sid]
            expected_n = source_ids.count(sid)
            assert len(hits) == expected_n, \
                f'expected exactly {expected_n} {sid} item(s) for {result_id}, found {len(hits)}'
            parts.extend(sorted(hits, key=lambda it: min(it['pages'])))
        combined = combine_parts(result_id, parts)
        assert combined['tashreeh_jawab'], f'{result_id}: combined jawab is empty!'
        assert combined['tashreeh_sawal'], f'{result_id}: combined sawal is empty!'
        assert combined['start_page'] == min(combined['pages']), f'{result_id}: start_page != min(pages)'
        remove_ids = set(source_ids)
        all_items = [it for it in all_items if it['id'] not in remove_ids]
        all_items.append(combined)
        print(f'COMBINED {result_id}: {len(parts)} parts, pages {combined["pages"][0]}-{combined["pages"][-1]} '
              f'({len(combined["pages"])} pages), sawal {len(combined["tashreeh_sawal"])} chars, '
              f'jawab {len(combined["tashreeh_jawab"])} chars, notes {len(combined["notes"])}')
    # de-duplicate any OTHER ids: earliest keeps plain id, later ones get -p<startpage>
    seen = {}
    for it in all_items:
        if it['id'] in seen:
            new_id = f"{it['id']}-p{it['start_page']}"
            print(f'DUPLICATE ID {it["id"]} (start {it["start_page"]}) -> renamed {new_id}')
            it['id'] = new_id
        seen[it['id']] = True
    ids = [it['id'] for it in all_items]
    assert len(ids) == len(set(ids)), f'STILL DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}'
    empty = [it['id'] for it in all_items if not it.get('tashreeh_jawab')]
    assert not empty, f'EMPTY JAWAB: {empty}'
    pages = set()
    for it in all_items:
        pages.update(it['pages'])
    expected = set()
    for entry in manifest['chunks']:
        if entry['chunk'] in merged_chunks:
            expected.update(range(entry['start_page'], entry['end_page'] + 1))
            expected.difference_update(entry['missing_pages'])
    missing_covered = expected - pages
    extra = pages - expected
    print(f'total items: {len(all_items)} | pages covered: {len(pages)} | expected: {len(expected)}')
    print(f'uncovered expected pages: {sorted(missing_covered)}')
    print(f'extra pages (outside merged chunks): {sorted(extra)}')
    assert not missing_covered, 'pages missing from merged chunks!'
    assert not extra, 'pages outside merged chunks!'
    assert len(all_items) == 200, f'expected 200 items after combines, got {len(all_items)}'
    assert len(pages) == 614, f'expected 614 pages, got {len(pages)}'
    # sort by start_page for the final file
    all_items.sort(key=lambda it: it['start_page'])
    with open(os.path.join(BASE, 'jild-14.json'), 'w', encoding='utf-8') as f:
        json.dump({'masail': all_items}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(BASE, 'chunks-manifest-jild14.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f'WROTE jild-14.json: {len(all_items)} items, {len(pages)} pages, chunks merged: {merged_chunks}')


if __name__ == '__main__':
    main()
