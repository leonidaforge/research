# RPF9 type inventory

Machine-written from a `lforge archive census` run. Every row is one
combination of properties observed in the run: the entry type stored in
the table of contents, the identification made from the decoded head, a
normalised shape of that head, the storage shape, whether the payload
transform applies, whether the payload decoded, whether the structure was
validated, what the application can do with the entry, the extension the
classification allowed and where that extension came from.

## Coverage

| Count | Value |
| ----- | ----: |
| roots_discovered | 22 |
| roots_opened | 22 |
| failed_roots | 0 |
| archives_opened | 4373 |
| nested_archives_opened | 4351 |
| archives_resumed | 0 |
| failed_archives | 0 |
| entries_enumerated | 1255039 |
| entries_probed | 0 |
| entries_decoded | 0 |
| entries_undecoded | 0 |
| structures_verified | 0 |
| containers_identified | 0 |
| declared_asset_classes | 1181971 |
| unresolved_formats | 1255039 |
| stopped early | nothing |
| complete | True |

A bounded run is a sample. Only a run whose coverage reports every
discovered root and no stopped scan is a count of the installation.

## Type summary

Sorted by type id. `declared` is the extension the engine registers for the type;
`from payload` is an extension the bytes themselves established.

| Type | Entries | Declared | From payload | Outcomes |
| ---- | ------: | -------- | ------------ | -------- |
| 0 | 4351 | - | - | - 4351 |
| 2 | 167897 | - | - | - 167897 |
| 3 | 55488 | - | - | - 55488 |
| 4 | 48584 | - | - | - 48584 |
| 5 | 2612 | - | - | - 2612 |
| 6 | 92199 | - | - | - 92199 |
| 11 | 48612 | - | - | - 48612 |
| 14 | 2 | - | - | - 2 |
| 15 | 250434 | - | - | - 250434 |
| 16 | 22382 | - | - | - 22382 |
| 17 | 22440 | - | - | - 22440 |
| 18 | 611 | - | - | - 611 |
| 64 | 443 | - | - | - 443 |
| 66 | 87 | - | - | - 87 |
| 67 | 62384 | - | - | - 62384 |
| 69 | 1 | - | - | - 1 |
| 70 | 8443 | - | - | - 8443 |
| 72 | 226 | - | - | - 226 |
| 73 | 166072 | - | - | - 166072 |
| 74 | 6308 | - | - | - 6308 |
| 77 | 3 | - | - | - 3 |
| 78 | 25608 | - | - | - 25608 |
| 79 | 27644 | - | - | - 27644 |
| 86 | 11 | - | - | - 11 |
| 87 | 15067 | - | - | - 15067 |
| 88 | 40019 | - | - | - 40019 |
| 89 | 746 | - | - | - 746 |
| 93 | 211 | - | - | - 211 |
| 94 | 80 | - | - | - 80 |
| 95 | 518 | - | - | - 518 |
| 96 | 1 | - | - | - 1 |
| 99 | 98 | - | - | - 98 |
| 100 | 27482 | - | - | - 27482 |
| 101 | 5 | - | - | - 5 |
| 102 | 142 | - | - | - 142 |
| 103 | 6762 | - | - | - 6762 |
| 104 | 1476 | - | - | - 1476 |
| 105 | 1476 | - | - | - 1476 |
| 108 | 32878 | - | - | - 32878 |
| 109 | 4 | - | - | - 4 |
| 110 | 5 | - | - | - 5 |
| 111 | 30511 | - | - | - 30511 |
| 113 | 2715 | - | - | - 2715 |
| 114 | 518 | - | - | - 518 |
| 115 | 8415 | - | - | - 8415 |
| 255 | 73068 | - | - | - 73068 |

## Distributions

### Identification kind

| Value | Entries |
| ----- | ------: |
| none | 1255039 |

### Format

| Value | Entries |
| ----- | ------: |
| none | 1255039 |

### Capability

| Value | Entries |
| ----- | ------: |
| unprobed | 1255039 |

### Extension

| Value | Entries |
| ----- | ------: |
| zbdr | 250434 |
| zdr | 167897 |
| zmap | 166072 |
| zbn | 92199 |
| - | 73068 |
| zcd | 62384 |
| zft | 55488 |
| zmt | 48612 |
| zdd | 48584 |
| zsm | 40019 |
| zascd | 32878 |
| zldbmt | 30511 |
| znv | 27644 |
| zsp | 27482 |
| zad | 25608 |
| zbft | 22440 |
| zbdd | 22382 |
| zas | 15067 |
| zpm | 8443 |
| zcov | 8415 |
| zfid | 6762 |
| ztyp | 6308 |
| rpf | 4351 |
| zkit | 2715 |
| ztd | 2612 |
| zhdat | 1476 |
| zmsk | 1476 |
| zscript | 746 |
| zvert | 611 |
| zcg | 518 |
| zcgc | 518 |
| mrf | 443 |
| zpt | 226 |
| zfc | 211 |
| zmmd | 142 |
| zcps | 98 |
| gfx | 87 |
| zlfc | 80 |
| zfd | 11 |
| zsmam | 5 |
| ztsl | 5 |
| zrd | 4 |
| zjd | 3 |
| zdatb | 2 |
| zasd | 1 |
| zpmd | 1 |

### Structure claim

| Value | Entries |
| ----- | ------: |
| unknown | 1255039 |

### Payload state

| Value | Entries |
| ----- | ------: |
| not-read | 1255039 |

### Storage

| Value | Entries |
| ----- | ------: |
| chunked-2 | 1139128 |
| stored | 76826 |
| chunked-3 | 24436 |
| chunked-4 | 14488 |
| raw-deflate | 161 |

### Entry type

| Value | Entries |
| ----- | ------: |
| 15 | 250434 |
| 2 | 167897 |
| 73 | 166072 |
| 6 | 92199 |
| 255 | 73068 |
| 67 | 62384 |
| 3 | 55488 |
| 11 | 48612 |
| 4 | 48584 |
| 88 | 40019 |
| 108 | 32878 |
| 111 | 30511 |
| 79 | 27644 |
| 100 | 27482 |
| 78 | 25608 |
| 17 | 22440 |
| 16 | 22382 |
| 87 | 15067 |
| 70 | 8443 |
| 115 | 8415 |
| 103 | 6762 |
| 74 | 6308 |
| 0 | 4351 |
| 113 | 2715 |
| 5 | 2612 |
| 104 | 1476 |
| 105 | 1476 |
| 89 | 746 |
| 18 | 611 |
| 114 | 518 |
| 95 | 518 |
| 64 | 443 |
| 72 | 226 |
| 93 | 211 |
| 102 | 142 |
| 99 | 98 |
| 66 | 87 |
| 94 | 80 |
| 86 | 11 |
| 101 | 5 |
| 110 | 5 |
| 109 | 4 |
| 77 | 3 |
| 14 | 2 |
| 69 | 1 |
| 96 | 1 |

## Every combination

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 0 | none | not-read | stored | no | not-read | unknown | unprobed | rpf | 4351 | 17 |
| 2 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zdr | 164701 | 1287 |
| 2 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zdr | 3196 | 2 |
| 3 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zft | 55488 | 265 |
| 4 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zdd | 48328 | 178 |
| 4 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zdd | 256 | 1 |
| 5 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | ztd | 2612 | 33 |
| 6 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbn | 90545 | 969 |
| 6 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zbn | 1654 | 1 |
| 11 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zmt | 28295 | 202 |
| 11 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zmt | 19572 | 286 |
| 11 | none | not-read | chunked-3 | yes | not-read | unknown | unprobed | zmt | 496 | 12 |
| 11 | none | not-read | raw-deflate | no | not-read | unknown | unprobed | zmt | 157 | 2 |
| 11 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zmt | 88 | 1 |
| 11 | none | not-read | raw-deflate | yes | not-read | unknown | unprobed | zmt | 4 | 4 |
| 14 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zdatb | 1 | 1 |
| 14 | none | not-read | chunked-3 | yes | not-read | unknown | unprobed | zdatb | 1 | 1 |
| 15 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbdr | 245666 | 1203 |
| 15 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zbdr | 4768 | 1 |
| 16 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbdd | 22126 | 131 |
| 16 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zbdd | 256 | 1 |
| 17 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbft | 22440 | 263 |
| 18 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zvert | 611 | 2 |
| 64 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | mrf | 443 | 2 |
| 66 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | gfx | 87 | 7 |
| 67 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcd | 62375 | 383 |
| 67 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zcd | 9 | 1 |
| 69 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zpmd | 1 | 1 |
| 70 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zpm | 8443 | 67 |
| 72 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zpt | 226 | 4 |
| 73 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zmap | 161985 | 312 |
| 73 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zmap | 4087 | 4 |
| 74 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | ztyp | 6135 | 589 |
| 74 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | ztyp | 173 | 2 |
| 77 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zjd | 3 | 1 |
| 78 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zad | 25608 | 131 |
| 79 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | znv | 27644 | 12 |
| 86 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zfd | 11 | 1 |
| 87 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zas | 15067 | 185 |
| 88 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zsm | 40019 | 5 |
| 89 | none | not-read | chunked-2 | yes | not-read | unknown | unprobed | zscript | 746 | 2 |
| 93 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zfc | 211 | 1 |
| 94 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zlfc | 80 | 1 |
| 95 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcg | 518 | 2 |
| 96 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zasd | 1 | 1 |
| 99 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcps | 98 | 1 |
| 100 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zsp | 27482 | 11 |
| 101 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | ztsl | 5 | 1 |
| 102 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zmmd | 142 | 13 |
| 103 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zfid | 6762 | 17 |
| 104 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zmsk | 1476 | 1 |
| 105 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zhdat | 1476 | 1 |
| 108 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zascd | 32878 | 4 |
| 109 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zrd | 4 | 4 |
| 110 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zsmam | 5 | 5 |
| 111 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zldbmt | 30511 | 39 |
| 113 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zkit | 2715 | 1 |
| 114 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcgc | 518 | 2 |
| 115 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcov | 8415 | 4 |
| 255 | none | not-read | stored | no | not-read | unknown | unprobed | - | 72475 | 127 |
| 255 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | - | 441 | 46 |
| 255 | none | not-read | chunked-3 | yes | not-read | unknown | unprobed | - | 151 | 2 |
| 255 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | - | 1 | 1 |

## By entry type

### Type 0: 4351 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 0 | none | not-read | stored | no | not-read | unknown | unprobed | rpf | 4351 | 17 |

Samples of type 0 as `not-read`:
- `anim.rpf!0`: - bytes, head ``
- `anim.rpf!1`: - bytes, head ``
- `anim.rpf!2`: - bytes, head ``
- `audio.rpf!0`: - bytes, head ``
- `audio.rpf!1`: - bytes, head ``
- `audio.rpf!2`: - bytes, head ``
- `data.rpf!0`: - bytes, head ``
- `data.rpf!1`: - bytes, head ``
- `data.rpf!2`: - bytes, head ``
- `levels.rpf!0`: - bytes, head ``
- `levels.rpf!1`: - bytes, head ``
- `levels.rpf!2`: - bytes, head ``
- `navmeshes.rpf!0`: - bytes, head ``
- `navmeshes.rpf!1`: - bytes, head ``
- `navmeshes.rpf!2`: - bytes, head ``
- `core_bvh4.rpf!0`: - bytes, head ``
- `core_bvh4.rpf!1`: - bytes, head ``
- `core_bvh4.rpf!2`: - bytes, head ``
- `core_licenses_data.rpf!0`: - bytes, head ``
- `core_restofworld.rpf!0`: - bytes, head ``
- `core_restofworld.rpf!1`: - bytes, head ``
- `core_restofworld.rpf!2`: - bytes, head ``
- `core_restofworld001.rpf!0`: - bytes, head ``
- `shared_minigame000.rpf!0`: - bytes, head ``

### Type 2: 167897 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 2 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zdr | 164701 | 1287 |
| 2 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zdr | 3196 | 2 |

Samples of type 2 as `not-read`:
- `data.rpf!14!0`: - bytes, head ``
- `data.rpf!14!1`: - bytes, head ``
- `data.rpf!14!2`: - bytes, head ``
- `levels.rpf!2!0`: - bytes, head ``
- `levels.rpf!2!2`: - bytes, head ``
- `levels.rpf!2!3`: - bytes, head ``
- `core_restofworld.rpf!8!0`: - bytes, head ``
- `core_restofworld.rpf!8!2`: - bytes, head ``
- `core_restofworld.rpf!8!6`: - bytes, head ``
- `shared_minigame000.rpf!3!2`: - bytes, head ``
- `shared_minigame000.rpf!3!3`: - bytes, head ``
- `shared_minigame000.rpf!3!4`: - bytes, head ``
- `story000.rpf!6!0`: - bytes, head ``
- `story000.rpf!6!1`: - bytes, head ``
- `story000.rpf!6!4`: - bytes, head ``

Samples of type 2 as `not-read`:
- `levels.rpf!1719!4`: - bytes, head ``
- `levels.rpf!1719!5`: - bytes, head ``
- `levels.rpf!1719!6`: - bytes, head ``

### Type 3: 55488 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 3 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zft | 55488 | 265 |

Samples of type 3 as `not-read`:
- `data.rpf!26!0`: - bytes, head ``
- `data.rpf!26!1`: - bytes, head ``
- `data.rpf!26!4`: - bytes, head ``
- `levels.rpf!5!0`: - bytes, head ``
- `levels.rpf!5!1`: - bytes, head ``
- `levels.rpf!5!2`: - bytes, head ``
- `core_restofworld.rpf!8!1`: - bytes, head ``
- `core_restofworld.rpf!8!3`: - bytes, head ``
- `core_restofworld.rpf!8!4`: - bytes, head ``
- `shared_minigame000.rpf!33!10`: - bytes, head ``
- `shared_minigame000.rpf!33!32`: - bytes, head ``
- `shared_minigame000.rpf!33!45`: - bytes, head ``
- `packs.rpf!18!0`: - bytes, head ``
- `packs.rpf!18!1`: - bytes, head ``
- `packs.rpf!18!2`: - bytes, head ``

### Type 4: 48584 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 4 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zdd | 48328 | 178 |
| 4 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zdd | 256 | 1 |

Samples of type 4 as `not-read`:
- `data.rpf!7!0`: - bytes, head ``
- `data.rpf!7!1`: - bytes, head ``
- `data.rpf!7!2`: - bytes, head ``
- `levels.rpf!14!12`: - bytes, head ``
- `levels.rpf!14!25`: - bytes, head ``
- `levels.rpf!14!194`: - bytes, head ``
- `core_restofworld.rpf!2!0`: - bytes, head ``
- `core_restofworld.rpf!2!1`: - bytes, head ``
- `core_restofworld.rpf!2!2`: - bytes, head ``
- `shared_minigame000.rpf!3!1`: - bytes, head ``
- `shared_minigame000.rpf!3!5`: - bytes, head ``
- `shared_minigame000.rpf!3!20`: - bytes, head ``
- `story000.rpf!131!0`: - bytes, head ``
- `story000.rpf!131!1`: - bytes, head ``
- `story000.rpf!131!2`: - bytes, head ``
- `story000_restofworld.rpf!17!0`: - bytes, head ``
- `packs.rpf!7!0`: - bytes, head ``
- `packs.rpf!7!1`: - bytes, head ``
- `packs.rpf!7!2`: - bytes, head ``

Samples of type 4 as `not-read`:
- `levels.rpf!1719!7`: - bytes, head ``
- `levels.rpf!1719!12`: - bytes, head ``
- `levels.rpf!1719!25`: - bytes, head ``

### Type 5: 2612 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 5 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | ztd | 2612 | 33 |

Samples of type 5 as `not-read`:
- `data.rpf!1!0`: - bytes, head ``
- `data.rpf!1!1`: - bytes, head ``
- `data.rpf!1!2`: - bytes, head ``
- `levels.rpf!637!0`: - bytes, head ``
- `levels.rpf!637!1`: - bytes, head ``
- `levels.rpf!637!2`: - bytes, head ``
- `core_restofworld.rpf!4!0`: - bytes, head ``
- `core_restofworld.rpf!4!1`: - bytes, head ``
- `core_restofworld.rpf!4!2`: - bytes, head ``
- `shared_minigame000.rpf!11!0`: - bytes, head ``
- `shared_minigame000.rpf!11!1`: - bytes, head ``
- `shared_minigame000.rpf!11!2`: - bytes, head ``
- `textures.rpf!0!0`: - bytes, head ``
- `textures.rpf!1!0`: - bytes, head ``
- `textures.rpf!2!0`: - bytes, head ``

### Type 6: 92199 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 6 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbn | 90545 | 969 |
| 6 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zbn | 1654 | 1 |

Samples of type 6 as `not-read`:
- `levels.rpf!2!1`: - bytes, head ``
- `levels.rpf!2!5`: - bytes, head ``
- `levels.rpf!2!10`: - bytes, head ``
- `shared_minigame000.rpf!3!0`: - bytes, head ``
- `shared_minigame000.rpf!3!8`: - bytes, head ``
- `shared_minigame000.rpf!3!13`: - bytes, head ``
- `story000.rpf!6!2`: - bytes, head ``
- `story000.rpf!6!3`: - bytes, head ``
- `story000.rpf!6!6`: - bytes, head ``

Samples of type 6 as `not-read`:
- `levels.rpf!1719!0`: - bytes, head ``
- `levels.rpf!1719!1`: - bytes, head ``
- `levels.rpf!1719!2`: - bytes, head ``

### Type 11: 48612 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 11 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zmt | 28295 | 202 |
| 11 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zmt | 19572 | 286 |
| 11 | none | not-read | chunked-3 | yes | not-read | unknown | unprobed | zmt | 496 | 12 |
| 11 | none | not-read | raw-deflate | no | not-read | unknown | unprobed | zmt | 157 | 2 |
| 11 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zmt | 88 | 1 |
| 11 | none | not-read | raw-deflate | yes | not-read | unknown | unprobed | zmt | 4 | 4 |

Samples of type 11 as `not-read`:
- `data.rpf!8!0`: - bytes, head ``
- `data.rpf!8!1`: - bytes, head ``
- `data.rpf!8!2`: - bytes, head ``
- `levels.rpf!12!2010`: - bytes, head ``
- `levels.rpf!12!2011`: - bytes, head ``
- `levels.rpf!12!2013`: - bytes, head ``
- `navmeshes.rpf!26!0`: - bytes, head ``
- `navmeshes.rpf!26!1`: - bytes, head ``
- `navmeshes.rpf!26!2`: - bytes, head ``
- `shared_minigame000.rpf!44!0`: - bytes, head ``
- `story000.rpf!43!0`: - bytes, head ``
- `story000.rpf!43!1`: - bytes, head ``
- `story000.rpf!43!2`: - bytes, head ``
- `story000_restofworld.rpf!13!0`: - bytes, head ``
- `story000_restofworld.rpf!13!1`: - bytes, head ``
- `story000_restofworld.rpf!13!2`: - bytes, head ``
- `packs.rpf!6!0`: - bytes, head ``
- `packs.rpf!6!1`: - bytes, head ``
- `packs.rpf!6!2`: - bytes, head ``

Samples of type 11 as `not-read`:
- `anim.rpf!111!0`: - bytes, head ``
- `anim.rpf!196!0`: - bytes, head ``
- `anim.rpf!196!1`: - bytes, head ``
- `data.rpf!2!321`: - bytes, head ``
- `data.rpf!4!321`: - bytes, head ``
- `data.rpf!5!321`: - bytes, head ``
- `levels.rpf!12!2012`: - bytes, head ``
- `levels.rpf!21!3493`: - bytes, head ``
- `levels.rpf!25!5435`: - bytes, head ``
- `navmeshes.rpf!0!2448`: - bytes, head ``
- `navmeshes.rpf!2!2448`: - bytes, head ``
- `navmeshes.rpf!3!2448`: - bytes, head ``
- `core_restofworld.rpf!9!0`: - bytes, head ``
- `core_restofworld.rpf!9!1`: - bytes, head ``
- `core_restofworld.rpf!20`: - bytes, head ``
- `shared_minigame000.rpf!0!3`: - bytes, head ``
- `shared_minigame000.rpf!1!3`: - bytes, head ``
- `shared_minigame000.rpf!6!3`: - bytes, head ``
- `story000.rpf!5!319`: - bytes, head ``
- `story000.rpf!8!319`: - bytes, head ``
- `story000.rpf!42!0`: - bytes, head ``
- `story000_script.rpf!0!0`: - bytes, head ``
- `story000_script.rpf!0!1`: - bytes, head ``
- `story000_script.rpf!0!2`: - bytes, head ``

Samples of type 11 as `not-read`:
- `anim.rpf!236`: - bytes, head ``
- `anim.rpf!240`: - bytes, head ``
- `anim.rpf!243`: - bytes, head ``
- `data.rpf!21!33`: - bytes, head ``
- `data.rpf!21!42`: - bytes, head ``
- `data.rpf!21!71`: - bytes, head ``
- `levels.rpf!2054`: - bytes, head ``
- `core_licenses_data.rpf!0!0`: - bytes, head ``
- `core_licenses_data.rpf!0!1`: - bytes, head ``
- `story000.rpf!67!0`: - bytes, head ``
- `story000.rpf!67!1`: - bytes, head ``
- `story000.rpf!147!0`: - bytes, head ``
- `story000_script.rpf!3!0`: - bytes, head ``
- `story000_script.rpf!3!1`: - bytes, head ``
- `story000_script.rpf!3!2`: - bytes, head ``
- `packs.rpf!60`: - bytes, head ``
- `packs.rpf!63`: - bytes, head ``
- `packs.rpf!65`: - bytes, head ``
- `textures.rpf!21`: - bytes, head ``

Samples of type 11 as `not-read`:
- `data.rpf!0!0`: - bytes, head ``
- `data.rpf!0!1`: - bytes, head ``
- `data.rpf!0!2`: - bytes, head ``
- `levels.rpf!1645!0`: - bytes, head ``

Samples of type 11 as `not-read`:
- `levels.rpf!1029!4065`: - bytes, head ``
- `levels.rpf!1029!4066`: - bytes, head ``
- `levels.rpf!1029!4068`: - bytes, head ``

Samples of type 11 as `not-read`:
- `story000.rpf!90!0`: - bytes, head ``
- `story000.rpf!407!0`: - bytes, head ``
- `story000.rpf!410!0`: - bytes, head ``

### Type 14: 2 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 14 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zdatb | 1 | 1 |
| 14 | none | not-read | chunked-3 | yes | not-read | unknown | unprobed | zdatb | 1 | 1 |

Samples of type 14 as `not-read`:
- `data.rpf!262`: - bytes, head ``

Samples of type 14 as `not-read`:
- `story000_script.rpf!2!0`: - bytes, head ``

### Type 15: 250434 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 15 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbdr | 245666 | 1203 |
| 15 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zbdr | 4768 | 1 |

Samples of type 15 as `not-read`:
- `core_bvh4.rpf!0!0`: - bytes, head ``
- `core_bvh4.rpf!0!1`: - bytes, head ``
- `core_bvh4.rpf!0!2`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!0!1`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!0!2`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!0!3`: - bytes, head ``

Samples of type 15 as `not-read`:
- `core_bvh4.rpf!772!0`: - bytes, head ``
- `core_bvh4.rpf!772!1`: - bytes, head ``
- `core_bvh4.rpf!772!2`: - bytes, head ``

### Type 16: 22382 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 16 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbdd | 22126 | 131 |
| 16 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zbdd | 256 | 1 |

Samples of type 16 as `not-read`:
- `core_bvh4.rpf!2!1`: - bytes, head ``
- `core_bvh4.rpf!2!8`: - bytes, head ``
- `core_bvh4.rpf!2!13`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!0!0`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!0!8`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!0!20`: - bytes, head ``

Samples of type 16 as `not-read`:
- `core_bvh4.rpf!772!8`: - bytes, head ``
- `core_bvh4.rpf!772!13`: - bytes, head ``
- `core_bvh4.rpf!772!31`: - bytes, head ``

### Type 17: 22440 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 17 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zbft | 22440 | 263 |

Samples of type 17 as `not-read`:
- `core_bvh4.rpf!11!0`: - bytes, head ``
- `core_bvh4.rpf!11!1`: - bytes, head ``
- `core_bvh4.rpf!11!2`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!2!8`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!2!29`: - bytes, head ``
- `shared_minigame000_bvh4.rpf!2!41`: - bytes, head ``

### Type 18: 611 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 18 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zvert | 611 | 2 |

Samples of type 18 as `not-read`:
- `levels.rpf!1644!0`: - bytes, head ``
- `levels.rpf!1644!1`: - bytes, head ``
- `levels.rpf!1644!2`: - bytes, head ``

### Type 64: 443 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 64 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | mrf | 443 | 2 |

Samples of type 64 as `not-read`:
- `anim.rpf!43!0`: - bytes, head ``
- `anim.rpf!43!1`: - bytes, head ``
- `anim.rpf!43!2`: - bytes, head ``
- `story000.rpf!84!0`: - bytes, head ``
- `story000.rpf!84!1`: - bytes, head ``
- `story000.rpf!84!2`: - bytes, head ``

### Type 66: 87 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 66 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | gfx | 87 | 7 |

Samples of type 66 as `not-read`:
- `data.rpf!1!3`: - bytes, head ``
- `data.rpf!1!4`: - bytes, head ``
- `data.rpf!1!5`: - bytes, head ``

### Type 67: 62384 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 67 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcd | 62375 | 383 |
| 67 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zcd | 9 | 1 |

Samples of type 67 as `not-read`:
- `anim.rpf!5!0`: - bytes, head ``
- `anim.rpf!5!1`: - bytes, head ``
- `anim.rpf!5!2`: - bytes, head ``
- `levels.rpf!21!3480`: - bytes, head ``
- `levels.rpf!21!3483`: - bytes, head ``
- `levels.rpf!59!297`: - bytes, head ``
- `core_restofworld.rpf!8!128`: - bytes, head ``
- `core_restofworld001.rpf!0!0`: - bytes, head ``
- `core_restofworld001.rpf!0!1`: - bytes, head ``
- `core_restofworld001.rpf!0!2`: - bytes, head ``
- `shared_minigame000.rpf!33!143`: - bytes, head ``
- `shared_minigame000.rpf!46!473`: - bytes, head ``
- `story000.rpf!4!11`: - bytes, head ``
- `story000.rpf!4!29`: - bytes, head ``
- `story000.rpf!4!47`: - bytes, head ``
- `story000_restofworld.rpf!1!0`: - bytes, head ``
- `story000_restofworld.rpf!1!1`: - bytes, head ``
- `story000_restofworld.rpf!1!2`: - bytes, head ``

Samples of type 67 as `not-read`:
- `levels.rpf!1719!4983`: - bytes, head ``
- `levels.rpf!1719!4984`: - bytes, head ``
- `levels.rpf!1719!4985`: - bytes, head ``

### Type 69: 1 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 69 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zpmd | 1 | 1 |

Samples of type 69 as `not-read`:
- `anim.rpf!95!0`: - bytes, head ``

### Type 70: 8443 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 70 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zpm | 8443 | 67 |

Samples of type 70 as `not-read`:
- `anim.rpf!0!0`: - bytes, head ``
- `anim.rpf!2!0`: - bytes, head ``
- `anim.rpf!2!1`: - bytes, head ``
- `story000.rpf!341!0`: - bytes, head ``
- `story000.rpf!427!0`: - bytes, head ``
- `story000.rpf!427!1`: - bytes, head ``

### Type 72: 226 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 72 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zpt | 226 | 4 |

Samples of type 72 as `not-read`:
- `data.rpf!29!0`: - bytes, head ``
- `data.rpf!29!1`: - bytes, head ``
- `data.rpf!29!2`: - bytes, head ``
- `core_restofworld.rpf!5!0`: - bytes, head ``
- `story000.rpf!295!0`: - bytes, head ``
- `story000.rpf!295!1`: - bytes, head ``
- `story000.rpf!295!2`: - bytes, head ``
- `story000_restofworld.rpf!12!0`: - bytes, head ``

### Type 73: 166072 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 73 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zmap | 161985 | 312 |
| 73 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | zmap | 4087 | 4 |

Samples of type 73 as `not-read`:
- `levels.rpf!19!0`: - bytes, head ``
- `levels.rpf!19!1`: - bytes, head ``
- `levels.rpf!19!2`: - bytes, head ``
- `shared_minigame000.rpf!2!0`: - bytes, head ``
- `shared_minigame000.rpf!2!1`: - bytes, head ``
- `shared_minigame000.rpf!2!2`: - bytes, head ``
- `story000.rpf!10!0`: - bytes, head ``
- `story000.rpf!10!1`: - bytes, head ``
- `story000.rpf!10!2`: - bytes, head ``

Samples of type 73 as `not-read`:
- `levels.rpf!772!0`: - bytes, head ``
- `levels.rpf!927!0`: - bytes, head ``
- `levels.rpf!927!1`: - bytes, head ``

### Type 74: 6308 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 74 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | ztyp | 6135 | 589 |
| 74 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | ztyp | 173 | 2 |

Samples of type 74 as `not-read`:
- `levels.rpf!0!0`: - bytes, head ``
- `levels.rpf!0!1`: - bytes, head ``
- `levels.rpf!0!2`: - bytes, head ``
- `core_restofworld.rpf!0!0`: - bytes, head ``
- `shared_minigame000.rpf!2!4`: - bytes, head ``
- `shared_minigame000.rpf!2!5`: - bytes, head ``
- `shared_minigame000.rpf!2!6`: - bytes, head ``
- `story000.rpf!10!68`: - bytes, head ``
- `story000.rpf!10!69`: - bytes, head ``
- `story000.rpf!10!70`: - bytes, head ``
- `packs.rpf!18!45`: - bytes, head ``
- `packs.rpf!46!2490`: - bytes, head ``

Samples of type 74 as `not-read`:
- `levels.rpf!1029!4063`: - bytes, head ``
- `levels.rpf!1029!4064`: - bytes, head ``
- `levels.rpf!1029!4067`: - bytes, head ``

### Type 77: 3 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 77 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zjd | 3 | 1 |

Samples of type 77 as `not-read`:
- `anim.rpf!200!0`: - bytes, head ``
- `anim.rpf!200!1`: - bytes, head ``
- `anim.rpf!200!2`: - bytes, head ``

### Type 78: 25608 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 78 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zad | 25608 | 131 |

Samples of type 78 as `not-read`:
- `story000.rpf!4!0`: - bytes, head ``
- `story000.rpf!4!1`: - bytes, head ``
- `story000.rpf!4!2`: - bytes, head ``
- `story000_restofworld.rpf!2!0`: - bytes, head ``
- `story000_restofworld.rpf!2!1`: - bytes, head ``
- `story000_restofworld.rpf!2!2`: - bytes, head ``

### Type 79: 27644 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 79 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | znv | 27644 | 12 |

Samples of type 79 as `not-read`:
- `navmeshes.rpf!0!0`: - bytes, head ``
- `navmeshes.rpf!0!1`: - bytes, head ``
- `navmeshes.rpf!0!2`: - bytes, head ``

### Type 86: 11 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 86 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zfd | 11 | 1 |

Samples of type 86 as `not-read`:
- `anim.rpf!99!0`: - bytes, head ``
- `anim.rpf!99!1`: - bytes, head ``
- `anim.rpf!99!2`: - bytes, head ``

### Type 87: 15067 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 87 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zas | 15067 | 185 |

Samples of type 87 as `not-read`:
- `anim.rpf!1!0`: - bytes, head ``
- `anim.rpf!1!1`: - bytes, head ``
- `anim.rpf!1!2`: - bytes, head ``
- `story000.rpf!1!0`: - bytes, head ``
- `story000.rpf!1!1`: - bytes, head ``
- `story000.rpf!1!2`: - bytes, head ``
- `story000_restofworld.rpf!5!0`: - bytes, head ``
- `story000_restofworld.rpf!5!1`: - bytes, head ``
- `story000_restofworld.rpf!5!2`: - bytes, head ``

### Type 88: 40019 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 88 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zsm | 40019 | 5 |

Samples of type 88 as `not-read`:
- `core_restofworld.rpf!7!0`: - bytes, head ``
- `core_restofworld.rpf!7!1`: - bytes, head ``
- `core_restofworld.rpf!7!2`: - bytes, head ``
- `shared_minigame000.rpf!19!0`: - bytes, head ``
- `shared_minigame000.rpf!19!1`: - bytes, head ``
- `shared_minigame000.rpf!19!2`: - bytes, head ``
- `packs.rpf!2!0`: - bytes, head ``
- `packs.rpf!2!1`: - bytes, head ``
- `packs.rpf!2!2`: - bytes, head ``

### Type 89: 746 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 89 | none | not-read | chunked-2 | yes | not-read | unknown | unprobed | zscript | 746 | 2 |

Samples of type 89 as `not-read`:
- `story000_script.rpf!1!0`: - bytes, head ``
- `story000_script.rpf!1!1`: - bytes, head ``
- `story000_script.rpf!1!2`: - bytes, head ``
- `script.rpf!0!0`: - bytes, head ``

### Type 93: 211 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 93 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zfc | 211 | 1 |

Samples of type 93 as `not-read`:
- `packs.rpf!1!0`: - bytes, head ``
- `packs.rpf!1!1`: - bytes, head ``
- `packs.rpf!1!5`: - bytes, head ``

### Type 94: 80 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 94 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zlfc | 80 | 1 |

Samples of type 94 as `not-read`:
- `packs.rpf!1!2`: - bytes, head ``
- `packs.rpf!1!3`: - bytes, head ``
- `packs.rpf!1!4`: - bytes, head ``

### Type 95: 518 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 95 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcg | 518 | 2 |

Samples of type 95 as `not-read`:
- `packs.rpf!0!0`: - bytes, head ``
- `packs.rpf!0!2`: - bytes, head ``
- `packs.rpf!0!4`: - bytes, head ``

### Type 96: 1 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 96 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zasd | 1 | 1 |

Samples of type 96 as `not-read`:
- `script.rpf!0!1`: - bytes, head ``

### Type 99: 98 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 99 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcps | 98 | 1 |

Samples of type 99 as `not-read`:
- `packs.rpf!56!0`: - bytes, head ``
- `packs.rpf!56!1`: - bytes, head ``
- `packs.rpf!56!2`: - bytes, head ``

### Type 100: 27482 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 100 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zsp | 27482 | 11 |

Samples of type 100 as `not-read`:
- `navmeshes.rpf!1!0`: - bytes, head ``
- `navmeshes.rpf!1!1`: - bytes, head ``
- `navmeshes.rpf!1!2`: - bytes, head ``

### Type 101: 5 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 101 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | ztsl | 5 | 1 |

Samples of type 101 as `not-read`:
- `packs.rpf!36!0`: - bytes, head ``
- `packs.rpf!36!1`: - bytes, head ``
- `packs.rpf!36!2`: - bytes, head ``

### Type 102: 142 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 102 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zmmd | 142 | 13 |

Samples of type 102 as `not-read`:
- `anim.rpf!3!0`: - bytes, head ``
- `anim.rpf!28!0`: - bytes, head ``
- `anim.rpf!36!0`: - bytes, head ``

### Type 103: 6762 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 103 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zfid | 6762 | 17 |

Samples of type 103 as `not-read`:
- `core_restofworld.rpf!2!795`: - bytes, head ``
- `core_restofworld.rpf!2!796`: - bytes, head ``
- `core_restofworld.rpf!2!797`: - bytes, head ``
- `packs.rpf!11!519`: - bytes, head ``
- `packs.rpf!11!520`: - bytes, head ``
- `packs.rpf!11!521`: - bytes, head ``

### Type 104: 1476 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 104 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zmsk | 1476 | 1 |

Samples of type 104 as `not-read`:
- `levels.rpf!69!0`: - bytes, head ``
- `levels.rpf!69!1`: - bytes, head ``
- `levels.rpf!69!2`: - bytes, head ``

### Type 105: 1476 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 105 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | zhdat | 1476 | 1 |

Samples of type 105 as `not-read`:
- `levels.rpf!1237!0`: - bytes, head ``
- `levels.rpf!1237!1`: - bytes, head ``
- `levels.rpf!1237!2`: - bytes, head ``

### Type 108: 32878 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 108 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zascd | 32878 | 4 |

Samples of type 108 as `not-read`:
- `anim.rpf!26!0`: - bytes, head ``
- `anim.rpf!26!1`: - bytes, head ``
- `anim.rpf!26!2`: - bytes, head ``
- `story000.rpf!142!0`: - bytes, head ``
- `story000.rpf!142!1`: - bytes, head ``
- `story000.rpf!142!2`: - bytes, head ``
- `story000_restofworld.rpf!4!0`: - bytes, head ``
- `story000_restofworld.rpf!4!1`: - bytes, head ``
- `story000_restofworld.rpf!4!2`: - bytes, head ``

### Type 109: 4 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 109 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zrd | 4 | 4 |

Samples of type 109 as `not-read`:
- `anim.rpf!12!0`: - bytes, head ``
- `anim.rpf!25!0`: - bytes, head ``
- `anim.rpf!163!0`: - bytes, head ``

### Type 110: 5 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 110 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zsmam | 5 | 5 |

Samples of type 110 as `not-read`:
- `core_restofworld.rpf!3!0`: - bytes, head ``
- `shared_minigame000.rpf!36!0`: - bytes, head ``
- `packs.rpf!4!0`: - bytes, head ``
- `packs.rpf!5!0`: - bytes, head ``
- `packs.rpf!15!0`: - bytes, head ``

### Type 111: 30511 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 111 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zldbmt | 30511 | 39 |

Samples of type 111 as `not-read`:
- `data.rpf!2!0`: - bytes, head ``
- `data.rpf!2!1`: - bytes, head ``
- `data.rpf!2!2`: - bytes, head ``
- `shared_minigame000.rpf!0!0`: - bytes, head ``
- `shared_minigame000.rpf!0!1`: - bytes, head ``
- `shared_minigame000.rpf!0!2`: - bytes, head ``
- `story000.rpf!5!0`: - bytes, head ``
- `story000.rpf!5!1`: - bytes, head ``
- `story000.rpf!5!2`: - bytes, head ``

### Type 113: 2715 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 113 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zkit | 2715 | 1 |

Samples of type 113 as `not-read`:
- `packs.rpf!55!0`: - bytes, head ``
- `packs.rpf!55!1`: - bytes, head ``
- `packs.rpf!55!2`: - bytes, head ``

### Type 114: 518 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 114 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcgc | 518 | 2 |

Samples of type 114 as `not-read`:
- `packs.rpf!0!1`: - bytes, head ``
- `packs.rpf!0!3`: - bytes, head ``
- `packs.rpf!0!5`: - bytes, head ``

### Type 115: 8415 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 115 | none | not-read | chunked-2 | no | not-read | unknown | unprobed | zcov | 8415 | 4 |

Samples of type 115 as `not-read`:
- `navmeshes.rpf!9!0`: - bytes, head ``
- `navmeshes.rpf!9!1`: - bytes, head ``
- `navmeshes.rpf!9!2`: - bytes, head ``

### Type 255: 73068 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 255 | none | not-read | stored | no | not-read | unknown | unprobed | - | 72475 | 127 |
| 255 | none | not-read | chunked-3 | no | not-read | unknown | unprobed | - | 441 | 46 |
| 255 | none | not-read | chunked-3 | yes | not-read | unknown | unprobed | - | 151 | 2 |
| 255 | none | not-read | chunked-4 | no | not-read | unknown | unprobed | - | 1 | 1 |

Samples of type 255 as `not-read`:
- `audio.rpf!0!0`: - bytes, head ``
- `audio.rpf!0!1`: - bytes, head ``
- `audio.rpf!0!2`: - bytes, head ``
- `movies.rpf!0`: - bytes, head ``
- `movies.rpf!1`: - bytes, head ``
- `movies.rpf!2`: - bytes, head ``
- `core_restofworld.rpf!12`: - bytes, head ``
- `core_restofworld.rpf!13`: - bytes, head ``
- `core_restofworld.rpf!14`: - bytes, head ``
- `shared_minigame000.rpf!7!0`: - bytes, head ``
- `shared_minigame000.rpf!7!1`: - bytes, head ``
- `shared_minigame000.rpf!7!2`: - bytes, head ``
- `story000.rpf!0!0`: - bytes, head ``
- `story000.rpf!0!1`: - bytes, head ``
- `story000.rpf!0!2`: - bytes, head ``
- `story000_restofworld.rpf!3!0`: - bytes, head ``
- `story000_restofworld.rpf!3!1`: - bytes, head ``
- `story000_restofworld.rpf!16!0`: - bytes, head ``
- `shaders.rpf!1`: - bytes, head ``
- `shaders.rpf!2`: - bytes, head ``

Samples of type 255 as `not-read`:
- `audio.rpf!14!0`: - bytes, head ``
- `audio.rpf!14!1`: - bytes, head ``
- `audio.rpf!14!2`: - bytes, head ``
- `common.rpf!1`: - bytes, head ``
- `common.rpf!4`: - bytes, head ``
- `common.rpf!5`: - bytes, head ``
- `levels.rpf!326!0`: - bytes, head ``
- `levels.rpf!1220!0`: - bytes, head ``
- `levels.rpf!1681!0`: - bytes, head ``
- `core_bvh4.rpf!28!0`: - bytes, head ``
- `core_bvh4.rpf!144!0`: - bytes, head ``
- `core_bvh4.rpf!208!0`: - bytes, head ``
- `core_licenses_data.rpf!1`: - bytes, head ``
- `core_licenses_data.rpf!2`: - bytes, head ``
- `core_licenses_data.rpf!3`: - bytes, head ``
- `core_restofworld.rpf!1!0`: - bytes, head ``
- `core_restofworld.rpf!1!1`: - bytes, head ``
- `core_restofworld.rpf!10`: - bytes, head ``
- `core_restofworld001.rpf!1`: - bytes, head ``
- `core_restofworld001.rpf!2`: - bytes, head ``
- `core_restofworld001.rpf!3`: - bytes, head ``
- `shared_minigame000.rpf!12!0`: - bytes, head ``
- `shared_minigame000.rpf!30!0`: - bytes, head ``
- `shared_minigame000.rpf!30!1`: - bytes, head ``

Samples of type 255 as `not-read`:
- `appdata0.rpf!0`: - bytes, head ``
- `appdata0.rpf!1`: - bytes, head ``
- `common.rpf!0`: - bytes, head ``
- `common.rpf!2`: - bytes, head ``
- `common.rpf!3`: - bytes, head ``

Samples of type 255 as `not-read`:
- `levels.rpf!1091!0`: - bytes, head ``

