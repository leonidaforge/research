# Resource research history

Interpretations that were once used for RAGE resources and later corrected. The current model is in the [format documents](../../formats/resources/README.md).

## Page-map counts read as stream counts

**Old assumption.** In the one-sample model the two bytes at page map `+8` and `+9` were probably stream counts, because they equal the number of stored streams in the sample (RES-F04). Six ASCII names follow the map, so the counts also seemed too small to describe the map's contents.

**Correction.** The bytes are page counts. A resource can store two pages in two streams, and a split page in several streams, so the two readings separate on other resources (RES-F12, RES-F15). The map is `16 + 8 * pages` bytes, so for a 1/1 resource it ends 0x20 bytes after its start. The names are resource data that begins after the map and are unrelated to the counts.

## A 4 KiB page unit

**Old assumption.** The twelve graphics values `0x60000000 + n * 0x1000` partitioned the 49,152-byte segment, so a page was taken to be a 4 KiB block addressed by pointers (pages.md, first revision).

**Correction.** The twelve values are targets inside one graphics page, not page boundaries. Page sizes follow from the stored chunk sizes: a single-page segment is not page-sized, and in a multi-page segment every page but the last is a multiple of `0x10000` (RES-F14). The page map counts pages, not 4 KiB blocks.

## The pointer split was undecided

**Old assumption.** The high nibble selected the segment, but a 16-bit selector with a 64 KiB offset fitted the sample equally well, and the split was left open (pointers.md, first revision).

**Correction.** A second resource places its page map at system offset `0x988E0` and holds an in-bounds system pointer at `0x98B34`. A 16-bit offset cannot express either value. The 4-bit selector with a 28-bit offset is the only reading that fits (RES-F16).

## `0xAA` as an unused-region fill

**Old assumption.** Unused regions of both segments were filled with `0xAA` (RES-F06).

**Correction.** The byte occurs 24 times in the graphics segment of the primary sample, in six 4-byte runs inside data blocks. It is not a segment-wide fill and does not mark unused space (RES-F06).

## A texture-dictionary identification

**Old assumption.** The primary sample was read as a probable texture dictionary because the page map is followed by short ASCII names and the 12 graphics targets begin with small header-like values (RES-F07).

**Correction.** The name meaning and pixel format were not established. The observation does not identify the payload format, so the current documents do not carry the texture-dictionary reading.

## The rechecked structural samples replaced an earlier set

**Old state.** The originating branch recorded a second-system-page sample with its map at `0x24EC0` in a 192,240-byte system segment, and a system-only sample whose entry sits at `0x1B33B90` with a `0x40` map and 96 bytes of system data.

**Correction.** The structural sample was re-derived from seven resources, recorded as RES-F23 and listed in the pages document. The earlier rows record no archive or row index for their subjects, so the change cannot be attributed to a recheck rather than to a different subject selection; the record does not distinguish the two. The earlier values are not retained because they cannot be matched to a named resource.
