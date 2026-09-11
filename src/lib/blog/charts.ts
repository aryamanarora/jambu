export type BlogChartView = {
	label: string;
	unit: string;
	note: string;
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
