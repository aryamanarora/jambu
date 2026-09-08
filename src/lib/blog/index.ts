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
		slug: 'shinaic-accent',
		title: 'How the Shinaic languages got their accents',
		description: 'Reconstructing inherited accent, lost vowels, and new tones across Shina, Palula, Sawi, Kalkoti, Kundal Shahi, Ushojo, and Brokskat.',
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
