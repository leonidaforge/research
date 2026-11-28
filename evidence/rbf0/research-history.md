# RBF0 research history

## 2026-11-25: fixed prefix length

RBF0-F02 originally stated that the first 12 bytes were identical in all samples. A newly decoded row with a 15-byte root name showed that only the first 10 bytes are invariant. Bytes `+0x0A..+0x0B` are the root name length. The body grammar replaced the earlier unknown tag placeholder, and the sample grew from 8 to 18 rows.

## 2026-11-25: finding F05 reassigned

RBF0-F05 originally listed byte-level tag observations. The decoded grammar replaced that claim; F05 now states the object stream form. The earlier observations are covered by RBF0-F08 (attributes), RBF0-F10 (terminators) and RBF0-F12 (string values).

## 2026-11-25: findings F04, F06 and F07 retained

F04 keeps the subject of the earlier name-structure claim and now states the per-payload name dictionary. F06 keeps the type ID 11 subject and adds that the type ID also carries `PSIN`, so it does not identify RBF0. F07 keeps the mode-1 raw DEFLATE subject and now covers 18 extractions. During the grammar revision the field-identifier and string-form findings were temporarily assigned F06 and F07; they are now F11 and F12.

## 2026-11-25: the fixed 10-byte prefix is a versioned header plus the first token

**Old reading.** Bytes `52 42 46 30 FB FF 01 00 00 00` were one fixed 10-byte prefix, with a `u32` value at `+0x06` and a root name length at `+0x0A`.

**Correction.** The `u32` was a `u16` version at `+0x06` followed by the first token `0x0000` at `+0x08`. The versioned header ends at `+0x08`; the token stream starts there. The root name length at `+0x0A` is the name definition for token index 0. Three payloads omit the `0xFFFB` marker, start the token stream at `+0x04`, and use 4-byte numbers. The sample grew to 238 unique payloads.

## 2026-11-25: the fixed 8-byte field is a typed value

**Old reading.** Field `0x1006` was a special fixed 8-byte value class, separate from string fields.

**Correction.** `0x1006` is a type 1 value token with name index 6. Type 1 values use the document number width: 8 bytes in versioned documents and 4 bytes in versionless documents. The special-case identifier set was removed.

## 2026-11-25: attributes are typed tokens, not a closed identifier set

**Old reading.** Attributes used identifiers `0x6003` and `0x6004`, and that pair was treated as the complete attribute vocabulary.

**Correction.** An attribute token is a name index plus a type code, the same word form as a body token. Observed attribute type codes are 1, 4 and 6, and observed attribute name indices span 1 to 39. The `0x6003` and `0x6004` words are type 6 tokens with name indices 3 and 4. The closed set is withdrawn.

## 2026-11-25: the eight-byte trailer is not universal

**Old reading.** Every payload ends with exactly eight `FF` bytes, read as four consecutive close words.

**Correction.** Every element ends with `0xFFFF`, and every payload ends with at least one close token, but the trailing `FF` run is 2 to 14 bytes across 238 unique payloads. Exactly eight bytes occur in 101 payloads. The four-word role assignment is not supported as a universal rule.

## 2026-11-25: subset parser replaced by the token grammar

**Old reading.** The parser accepted only objects, string fields, the `0x1006` fixed value and terminators, and reported other identifiers as unsupported.

**Correction.** The grammar is a token stream with one name table and type codes 0 to 6 plus the text and close tokens. An independent parser consumes 238 of 238 unique payloads. The original 18-row counts remain valid as a subset: 15,305 text nodes, 14,127 attributes and 44 type 1 values.

## 2026-11-28: text nodes end with a NUL that is not part of the text

**Old reading.** A text node's declared bytes are the value, verbatim.

**Correction.** The declared length includes one trailing `0x00`. Across the 1,462 payloads of `data.rpf`, 287,267 of 287,297 text nodes end with it, and the 30 that do not are also not valid UTF-8. A text value therefore ends before its final NUL (RBF0-F19). The same pass shows type-6 values carry no terminator at all: none of 110,051 ends with a NUL (RBF0-F20).

## 2026-11-28: type 6 occurs in body positions too

**Old reading.** Type 6 appeared only in counted attribute positions, and whether it may be a field value was Unknown.

**Correction.** Type-6 values appear in body positions throughout `data.rpf`. The token form is the same; only the position was unobserved before (RBF0-F20).

## 2026-11-28: type 1 and type 4 are different encodings

**Old reading.** Types 1 and 4 were both recorded as numbers of the document width, with their meaning Unknown.

**Correction.** Type 1 is a 64-bit integer and type 4 is an IEEE-754 binary64. The population decides it: the same value `1` is `01 00 00 00 00 00 00 00` as class 1 and `00 00 00 00 00 00 F0 3F` as class 4, class 4 is finite across all 39,291 observations in the range -431,602,080 to 65,536, and class 1 fits in `i32` in 30,655 of 30,663 observations. Read the other way round, each class would be nonsense (RBF0-F21). What a number describes remains Unknown.

## 2026-11-28: the 32-level nesting cap was a decoder limit, not a format limit

**Old reading.** The parser defaulted to 32 levels of nesting, which was treated as generous.

**Correction.** Four payloads of `data.rpf` nest deeper than 32 levels; the deepest is 35. A limit that refuses real documents is a bug in the limit, not a property of the format (RBF0-F22).

## 2026-11-28: the document is a tree, and the tree is markup

**Old reading.** The document purpose was Unknown, and the payloads were described as a token stream whose meaning could not be summarised.

**Correction.** The exhaustive walk of `data.rpf` decodes 1,462 of 1,462 payloads into trees of named elements. The 30 root families are UI description and tuning documents, and their vocabulary is the engine's UI vocabulary (RBF0-F25). The grammar is markup: elements nest, repeat to form lists, and hold attributes, values and text. Individual field semantics remain Unknown.
