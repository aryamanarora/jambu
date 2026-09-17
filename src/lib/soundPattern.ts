import { isDetachedNotation, matchesSound, segmentKey, type SoundColumn } from './phonology';

export const PATTERN_CLASSES = ['V', 'C', 'short', 'long', 'high', 'stop', 'nasal', 'sibilant', 'retroflex', 'aspirated'];
export interface TargetRange { start: number; end: number }
export interface SoundPattern { tokens: string[]; whole: boolean; error: string; target: TargetRange | null }
const invalidPattern = (error: string): SoundPattern => ({ tokens: [], whole: false, error, target: null });

/** Spaces are optional between literal segments; brackets combine class properties. */
export function parseSoundPattern(text: string, old = true): SoundPattern {
	if (!text.trim() || text.trim() === '*' || text.trim() === ':word') return { tokens: [], whole: true, error: '', target: null };
	const tokens: string[] = [];
	let targetStart: number | null = null, targetEnd: number | null = null;
	const chunks = text.trim().match(/\[[^\]]*\]|:[^\s[\]:()]+|[^\s[\]:()]+|[\[\]:()]/gu) ?? [];
	for (const chunk of chunks) {
		if (chunk === '(') {
			if (targetStart != null) return invalidPattern('Mark one continuous target with parentheses, for example V (k) V.');
			targetStart = tokens.length;
			continue;
		}
		if (chunk === ')') {
			if (targetStart == null || targetEnd != null) return invalidPattern('Open the target with (, for example V (k) V.');
			targetEnd = tokens.length;
			continue;
		}
		if (['[', ']', ':'].includes(chunk)) return invalidPattern('Close the class brackets, for example [retroflex+stop].');
		const name = chunk.replace(/^:/, '').replace(/^\[|\]$/g, '');
		if (chunk.startsWith('[') || chunk.startsWith(':') || PATTERN_CLASSES.includes(name)) {
			const names = name.split(/[+&,\s]+/).filter(Boolean);
			if (!names.length || names.some(n => !PATTERN_CLASSES.includes(n))) return invalidPattern(`Unknown class “${name}”. Use V, C, or a class from the picker.`);
			tokens.push(':' + names.join('+'));
			continue;
		}
		if (chunk.includes('*')) return invalidPattern('Use * by itself to select the whole form, or V / C for one sound class.');
		if (/^\p{M}/u.test(chunk)) return invalidPattern('A diacritic or modifier must follow its sound.');
		const graphemes = [...chunk.normalize('NFD').matchAll(/[^\p{M}][\p{M}]*/gu)].map(m => m[0].normalize('NFC'));
		for (let i = 0; i < graphemes.length; i++) {
			let g = graphemes[i];
			if (old && segmentKey(g) === 'a' && ['i', 'u'].includes(segmentKey(graphemes[i + 1] ?? ''))) g += graphemes[++i];
			while (/^[ʰʱʲʸʷː]$/.test(graphemes[i + 1] ?? '')) g += graphemes[++i];
			if (g !== '#' && isDetachedNotation(g)) return invalidPattern('A diacritic or modifier must follow its sound.');
			tokens.push(['V', 'C'].includes(g) ? ':' + g : g);
		}
	}
	if (!tokens.length || tokens.every(t => t === '#')) return invalidPattern('Include a sound between word boundaries.');
	if (tokens.slice(1, -1).includes('#')) return invalidPattern('Use # only at the beginning or end of a sequence.');
	if (tokens.length > 16) return invalidPattern('Use a sequence of at most 16 sounds or classes.');
	if (targetStart != null && targetEnd == null) return invalidPattern('Close the target with ), for example V (k) V.');
	if (targetStart != null && targetEnd != null && (targetStart === targetEnd || tokens.slice(targetStart, targetEnd).includes('#'))) {
		return invalidPattern('Select at least one sound as the target; keep word boundaries outside parentheses.');
	}
	return { tokens, whole: false, error: '', target: targetStart == null ? null : { start: targetStart, end: targetEnd! } };
}

export function matchesPatternToken(sound: string, token: string, old = true): boolean {
	return token.startsWith(':') ? token.slice(1).split('+').every(t => matchesSound(sound, ':' + t, old)) : matchesSound(sound, token, old);
}

export interface PatternSpan { start: number; end: number; index: number; lastIndex: number; positions: number[]; contextStart: number; contextEnd: number; sound: string; outcome: string }
export function matchPattern(columns: SoundColumn[], pattern: SoundPattern, old = true): PatternSpan[] {
	if (pattern.error) return [];
	const ancestor = columns.filter(c => c.etymonSeg);
	if (!ancestor.length) return [];
	const startBound = pattern.tokens[0] === '#', endBound = pattern.tokens.at(-1) === '#';
	const tokens = pattern.tokens.filter(t => t !== '#');
	const width = pattern.whole ? ancestor.length : tokens.length;
	const matches: PatternSpan[] = [];
	for (let i = 0; i + width <= ancestor.length; i++) {
		if (startBound && i !== 0 || endBound && i + width !== ancestor.length) continue;
		if (!pattern.whole && !tokens.every((t, j) => matchesPatternToken(ancestor[i + j].etymonSeg, t, old))) continue;
		const targetStart = pattern.target ? pattern.target.start - Number(startBound) : 0;
		const targetEnd = pattern.target ? pattern.target.end - Number(startBound) : width;
		const selected = ancestor.slice(i + targetStart, i + targetEnd);
		const start = pattern.whole ? columns[0].pos : selected[0].pos;
		const end = pattern.whole ? columns.at(-1)!.pos : selected.at(-1)!.pos;
		const aligned = columns.filter(c => c.pos >= start && c.pos <= end);
		const unresolved = aligned.some(c => c.etymonSeg && isDetachedNotation(c.reflexSeg));
		matches.push({ start, end, index: i + targetStart, lastIndex: i + targetEnd - 1, positions: selected.map(c => c.pos),
			contextStart: ancestor[i].pos, contextEnd: ancestor[i + width - 1].pos,
			sound: selected.map(c => segmentKey(c.etymonSeg)).join(''),
			outcome: unresolved ? '?' : aligned.map(c => segmentKey(c.reflexSeg)).join('') || '∅' });
		if (pattern.whole) break;
	}
	return matches;
}


export function patternTokenText(token: string): string {
	if (token === ':V' || token === ':C') return token.slice(1);
	return token.startsWith(':') ? `[${token.slice(1)}]` : token;
}

/** Canonical text makes a target selectable without asking the user to type syntax. */
export function formatSoundPattern(pattern: SoundPattern, target: TargetRange | null = pattern.target): string {
	if (pattern.whole) return '*';
	return pattern.tokens.map((token, i) =>
		`${target?.start === i ? '(' : ''}${patternTokenText(token)}${target?.end === i + 1 ? ')' : ''}`
	).join(' ');
}

export function targetSelectedText(text: string, start: number, end: number): { text: string; caret: number } {
	if (start === end) return { text, caret: end };
	const strip = (s: string) => s.replace(/[()]/g, '');
	const before = strip(text.slice(0, start)), selected = strip(text.slice(start, end)), after = strip(text.slice(end));
	return { text: `${before}(${selected})${after}`, caret: before.length + selected.length + 2 };
}

/** Insert at the caret; within a class, add a conjunct rather than nesting brackets. */
export function insertPatternClass(text: string, start: number, end: number, name: string): { text: string; caret: number } {
	const open = text.lastIndexOf('[', start - 1), close = text.indexOf(']', start);
	if (name !== '#' && open >= 0 && close >= end && text.lastIndexOf(']', start - 1) < open) {
		const content = start === end ? text.slice(open + 1, close) : text.slice(open + 1, start) + name + text.slice(end, close);
		const names = content.split(/[+&,\s]+/).filter(Boolean);
		if (start === end && !names.includes(name)) names.push(name);
		const replacement = `[${names.join('+')}]`;
		return { text: text.slice(0, open) + replacement + text.slice(close + 1), caret: open + replacement.length - 1 };
	}
	const token = ['V', 'C', '#'].includes(name) ? name : `[${name}]`;
	const before = text.slice(0, start), after = text.slice(end);
	const lead = before && !/[\s(]$/.test(before) ? ' ' : '';
	const trail = after && !/^[\s)]/.test(after) ? ' ' : '';
	return { text: before + lead + token + trail + after, caret: before.length + lead.length + token.length };
}
