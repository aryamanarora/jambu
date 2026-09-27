import assert from 'node:assert/strict';
import { CitationCache } from './parity_citation_cache.mjs';
const cache = new CitationCache(800);
const counts = new Map();
const get = (key, size = 1) => cache.get(key, () => {
    counts.set(key, (counts.get(key) ?? 0) + 1);
    return [{ locator: 'x'.repeat(size) }];
});
get('large', 1000); // 2,384 bytes: oversized.
get('a'); get('b'); get('a'); get('c'); // a touched; b evicted.
get('large', 1000); // small-group churn must not evict large.
get('a');
assert.equal(counts.get('large'), 1);
assert.equal(counts.get('a'), 1);
get('b');
assert.equal(counts.get('b'), 2);
assert.ok(cache.smallBytes <= 800);
assert.equal(cache.stats.estimatedPeakBytes, 2384 + 2 * 386);
get('other-large', 1200);
assert.equal(cache.oversized.key, 'other-large');
get('large', 1000); // second oversized source replaces only protected slot.
assert.equal(counts.get('large'), 2);
assert.equal(cache.stats.oversizedDecodes, 3);
assert.equal(cache.stats.misses, cache.stats.decodes);
console.log('Protected oversized slot and bounded small LRU checks passed');
