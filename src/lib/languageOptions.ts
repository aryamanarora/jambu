import { cladeColor } from './clades';
import type { Language, Dialect } from './types';

export interface SelectOption {
	value: string;
	label: string;
	sub?: string;
	swatch?: string;
	search?: string;
	note?: string;
}

/** Shared labels, branch colours and searchable IDs for every language picker. */
export function languageOptions(languages: Language[], dialects: Dialect[] = []): SelectOption[] {
	const byId = new Map(languages.map(l => [l.id, l]));
	return [
		...languages.map(l => ({ value: l.id, label: l.name ?? l.id, sub: l.clade ?? '', swatch: cladeColor(l.clade) })),
		...dialects.map(d => {
			const parent = byId.get(d.language_id);
			return { value: d.token, label: `${parent?.name ?? d.language_id}: ${d.name}`, sub: `dialect · ${parent?.clade ?? ''}`, swatch: cladeColor(parent?.clade), search: d.language_id };
		})
	];
}

export function filterOptions(options: SelectOption[], query: string): SelectOption[] {
	const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
	return options.filter(o => {
		const text = `${o.label} ${o.value} ${o.sub ?? ''} ${o.search ?? ''}`.toLocaleLowerCase();
		return terms.every(term => text.includes(term));
	});
}
