/** Retained decoded-byte estimate, not a hard RAM limit: decoder/SQLite temporaries excluded. */
export class CitationCache {
    constructor(budget = 128 * 1024 * 1024) {
        this.budget = budget;
        this.small = new Map();
        this.smallBytes = 0;
        this.oversized = null;
        this.stats = { hits: 0, misses: 0, decodes: 0, oversizedDecodes: 0, evictions: 0, estimatedPeakBytes: 0 };
    }
    get(key, decode) {
        if (this.oversized?.key === key) {
            this.stats.hits++;
            return this.oversized.group;
        }
        const hit = this.small.get(key);
        if (hit) {
            this.stats.hits++;
            this.small.delete(key);
            this.small.set(key, hit);
            return hit.group;
        }
        this.stats.misses++;
        const group = decode();
        this.stats.decodes++;
        // Estimated object/string headers + array slots and UTF-16 payload.
        const bytes = 256 + group.reduce((n, c) => n + 128 + 2 * c.locator.length, 0);
        if (bytes > this.budget) {
            this.stats.oversizedDecodes++;
            if (this.oversized) this.stats.evictions++;
            this.oversized = { key, group, bytes };
        } else {
            while (this.smallBytes + bytes > this.budget) {
                const oldest = this.small.keys().next().value;
                this.smallBytes -= this.small.get(oldest).bytes;
                this.small.delete(oldest);
                this.stats.evictions++;
            }
            this.small.set(key, { group, bytes });
            this.smallBytes += bytes;
        }
        this.stats.estimatedPeakBytes = Math.max(this.stats.estimatedPeakBytes,
            this.smallBytes + (this.oversized?.bytes ?? 0));
        return group;
    }
}
