/**
 * Compatibility fold used by the optional relaxed search mode.
 *
 * NFKD expands compatibility characters (for example ʰ → h and full-width letters → ASCII),
 * while removing combining marks makes a query such as `amsa` match `áṁśa`. The two explicit
 * mappings cover Unicode glyph variants that normalization deliberately leaves distinct.
 */
export function unicodeSearchFold(value: string): string {
	return (value ?? '')
		.normalize('NFKD')
		.toLowerCase()
		.replace(/\p{M}/gu, '')
		.replaceAll('ɡ', 'g')
		.replaceAll('ı', 'i');
}

export function unicodeSearchIncludes(value: string, query: string, relaxed = false): boolean {
	return relaxed
		? unicodeSearchFold(value).includes(unicodeSearchFold(query))
		: value.toLocaleLowerCase().includes(query.toLocaleLowerCase());
}
