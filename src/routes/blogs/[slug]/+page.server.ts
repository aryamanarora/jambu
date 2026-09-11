import { error } from '@sveltejs/kit';
import { publishedPosts } from '$lib/blog';
import { getBlogPost } from '$lib/server/blog';

export const prerender = true;
export const entries = () => publishedPosts().map(({ slug }) => {
	// Validate outside the page loader: the site's crawler tolerates HTTP errors.
	getBlogPost(slug);
	return { slug };
});
export function load({ params }: { params: { slug: string } }) {
	const result = getBlogPost(params.slug);
	if (!result) error(404, 'Blog post not found');
	return result;
}
