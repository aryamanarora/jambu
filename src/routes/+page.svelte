<script lang="ts">
	import { base } from '$app/paths';
</script>

<svelte:head>
	<title>Jambu — an etymological dictionary of South Asian languages</title>
	<meta
		name="description"
		content="Jambu is a modern online etymological dictionary of the South Asian languages — Indo-Aryan, Dravidian, Munda, and more."
	/>
</svelte:head>

<div class="floater">
	<h2>Cite</h2>
	<p>
		Aryaman Arora, Adam Farris, Samopriya Basu, and Suresh Kolichala. 2023.
		“<a href="https://arxiv.org/abs/2306.02514">Jambu: A historical linguistic database for South
			Asian languages</a>.” <em>SIGMORPHON</em>.
	</p>
</div>

<h1>Welcome to <em>Jambu</em></h1>
<p class="lead">
	<em>Jambu</em> is a modern online etymological dictionary of the South Asian languages.
</p>
<p>
	The <em>Jambu</em> project seeks to modernise and consolidate previous work on the historical and
	comparative lexicography of the South Asian languages—including the Indo-Aryan, Dravidian, Munda,
	and Sino-Tibetan language families. It is a spiritual continuation of the print dictionaries by
	Turner (<em>CDIAL</em>) and Burrow and Emeneau (<em>DEDR</em>), as well as the more recent online
	attempts at such a resource by the
	<a href="http://www.aa.tufs.ac.jp/sarva/">SARVA project</a> and
	<a href="http://kolichala.com/DEDR/">Suresh Kolichala’s <em>DEDR</em> search interface</a>.
</p>

<h3>A brief overview</h3>
<ul>
	<li>
		<a href="{base}/entries">Entries</a> is a list of headwords. Clicking on an entry gives a map, list
		of descendants/cognates, and the CDIAL headword line.
	</li>
	<li>
		<a href="{base}/reflexes">Reflexes</a> is the entire lexicon, including all entries in all languages.
		Each lemma includes a link to the source it was derived from, as well as assorted lexicographic
		information.
	</li>
	<li>
		<a href="{base}/languages">Languages</a> is all of the included languages. Clicking a language gives
		its lexicon.
	</li>
	<li><a href="{base}/references">References</a> is a list of sources.</li>
</ul>

<p>
	<em>Jambu</em> is named for the Indian blackberry, i.e.
	<a href="{base}/entries/5131"><em>jambú</em> <span class="id-tag">[5131]</span></a>
	or <em>Syzygium cumini</em>. India was historically referred to as
	<a href="{base}/entries/5134"><em>jambudvīpa</em> <span class="id-tag">[5134]</span></a>.
</p>
