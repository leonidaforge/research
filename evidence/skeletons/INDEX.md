# Skeleton evidence index

Payload observations from the Scarlett build
[e95020b2](../../builds/gta-vi/scarlett-e95020b2/README.md). No executable code
path was traced for this subject. Every finding is **Private-evidence
supported**: it is checkable against a local installation but not from this
repository alone.

The subject is the skeleton record referenced by a drawable header. Findings are
cited from
[formats/resources/skeletons/README.md](../../formats/resources/skeletons/README.md).

## Coverage

Two corpora were read through the native archive path. `data.rpf!26` and
`levels.rpf!5` hold the 3,211 rows that carry the four samples below. A second
census of 27 archived containers read 7,309 type-2 and type-3 rows and is what
corrected SKEL-F02, SKEL-F05 and SKEL-F06.

| Quantity                                   | Narrow corpus | Wide corpus |
| ------------------------------------------ | ------------- | ----------- |
| Rows read                                  | 3,211         | 7,309       |
| Skeletons present                          | 3,138         | 5,628       |
| Null skeleton slots                        | 73            | 1,681       |
| Bone counts observed                       | 1..42         | 1..596      |
| Roots per skeleton                         | 1             | 1..16       |
| Hierarchy depths observed                  | 1..21         | 1..35       |
| Skeletons with any structural issue        | 0             | 2           |
| Decoded-LOD geometries declaring bones     | 3,425         | 10,106      |
| Influence sets validated                   | 3,425         | 8,304       |
| Weighted geometries                        | 100           | 425         |

Both structural issues in the wide corpus are the two skeletons whose walk ran
past the bone allocation; the neighbouring arrays bound the count and the extra
record is dropped with `BoneArrayOverrun`. See SKEL-F16.

## Findings

| ID        | Finding                                                                                                                                                                                     | Evidence                        | Confidence                         | Limits                                                        |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------- | ------------------------------------------------------------- |
| SKEL-F01  | A drawable references its skeleton through the header slot at `+0x18`; the slot is a system pointer or null.                                                                                 | Payload data, cross sample      | Confirmed                          | The slot is absent from non-drawable roots                    |
| SKEL-F02  | The skeleton header holds zeros at `+0x00` and `+0x08`, the constant `1` at `+0x10` and `0x20` at `+0x18`, a key count at `+0x1C` and six pointers. | Payload data, cross sample | Confirmed (values) / Unknown (meanings) | Meaning of `+0x10` and `+0x18` Unknown; `+0x1C` is short of twice the bone count on 24 of 5,628 skeletons |
| SKEL-F03  | Six system pointers follow: a key map at `+0x20`, bones at `+0x28`, inverse bind at `+0x30`, local matrices at `+0x38`, parents at `+0x40` and names at `+0x48`.                              | Payload data, cross sample      | Confirmed                          | Key map decoded only as `(u32, u32)` pairs                    |
| SKEL-F04  | A bone record is 0x50 bytes with a quaternion at `+0x00`, translation at `+0x10`, a 32-bit identifier at `+0x1C`, scale at `+0x20`, a name pointer at `+0x30` and four `u16` at `+0x40` and `+0x48`. | Payload data, 5,628 skeletons | Confirmed                          | The flag word at `+0x40` and `+0x44` are Unknown              |
| SKEL-F05  | The bone count is not stored as a field: the first `u16` of a record's trailing group is its index, so the walk ends where the sequence breaks. The header word at `+0x1C` is twice the bone count on 5,604 of 5,628 skeletons and short by 1 or 2 on the rest. | Cross sample, 5,628 skeletons | Confirmed | The fourth `u16` behaves like a subtree-end jump whose meaning is Unknown |
| SKEL-F06  | The parent index is the fourth `u16` at `+0x46`; `0xFFFF` marks a root. The `+0x40` array repeats the same parents independently. One of 5,628 skeletons disagrees between the two statements.                                                                  | Cross sample, 5,628 skeletons | Confirmed                          | No cause was established for the single disagreement |
| SKEL-F07  | The quaternion is `x, y, z, w` in a right-handed, column-vector convention: child translation rotated by the parent rotation reproduces the stored model positions.                          | Cross sample                    | Confirmed                          | Proved through SKEL-F08, not from engine code                 |
| SKEL-F08  | The `+0x38` array stores transpose(local rotation) and the local translation; the `+0x30` array stores the model-space rotation and `-R_model^T * t_model`, the translation half of the inverse bind matrix. | Cross sample, 6-level peacock tail | Confirmed                      | Matrix record's last value Unknown                            |
| SKEL-F09  | Local transforms compose as `R_model = R_parent * R_local` and `t_model = t_parent + R_parent * t_local`.                                                                                   | Cross sample                    | Confirmed                          | None observed                                                 |
| SKEL-F10  | The stored inverse-bind records validate against the composed pose with a largest observed delta of `0` at the stored precision, on all sampled skeletons.                                   | Cross sample                    | Confirmed                          | A separately authored pose is not present                     || SKEL-F11  | Geometry records declare a bone count at `+0x2C`. It equals the skeleton bone count on highest-LOD geometries and is zero on lower LODs.                                                    | Cross sample                    | Confirmed                          | The same field is untested on non-skinned geometry            |
| SKEL-F12  | The vertex-buffer declaration table is a fixed 23-slot array and the slot is the attribute's semantic: slot 6 carries four `u8` blend weights (format `0x26`) and slot 8 the blend indices. The index encoding is the pair of declaration format and layout size, and five pairs occur: `0x25`/4 four `u8` (8,254 geometries), `0x8C`/16 four `u32` (104), `0x4A`/8 two `u32` (15), `0x00`/1 one `u8` (446) and `0x00`/2 one `u16` (55). | Cross sample, 10,106 geometries | Confirmed for slots 6 and 8 | An earlier reader stopped at the first zero word and misread slot 6 as a layout attribute; that reading is withdrawn |
| SKEL-F13  | Weight totals are 255 in most vertices, 127 on a minority, and rarely unnormalised (169 on four vertices of one geometry). The association uses the non-zero lanes and never rescales them.  | Cross sample                    | Confirmed                          | The normalisation rule is Unknown                             |
| SKEL-F14  | A one-bone skeleton needs no index stream: every sampled vertex weights lane 0 with 255. A missing index stream is accepted only in that case. 753 of 10,106 geometries are in that state; no surveyed geometry stores weights without an index attribute. | Cross sample, 10,106 geometries | Confirmed | The 479 multi-bone geometries with no influence attribute at all stay unassociated |
| SKEL-F15  | A skeleton may hold several roots: 5,080 of 5,628 have one, 58 have two, and the rest up to 16. The extra roots are helper bones (`XH_SecondarySurface`, `OH_EyelineDirection_01`, `OH_TorsoDirection_01`) that head their own short chains. | Cross sample, 5,628 skeletons | Confirmed | The helper-bone families are named, not classified |
| SKEL-F16  | The bone array is bounded by the arrays that follow it, because each holds one record per bone and its start is stored. 2,303 of 5,628 skeletons have the next array starting exactly at the end of the bone records; no skeleton exceeds the limit the tiling arrays imply. Two skeletons walked one record too far and are trimmed and reported. | Cross sample, 5,628 skeletons | Confirmed | A truncated array that keeps a consistent index sequence is only caught by the neighbouring arrays |
| SKEL-F17  | Scale is `(1, 1, 1)` in all 133,110 surveyed bones. Neither stored matrix carries a scale, and the composition applies none. | Cross sample, 133,110 bones | Confirmed for the corpus | Non-identity scale is unsupported, not disproved |
| SKEL-F18  | 4,016 surveyed one-bone geometries split into 3,263 with a weight form and 753 without. All 753 belong to one-bone skeletons and their geometry records hold no bone index, bone-array pointer or palette pointer, so the reading rests on the declared count matching the skeleton. | Cross sample, 10,106 geometries | Confirmed | Accepted only where the two counts agree; 479 multi-bone geometries with no influence attribute stay unassociated |
| SKEL-F19  | Each model stores an axis-aligned box per geometry. Decoded vertices match it where it exists: peacock 4 of 4 (`2.0e-5`), candlestick 2 of 2 (`2.0e-6`); the tarot and bolt records declare no box. | Four fragments, decoded against declared boxes | Confirmed for the four | A missing box leaves the vertex space unestablished, not disproved |
| SKEL-F20  | No bone palette accompanies an influence stream: the geometry record's fields at `+0x28`, `+0x2A`, `+0x2E`, `+0x30`, `+0x34`, `+0x38` and `+0x3C` hold no bone index and no palette pointer, and the model's `+0x28` slot does not read as a `u8` or `u16` bone list. Blend indices name the skeleton's own array positions. | Cross sample, 10,106 geometries | Confirmed for the corpus | A palette outside the corpus is not excluded; the reader carries a palette variant no decoder produces |
| SKEL-F21  | 501 geometries store one blend index per vertex and no weight stream: 446 as one `u8`, 55 as one `u16`. All declare more than one bone, every index is inside the declared count, the largest is 319 and no geometry repeats a single index, so each vertex selects one bone with weight 1. | Cross sample, 10,106 geometries | Confirmed | Weight 1 is structural: there is no weight stream to contradict it |
| SKEL-F22  | The authored vertices are the deformed result at the reference pose. Skinning composes as `S[i] = G_pose[i] * inverse-bind[i]` over the verified hierarchy, and a GPU compute probe matches a CPU reference on real data: the peacock tail (25,456 vertices) within `3.6e-7` m at a 40 degree pose, the candlestick (788 vertices) within `3.7e-9` m. | Two chains, 26,244 vertices | Confirmed for the samples | Linear blend skinning only; the data holds no authored animation pose |

## Sample locators

The selectors are the original native paths. `levels.rpf!5!0` means: open
`levels.rpf`, descend into the archive in row 5, then open row 0.

| Resource           | Selector          | Member drawable                  | Split    | Bones | Roots | Depth | Weighted | Inverse bind |
| ------------------ | ----------------- | -------------------------------- | -------: | ----: | ----: | ----: | -------- | ------------ |
| Tarot deck         | `levels.rpf!5!0`  | `prop_am_card_tarot_deck_01a.#ft` | `0x1980` |     3 |     1 |     3 | no       | 3 of 3       |
| Candlestick        | `levels.rpf!5!1`  | `prop_am_candlestick_02a.#ft`     | `0x3cc0` |     4 |     1 |     4 | no       | 4 of 4       |
| Weapon bolt        | `data.rpf!26!9`   | `w_sg_goodwin_01_bolt_01_mid.#ft` | `0x1c30` |     3 |     1 |     3 | no       | 3 of 3       |
| Peacock taxidermy  | `levels.rpf!5!8`  | `mint_peacock_taxidermy_01.#ft`   | `0xbbc0` |    10 |     1 |    10 | yes      | 10 of 10     |

Survey archives: `data.rpf!26` (1,229 type-2 and 1,982 type-3 rows) and
`levels.rpf!5`, which form the narrow corpus. The wide corpus is 27 archive
files named in a list passed as `LF_TEST_ARCHIVE_LIST`; the same archives are
the ones the fragment census used. The survey test is
`surveys_native_skeleton_rows` in `apps/desktop/src/files/model.rs`; the four
resources are asserted by `decodes_real_skeleton_resources`.

## Deformation measurements

The two evaluators are the CPU reference in `crates/scene` and a GPU compute
probe in `crates/renderer`, run over the same skinning matrices.

| Chain                | Selector         | Posed bone | Pose                | Vertices compared | Worst difference |
| -------------------- | ---------------- | ---------- | ------------------- | ----------------: | ---------------: |
| `mint_peacock_taxidermy_01.#ft` | `levels.rpf!5!8` | `Tail_01` (4) | 40 deg about model Z | 25,456 | `3.6e-7` m |
| `prop_am_candlestick_02a.#ft`   | `levels.rpf!5!1` | `Candle` (3)  | 60 deg about model Z | 788    | `3.7e-9` m |

The peacock frame moves 24,496 of the compared vertices with a largest
displacement of 1.19 m and collapses no normal, so the agreement is measured on
a pose with real displacement. The harness is
`renders_the_verified_deformation`, which also writes the authored, posed,
overlay, influence and reset frames.

## Method

- Every claim above is read from decoded payload bytes through the archive's
  page metadata, not from extracted standalone files alone.
- The quaternion and composition conventions are checked against the two
  independent matrix arrays, not against a plausible render.
- Geometry associations are accepted only after every vertex validates.
- Renders were produced through the offscreen path and inspected for placement.
