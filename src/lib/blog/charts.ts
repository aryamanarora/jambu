
export type BlogMapPoint = {
	id: string;
	label: string;
	group: string;
	latitude: number | null;
	longitude: number | null;
	locationLabel: string;
	values: number[];
	families: { id: string; label: string }[];
	unresolved: number;
	loans: number;
	examples: { id: string; language: string; form: string; gloss: string; status: string }[];
};

export type BlogMap = {
	categories: string[];
	points: BlogMapPoint[];
	note: string;
};

export type BlogChartView = {
	label: string;
	unit: string;
	familyMode?: 'head' | 'entry';
	note: string;
	/** Explicit opt-in for weighted votes; ordinary research charts require integer counts. */
	fractionalVotes?: boolean;
	map?: BlogMap;
	otherFamilies?: { id: string; label: string; values: number[]; languages: string[] }[];
	categories: string[];
	rows: { label: string; values: number[] }[];
};
export type BlogChart = {
	id: string;
	title: string;
	sources: string[];
	/** Root-relative directory for this post's downloadable evidence. */
	sourceBase?: string;
	views: BlogChartView[];
};
