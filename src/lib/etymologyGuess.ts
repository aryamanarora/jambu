/** Minimum phonological similarity used by the Etymology Lab to count a form as supported. */
export const ETYMOLOGY_GUESS_THRESHOLD = 0.28;

export type GuessForm = {
	word: string;
	phonemic?: string | null;
	language_id?: string | null;
};

export type GuessEtymon<T> = {
	value: T;
	headword: string;
	reflexes: GuessForm[];
};

export type EtymologyGuess<T> = {
	value: T;
	similarity: number;
	matchedWord: string;
	matchedLanguageId: string | null;
};

function soundKey(value: string): string[] {
	return [...(value ?? '')
		.normalize('NFD')
		.toLocaleLowerCase()
		.replace(/[\p{M}\s*\-‐‑‒–—―'’ʔˀ.\xb7|()[\]{}\/\\]/gu, '')];
}

/** Normalized edit similarity shared by the Lab and concept-page best guesses. */
export function soundSimilarity(left: string, right: string): number {
	const a = soundKey(left);
	const b = soundKey(right);
	if (!a.length || !b.length) return 0;
	let previous = Array.from({ length: b.length + 1 }, (_, index) => index);
	for (let i = 1; i <= a.length; i++) {
		const current = [i];
		for (let j = 1; j <= b.length; j++) {
			current[j] = Math.min(
				current[j - 1] + 1,
				previous[j] + 1,
				previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)
			);
		}
		previous = current;
	}
	return Math.max(0, 1 - previous[b.length] / Math.max(a.length, b.length));
}

/**
 * Pick the closest etymon using the Lab's sound strategy: compare the form with the headword and
 * every attested reflex, discounting cross-language reflex matches to 82%. The caller controls
 * the candidate set; concept pages pass only etyma already attested for that concept.
 */
export function bestEtymologyGuess<T>(
	form: GuessForm,
	candidates: GuessEtymon<T>[],
	threshold = ETYMOLOGY_GUESS_THRESHOLD
): EtymologyGuess<T> | null {
	const formSound = form.phonemic || form.word;
	let best: EtymologyGuess<T> | null = null;
	for (const candidate of candidates) {
		let match: EtymologyGuess<T> = {
			value: candidate.value,
			similarity: soundSimilarity(formSound, candidate.headword),
			matchedWord: candidate.headword,
			matchedLanguageId: null
		};
		for (const reflex of candidate.reflexes) {
			const weight = reflex.language_id === form.language_id ? 1 : 0.82;
			const similarity = soundSimilarity(formSound, reflex.phonemic || reflex.word) * weight;
			if (similarity > match.similarity) {
				match = {
					value: candidate.value,
					similarity,
					matchedWord: reflex.word,
					matchedLanguageId: reflex.language_id ?? null
				};
			}
		}
		if (!best || match.similarity > best.similarity) best = match;
	}
	return best && best.similarity >= threshold ? best : null;
}
