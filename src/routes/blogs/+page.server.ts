import { publishedPosts } from '$lib/blog';
import { getBlogPost } from '$lib/server/blog';

export const prerender = true;
export function load() {
	// Validate every published post here too: malformed links must fail the static build.
	return { posts: publishedPosts().map((post) => {
		const rendered = getBlogPost(post.slug)!;
		return { ...post, recordCount: rendered.records.length };
	}) };
}
