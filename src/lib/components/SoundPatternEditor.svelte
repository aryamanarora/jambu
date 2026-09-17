<script lang="ts">
	import { tick } from 'svelte';
	import { parseSoundPattern, formatSoundPattern, patternTokenText, insertPatternClass, targetSelectedText } from '$lib/soundPattern';

	let { value, old, onChange, onSubmit }: {
		value: string;
		old: boolean;
		onChange: (value: string) => void;
		onSubmit: () => void;
	} = $props();
	let root = $state<HTMLDivElement | null>(null);
	let input = $state<HTMLInputElement | null>(null);
	let picker = $state<HTMLDivElement | null>(null);
	let availableHeight = $state(500);
	let editing = $state(false), focused = $state(false);
	let selection = $state({ start: 0, end: 0 });
	let anchor = $state<number | null>(null);
	const parsed = $derived(parseSoundPattern(value, old));
	$effect(() => {
		if (editing) {
			parsed.error;
			void tick().then(() => { if (picker) availableHeight = Math.max(160, window.innerHeight - picker.getBoundingClientRect().top - 16); });
		}
	});
	const classes = [
		{ label: 'Vowels', values: [['V', 'Any vowel'], ['short', 'Short'], ['long', 'Long'], ['high', 'High']] },
		{ label: 'Consonants', values: [['C', 'Any consonant'], ['stop', 'Stop'], ['nasal', 'Nasal'], ['sibilant', 'Sibilant'], ['retroflex', 'Retroflex'], ['aspirated', 'Aspirated']] }
	];
	const tokenLabel = (token: string) => token === ':V' ? 'Vowel' : token === ':C' ? 'Consonant' : token.startsWith(':') ? token.slice(1).replaceAll('+', ' + ') : token;
	const isTarget = (index: number) => parsed.tokens[index] !== '#' && (!parsed.target || index >= parsed.target.start && index < parsed.target.end);
	function rememberSelection() {
		selection = { start: input?.selectionStart ?? value.length, end: input?.selectionEnd ?? value.length };
	}
	function leave(event: FocusEvent) {
		if (!root?.contains(event.relatedTarget as Node | null)) editing = false;
	}
	function finish() {
		editing = false;
		focused = false;
		if (document.activeElement instanceof HTMLElement && root?.contains(document.activeElement)) document.activeElement.blur();
	}
	async function write(result: { text: string; caret: number }) {
		onChange(result.text);
		await tick();
		input?.focus();
		input?.setSelectionRange(result.caret, result.caret);
		rememberSelection();
	}
	function insertClass(name: string) {
		anchor = null;
		void write(value.trim() === '*' || value.trim() === ':word'
			? insertPatternClass('', 0, 0, name)
			: insertPatternClass(value, selection.start, selection.end, name));
	}
	function selectTarget(index: number, extend: boolean) {
		const start = extend ? anchor ?? parsed.target?.start ?? index : index;
		anchor = start;
		const text = formatSoundPattern(parsed, { start: Math.min(start, index), end: Math.max(start, index) + 1 });
		void write({ text, caret: text.length });
	}
	function alignAll() {
		anchor = null;
		const text = formatSoundPattern(parsed, null);
		void write({ text, caret: text.length });
	}
	function addBoundary(start: boolean) {
		anchor = null;
		const text = formatSoundPattern(parsed);
		const result = start ? text.startsWith('#') ? text : '# ' + text : text.endsWith('#') ? text : text + ' #';
		void write({ text: result, caret: start ? 0 : result.length });
	}
	const keepSelection = (event: PointerEvent) => event.preventDefault();
</script>

<div class="sound-pattern" bind:this={root} role="group" aria-label="Sound pattern editor" onfocusin={() => editing = true} onfocusout={leave}>
	<label for="sound-pattern-input">Sound sequence or classes</label>
	<div class="field">
		<input id="sound-pattern-input" bind:this={input} value={value}
			class:parsed={!focused && !parsed.error} spellcheck="false" autocomplete="off"
			placeholder="V (k) V, [retroflex], or *"
			aria-describedby="sound-pattern-help" aria-invalid={!!parsed.error}
			onfocus={() => { focused = true; editing = true; }} onblur={() => focused = false}
			onselect={rememberSelection} onclick={rememberSelection} onkeyup={rememberSelection}
			oninput={event => { anchor = null; editing = true; onChange(event.currentTarget.value); rememberSelection(); }}
			onkeydown={event => {
				if (event.key === 'Escape') { event.preventDefault(); finish(); }
				if (event.key === 'Enter' && !parsed.error) { event.preventDefault(); finish(); onSubmit(); }
			}}
		/>
		{#if !focused && !parsed.error}
			<div class="parsed-sequence" aria-hidden="true">
				{#if parsed.whole}<span class="token target">Whole form</span>
				{:else}{#each parsed.tokens as token, index}<span class="token" class:target={isTarget(index)} class:boundary={token === '#'}>{tokenLabel(token)}</span>{/each}{/if}
			</div>
		{/if}
	</div>
	<p id="sound-pattern-help" class:error={!!parsed.error}>
		{#if parsed.error}{parsed.error}
		{:else if parsed.target}Highlighted sounds are aligned; the rest is context.
		{:else}All matched sounds are aligned. Focus to choose classes or a smaller target.{/if}
	</p>
	{#if editing}
		<div class="picker" bind:this={picker} style:--available-height={`${availableHeight}px`} role="group" aria-label="Build sound pattern">
			<div class="picker-head"><strong>Build a pattern</strong><button type="button" onclick={finish}>Done</button></div>
			{#if !parsed.whole && !parsed.error}
				<div class="target-picker">
					<span class="section-label">Align these sounds</span>
					<div class="tokens">
						{#each parsed.tokens as token, index}
							{#if token === '#'}<span class="token boundary" title="Word edge">#</span>
							{:else}<button type="button" class="token" class:target={isTarget(index)} aria-pressed={isTarget(index)} aria-label="Align {patternTokenText(token)} at position {index + 1}" onpointerdown={keepSelection} onclick={event => selectTarget(index, event.shiftKey)}>{tokenLabel(token)}</button>{/if}
						{/each}
					</div>
					<p>Click a token; Shift-click to extend the target.</p>
					<div class="target-actions"><button type="button" onpointerdown={keepSelection} onclick={alignAll}>Align all sounds</button><button type="button" disabled={selection.start === selection.end} onpointerdown={keepSelection} onclick={() => { anchor = null; void write(targetSelectedText(value, selection.start, selection.end)); }}>Align selected text</button></div>
				</div>
			{/if}
			{#each classes as group}
				<div class="class-group"><span class="section-label">{group.label}</span><div>{#each group.values as [id, label]}<button type="button" aria-label="Insert {label.toLowerCase()} class" onpointerdown={keepSelection} onclick={() => insertClass(id)}>{label}</button>{/each}</div></div>
			{/each}
			<div class="syntax"><button type="button" disabled={parsed.whole || !!parsed.error} onpointerdown={keepSelection} onclick={() => addBoundary(true)}># Word start</button><button type="button" disabled={parsed.whole || !!parsed.error} onpointerdown={keepSelection} onclick={() => addBoundary(false)}>Word end #</button><span>Combine descriptors inside brackets: <code>[retroflex+stop]</code>.</span></div>
			<p class="example"><code>V (k) V</code> matches k between vowels and counts only its aligned outcome.</p>
		</div>
	{/if}
</div>

<style>
	.sound-pattern { position:relative; margin-top:.6rem; min-width:0; }
	label { display:block; margin-bottom:.4rem; font-size:.76rem; color:var(--muted); }
	.field { display:grid; min-width:0; }
	input { grid-area:1/1; width:100%; min-width:0; min-height:46px; box-sizing:border-box; padding:.55rem .7rem; border:1px solid var(--border); border-radius:.35rem; background:var(--surface); color:var(--ink); font:1.05rem var(--font-phon); }
	input.parsed { color:transparent; caret-color:transparent; }
	input.parsed::placeholder { color:transparent; }
	input:focus-visible, button:focus-visible { outline:2px solid var(--plum-2); outline-offset:2px; }
	.parsed-sequence { grid-area:1/1; display:flex; align-items:center; flex-wrap:wrap; gap:.3rem; padding:.5rem .65rem; pointer-events:none; min-width:0; }
	.token { display:inline-block; padding:.2rem .45rem; font:1rem var(--font-phon); background:var(--surface-2); color:var(--muted); border:1px solid var(--border); border-radius:.3rem; overflow-wrap:anywhere; max-width:100%; box-sizing:border-box; }
	.token.target { background:var(--plum-2); color:var(--surface); border-color:var(--plum-2); }
	.token.boundary { background:transparent; border-color:transparent; }
	p { color:var(--muted); font-size:.68rem; line-height:1.5; margin:.4rem 0 0; }
	p.error { color:var(--bad); }
	.picker { position:absolute; left:0; right:0; z-index:35; margin-top:.35rem; padding:.85rem; background:var(--surface); color:var(--ink); border:1px solid var(--border-strong); border-radius:.45rem; box-shadow:var(--shadow-md); max-height:min(65dvh,var(--available-height)); overflow:auto; box-sizing:border-box; }
	.picker-head { display:flex; align-items:center; justify-content:space-between; gap:1rem; font-size:.8rem; }
	button { font:inherit; font-size:.73rem; color:var(--ink); border:1px solid var(--border); border-radius:.3rem; background:var(--surface); padding:.35rem .5rem; cursor:pointer; }
	button:hover:not(:disabled) { border-color:var(--plum-2); }
	button:disabled { opacity:.45; cursor:default; }
	.picker-head button { color:var(--plum-2); border:0; padding:.15rem; }
	.section-label { display:block; font-size:.68rem; color:var(--muted); margin-bottom:.4rem; }
	.target-picker { border-bottom:1px solid var(--border); padding:.65rem 0; margin-bottom:.65rem; }
	.tokens, .target-actions, .class-group>div { display:flex; flex-wrap:wrap; gap:.3rem; }
	.target-actions { margin-top:.4rem; }
	.target-actions button { font-size:.66rem; }
	.class-group { margin:.6rem 0; }
	.syntax { display:flex; align-items:center; flex-wrap:wrap; gap:.4rem .6rem; font-size:.66rem; color:var(--muted); }
	.example { border-top:1px solid var(--border); padding-top:.6rem; margin-top:.65rem; }
	@media(max-width:600px) { .picker { position:relative; max-height:none; box-shadow:none; } }
</style>
