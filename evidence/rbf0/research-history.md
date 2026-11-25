# RBF0 research history

## 2026-11-25: fixed prefix length

RBF0-F02 originally stated that the first 12 bytes were identical in all samples. A newly decoded row with a 15-byte root name showed that only the first 10 bytes are invariant. Bytes `+0x0A..+0x0B` are the root name length. The body grammar replaced the earlier unknown tag placeholder, and the sample grew from 8 to 18 rows.
