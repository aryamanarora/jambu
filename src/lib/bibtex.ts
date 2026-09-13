import { base } from '$app/paths';
import { striptags } from './render';
import type { Reference } from './types';

let records: Promise<Record<string, string>> | undefined;

/** Preserve uncatalogued citations as notes rather than guessing bibliographic fields. */
export function fallbackBibtex(reference: Partial<Reference> & { id: string }): string {
	const key = reference.id.replace(/[^\p{L}\p{N}_:.-]/gu, '_');
	const escape = (value: string) => value.replace(/[\\{}%&#_$]/g, (char) =>
		char === '\\' ? '\\textbackslash{}' : `\\${char}`);
	const citation = striptags(reference.source || reference.short || reference.id)
		.replace(/\\([\\`*{}\[\]()#+\-.!_>])/g, '$1')
		.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
		.replace(/[*_`]/g, '').replace(/\s+/g, ' ').trim();
	return `@misc{${key},\n  note = {${escape(citation)}}\n}\n`;
}

export async function referenceBibtex(reference: Partial<Reference> & { id: string }): Promise<string> {
	records ??= fetch(`${base}/bibtex.json`).then((response) => {
		if (!response.ok) throw new Error('Could not load bibliography');
		return response.json() as Promise<Record<string, string>>;
	}).catch((error) => { records = undefined; throw error; });
	return (await records)[reference.id] ?? fallbackBibtex(reference);
}
