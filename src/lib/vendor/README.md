# fzstd 0.1.1 decoder

Vendored from the installed `fzstd@0.1.1` ESM module and declarations, under the
included MIT licence (`LICENSE.fzstd`). The sole decoder change replaces the
32-bit offset read with `readOffsetBits` from `../zstdBits.js`. A 26-bit offset
starting at bit 7 needs five bytes; the original read silently dropped its high
bit on the larger Jambu Zstandard frame.

`tests/zstd-bits.test.mjs` checks the boundary and every supported bit alignment
against a BigInt oracle. `scripts/pack_db.mjs` additionally requires exact SHA-256
round-trip equality through this decoder before atomically installing an artifact.
The same decoder is used by the browser and the unpacking script. No other upstream
code is changed. The final 48,801,375-byte artifact restores the 124,502,016-byte
SQLite image exactly (SHA-256 14990724cc34f534337682653e5681a588bae0e7c67093f0dc21622a1d0abbbf).
