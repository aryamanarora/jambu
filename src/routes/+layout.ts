// Client-side routing everywhere; individual canonical routes opt into prerendering with
// `export const prerender = true`. Everything else is served the 200.html SPA fallback.
export const prerender = false;
export const ssr = true;
export const trailingSlash = 'ignore';
