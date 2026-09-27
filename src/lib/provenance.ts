/** Link repository provenance while leaving any explanatory suffix in the label. */
export function provenanceUrl(label: string): string | null {
	const match = label.match(/^(data\/\S+?)(?:\s+\([^\n]*\))?$/);
	if (!match) return null;
	const path = match[1];
	if (path.split('/').some((part) => part === '..' || part === '.')) return null;
	return `https://github.com/moli-mandala/data/blob/main/${path.split('/').map(encodeURIComponent).join('/')}`;
}
