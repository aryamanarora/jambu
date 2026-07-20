/**
 * server/db.ts — BUILD-TIME SQLite access via better-sqlite3.
 *
 * Used only by `+page.server.ts` loads during prerendering (and by the dev server). The output
 * is baked into static HTML + `__data.json`, so at runtime on GitHub Pages there is no server —
 * canonical pages are already rendered. This module is under `$lib/server/` so SvelteKit will
 * never bundle better-sqlite3 into the client.
 *
 * PRERENDER_LIMIT (optional env): cap how many entry/language/reference pages are prerendered.
 * For fast LOCAL build smoke-tests only — production must prerender everything.
 */
import Database from 'better-sqlite3';
import type { Language, Lemma, Reference } from '$lib/types';

const DB_PATH = process.env.JAMBU_DB ?? '.dbwork/jambu.db';

let db: Database.Database | null = null;
export function getDb(): Database.Database {
	if (!db) db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
	return db;
}

export const PRERENDER_LIMIT = process.env.PRERENDER_LIMIT
	? parseInt(process.env.PRERENDER_LIMIT, 10)
	: Infinity;

function limit<T>(rows: T[]): T[] {
	return Number.isFinite(PRERENDER_LIMIT) ? rows.slice(0, PRERENDER_LIMIT) : rows;
}

// ---- id enumerations for prerender `entries()` ---------------------------

export function allEntryIds(): { entry: string }[] {
	const rows = getDb()
		.prepare(`SELECT id FROM lemmas WHERE origin_lemma_id IS NULL ORDER BY "order"`)
		.all() as { id: string }[];
	return limit(rows.map((r) => ({ entry: String(r.id) })));
}

export function allLanguageIds(): { lang1: string }[] {
	const rows = getDb().prepare(`SELECT id FROM languages ORDER BY "order", name`).all() as {
		id: string;
	}[];
	return limit(rows.map((r) => ({ lang1: String(r.id) })));
}

export function allReferenceIds(): { ref: string }[] {
	const rows = getDb().prepare(`SELECT id FROM "references" ORDER BY short`).all() as {
		id: string;
	}[];
	return limit(rows.map((r) => ({ ref: String(r.id) })));
}

// ---- single-record loads --------------------------------------------------

export type EntryMeta = Omit<Lemma, 'language'> & { language: Language | null };

export function getEntryMeta(id: string): EntryMeta | null {
	const dbh = getDb();
	const e = dbh.prepare('SELECT * FROM lemmas WHERE id = ?').get(id) as Lemma | undefined;
	if (!e) return null;
	const language = (dbh.prepare('SELECT * FROM languages WHERE id = ?').get(e.language_id) ??
		null) as Language | null;
	return { ...e, language };
}

export function getLanguageRow(id: string): Language | null {
	return (getDb().prepare('SELECT * FROM languages WHERE id = ?').get(id) ?? null) as Language | null;
}

export function allLanguages(): Language[] {
	return getDb().prepare('SELECT * FROM languages ORDER BY "order", name').all() as Language[];
}

export function getReferenceRow(id: string): Reference | null {
	return (getDb().prepare('SELECT * FROM "references" WHERE id = ?').get(id) ??
		null) as Reference | null;
}

export function allReferences(): Reference[] {
	return getDb().prepare('SELECT * FROM "references" ORDER BY short').all() as Reference[];
}
