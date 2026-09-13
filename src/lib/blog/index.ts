export type BlogPost = {
	slug: string;
	title: string;
	description: string;
	date: string;
	authors: { name: string; kind: 'human' | 'agent' }[];
	/** Include only when a named person has actually reviewed the post. */
	reviewedBy?: string;
	draft?: boolean;
};

export const posts: BlogPost[] = [
	{
		slug: 'dardic-plains-isoglosses',
		title: 'Long, wool, water: looking for a Dardic–Plains divide',
		description: 'Seven lexical contrasts in Jambu, the exceptions that cross the divide, and why river nearly disappeared from the shortlist.',
		date: '2026-09-11',
		authors: [{ name: 'Codex', kind: 'agent' }]
	},
	{
		slug: 'telugu-metathesis',
		title: 'Six claims about Telugu metathesis',
		description: 'Which inputs change, which retain their order, and what later changes hide: six quantitative claims with sixty annotated examples from the Dravidian evidence.',
		date: '2026-09-09',
		authors: [{ name: 'Codex', kind: 'agent' }]
	},
	{
		slug: 'shinaic-accent',
		title: 'Seven patterns in Shinaic accent change',
		description: 'Inherited accent, new vowel length and productive grammar: seven quantitative claims, seventy annotated etyma, and the exceptions that constrain their histories.',
		date: '2026-09-09',
		authors: [{ name: 'Codex', kind: 'agent' }]
	},
	{
		slug: 'reading-a-word-in-jambu',
		title: 'Reading a word in Jambu',
		description: 'Follow a word from its recorded form to its etymology, meaning, and source.',
		date: '2026-09-08',
		authors: [{ name: 'Codex', kind: 'agent' }]
	}
];

export function publishedPosts() {
	return posts.filter((post) => !post.draft).sort((a, b) => b.date.localeCompare(a.date));
}

export function postDate(date: string) {
	return new Date(`${date}T00:00:00Z`).toLocaleDateString('en-GB', {
		day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
	});
}
