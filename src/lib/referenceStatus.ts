export function referenceProgress(progress: string | null): 'ok' | 'warn' | 'bad' {
	return progress === 'Yes' ? 'ok' : progress === 'Partial' ? 'warn' : 'bad';
}

export function unetymologisedPercent(total: number, unetymologised: number): string {
	return total ? `${((unetymologised / total) * 100).toFixed(1)}%` : '—';
}
