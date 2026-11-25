# RBF0 research history

## 2026-11-25: fixed prefix length

RBF0-F02 originally stated that the first 12 bytes were identical in all samples. A newly decoded row with a 15-byte root name showed that only the first 10 bytes are invariant. Bytes `+0x0A..+0x0B` are the root name length. The body grammar replaced the earlier unknown tag placeholder, and the sample grew from 8 to 18 rows.

## 2026-11-25: finding F05 reassigned

RBF0-F05 originally listed byte-level tag observations. The decoded grammar replaced that claim; F05 now states the object stream form. The earlier observations are covered by RBF0-F08 (attributes), RBF0-F10 (terminators) and RBF0-F12 (string values).

## 2026-11-25: findings F04, F06 and F07 retained

F04 keeps the subject of the earlier name-structure claim and now states the per-payload name dictionary. F06 keeps the type ID 11 subject and adds that the type ID also carries `PSIN`, so it does not identify RBF0. F07 keeps the mode-1 raw DEFLATE subject and now covers 18 extractions. During the grammar revision the field-identifier and string-form findings were temporarily assigned F06 and F07; they are now F11 and F12.
