# Vehicle resources

Vehicle bodies are fragments stored in unresolved top-level rows of `levels.rpf`.
They are not the entries under `levels/americas/vehicles/vehicle_assets.rpf`,
which holds add-on parts, and they are not in `packs.rpf`, whose fragment and
dictionary archives hold characters and clothing.

All findings below are **Private-evidence supported** against the Scarlett build
`e95020b2`. No engine code path for vehicle loading was traced.

## Discovery

A vehicle archive is a type 0 row of `levels.rpf` whose name is unresolved.
Sampling the first root rows finds terrain and props only; that sampling bias is
why earlier searches reported no vehicle models.

A content scan of all 73 unresolved top-level rows found vehicle fragments in 46
of them. Each archive holds one to six vehicles. Examples:

| Top-level row | Logical size | Models named by fragment headers                     |
| ------------- | ------------ | ---------------------------------------------------- |
| 430           | 28,316,096   | `akane`, `blista2`                                   |
| 618           | 349,138,304  | `buffalo`, `emperor`, `impaler5`, `intruder`, `sultan` |
| 620           | 15,808,976   | `raiden`, `schutzen`                                 |
| 690           | 53,683,584   | `clarion`, `rhode`, `speeder700gt`, `squalo`         |
| 740           | 73,142,448   | `cheetah2`, `coquette2`                              |

## Archive layout

A vehicle archive contains type 3 fragments.

| Entry                    | Role                                                | Status    |
| ------------------------ | --------------------------------------------------- | --------- |
| `<model>_hi.#ft`         | Highest-detail body; carries the wheel skeleton      | Confirmed |
| `<model>_mid.#ft`        | Medium-detail body                                  | Confirmed |
| `<model>.#ft`            | Low-detail body                                     | Confirmed |
| `<model>_<part>_hi.#ft`  | Bumpers, skirts, spoilers, exhausts, roof parts     | Confirmed |
| type 11                  | Metadata rows                                       | Confirmed |

`akane_hi.#ft` is 8,316,528 logical bytes at `levels.rpf` row 430, inner row 107.
Its fragment root reports one component, three meshes, and wheel bones in the
skeleton.

## Wheel skeleton

The drawable header is at system `+0x3F5C0` in the Akane sample. Its `+0x18`
pointer selects the skeleton header. The header fields below are confirmed on
that sample.

| Offset from skeleton header | Width | Content                         |
| --------------------------- | ----- | ------------------------------- |
| `+0x28`                     | 8     | Pointer to the bone array       |
| `+0x30`                     | 8     | Pointer to the inverse bind array |
| `+0x6C`                     | 2     | Joint count                     |
| `+0x6E`                     | 2     | Joint count, repeated           |

Each bone record is `0x50` bytes. The joint hash is at `+0x1C`, the parent index
at `+0x46`, and the record index at `+0x48`. Each inverse bind matrix is 64 bytes:
a 3x4 affine transform stored row-major, with the translation in the last row.

A wheel pivot is the translation row of the inverted inverse bind matrix.

Wheel joint hashes:

| Bone        | Hash         |
| ----------- | ------------ |
| `wheel_lf`  | `0xC5632281` |
| `wheel_rf`  | `0x07F7A965` |
| `wheel_lr`  | `0x6512E1D6` |
| `wheel_rr`  | `0x638BE088` |
| `wheel_lm1` | `0x65A722CD` |
| `wheel_rm1` | `0xAD5C9421` |
| `wheel_lm2` | `0x545B8036` |
| `wheel_rm2` | `0xA9030B6E` |
| `wheel_lm3` | `0xCA346BE2` |
| `wheel_rm3` | `0xF73DA7E2` |

Akane carries `wheel_lf`, `wheel_rf`, `wheel_lr`, and `wheel_rr` at skeleton
indices 246, 280, 305, and 325. Their pivots are `±0.74` on X, `+1.29` front and
`-1.26` rear on Y, and `-0.48` on Z.

## Wheel assets

Wheels are shared drawables, not part of the body archive. They are all type 2
rows of `levels.rpf` row 1302.

| Sample                  | Inner row | Logical size | Header                  |
| ----------------------- | --------- | ------------ | ----------------------- |
| `rim_street_035_hi`     | 1         | 468,688      | `rim_street_035_hi.#dr` |
| `tyre_lowpro_001_hi`    | 40        | 141,008      | `tyre_lowpro_001_hi.#dr` |

A low-profile tyre of 21 KB (`tyre_track_001`) has no mesh-blob marker, so its
system/graphics boundary is not inferable from the payload alone. Larger `_hi`
tyres carry the marker and split.

## Sample digests

| Sample                    | SHA-256 of the extracted logical bytes              |
| ------------------------- | --------------------------------------------------- |
| `akane_hi.#ft`            | `EACD1125B0A250210B94F84E41FCD4D187D2BA891C9C73A600146679D2A34D91` |
| `rim_street_035_hi.#dr`   | `FBA9AF8F1613CE52771E8917EC4E9DE3FA6E4D35077E0EE99C7FFD624F5CAFF3` |
| `tyre_lowpro_001_hi.#dr`  | `CD786167750B99E4836526A431471BB6E357FA552D86E320C9A871A3E506709E` |

## Rendering

The body decodes through `lforge-model` as a fragment. A preview renders the body
alone. The shared wheel kits do not follow an individual arch, so a mounted rim
reads as a wrong part rather than as a missing one. `lforge_model::attach_wheels`
still mounts a kit; no preview calls it.

Two commands generate the set.

`lforge vehicle bodies --archive levels.rpf --executable game.exe --names
catalog.txt --output bodies.json` scans the unresolved top-level rows for type 3
fragments named `<model>_hi.#ft` and records the archive locator of the best body
per model. It holds no absolute path, so it can be regenerated elsewhere.

`lforge vehicle previews --bodies bodies.json --archive levels.rpf --textures
data/ttdb --colors vehicleColors.json --output previews/` renders a 1024x1024
primary WebP and a 320x320 thumbnail per body, writes `previews.json`, and reuses
an image only when a versioned identity still matches. The identity covers the
body digest, the policy and shader revisions, the texture store digests, the
paint, the camera, the output size and the encoder profile.

Materials are shaded by the metal-roughness model in `lforge-renderer`: three
studio lights with a GGX lobe, a procedural backdrop sampled by reflection, and
an ACES tone map. The preview classifies each material by shader hash and gives
paint, glass, lamp, tyre, and trim their own response.

Painted panels carry no albedo texture. The paint shader declares a Diffuse key
that no store we hold resolves, so the preview tints those panels with a colour
from `vehicleColors.json`. Glass, lamps, grilles, and badges do resolve, from
`data/ttdb/vehicles/ttdb_vehicles.ttpf`; on Akane that is 10 of 24 materials.

A full run registered 326 of the 332 canonical vehicles and rendered 323 of them.
Three bodies fail: `arcturus` decodes no renderable mesh, and `grouse` and `taco`
have no inferable system/graphics boundary.

## Open items

- The paint Diffuse key `0x5D7A3A87CC19967D` resolves in no extracted store. It
  appears only as a shader reference inside type 4 drawables in `packs.rpf`, so
  the dictionary that holds it is still unlocated.
- Six canonical vehicles have no body fragment: `catcher`, `cutterpredator`,
  `metrotrain`, `predator`, `speeder` and `zale`. Four are boats, one is a train.
- Per-model wheel and tyre selection is not resolved. The shared kits are decoded
  and could be mounted, but they fit the arches badly.
- ZMT metadata and per-model handling files are not identified.
- Boats and aircraft have no wheel bones; their previews are body-only.

