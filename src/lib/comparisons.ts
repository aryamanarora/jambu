import type { CrossFamilyComparison } from './types';

function currentEntryReceives(comparison: CrossFamilyComparison, currentId: string): boolean {
	const sourceReceives = comparison.direction === 'entry-from-compared';
	const currentIsSourceArticle = comparison.entry_id === currentId;
	return sourceReceives === currentIsSourceArticle;
}

/** Describe a source-relative comparison from the perspective of the entry being rendered. */
export function comparisonLabel(
	comparison: CrossFamilyComparison,
	currentId: string
): string {
	if (comparison.relation === 'related') return '';
	if (comparison.direction === 'undetermined') {
		return comparison.relation === 'loan'
			? 'possible loan connection (direction unclear) with'
			: 'possible influence (direction unclear) involving';
	}
	const currentReceives = currentEntryReceives(comparison, currentId);
	if (comparison.relation === 'loan')
		return currentReceives ? 'possibly borrowed from' : 'possible source of';
	return currentReceives ? 'possibly influenced by' : 'possible influence on';
}

/** Short relation wording for dense list cells; the entry page retains the full qualification. */
export function compactComparisonLabel(
	comparison: CrossFamilyComparison,
	currentId: string
): string {
	if (comparison.relation === 'related') return 'cf.';
	if (comparison.direction === 'undetermined')
		return comparison.relation === 'loan' ? 'loan link with' : 'influence link with';
	const currentReceives = currentEntryReceives(comparison, currentId);
	if (comparison.relation === 'loan') return currentReceives ? 'from' : 'source of';
	return currentReceives ? 'influenced by' : 'influences';
}
