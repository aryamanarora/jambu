import type { AlignSeg } from './query';

export interface AlignmentCell {
	main: AlignSeg | null;
	post: AlignSeg[];
}

/** Keep insertions beside the preceding ancestor column, including any leading insertions. */
export function alignmentGrid(segs: AlignSeg[], indices: number[]): { cells: AlignmentCell[]; lead: AlignSeg[] } {
	const colOf = new Map(indices.map((index, column) => [index, column]));
	const cells: AlignmentCell[] = indices.map(() => ({ main: null, post: [] }));
	const lead: AlignSeg[] = [];
	let lastCol = -1;
	for (const segment of segs) {
		const column = segment.etymonIdx >= 0 ? colOf.get(segment.etymonIdx) : undefined;
		if (column !== undefined) {
			cells[column].main = segment;
			lastCol = column;
		} else if (lastCol >= 0) cells[lastCol].post.push(segment);
		else lead.push(segment);
	}
	return { cells, lead };
}
