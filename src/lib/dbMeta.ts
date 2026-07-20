// Metadata shared between the main thread and the SQLite worker.
//
// DB_VERSION namespaces the copy cached in OPFS. Bump it whenever the deployed jambu.db changes
// so returning visitors re-download instead of querying a stale cached copy.
export const DB_VERSION = '5';

/** Path of the DB inside the OPFS SAHPool VFS (versioned for cache-busting). */
export const OPFS_DB_PATH = `/jambu-v${DB_VERSION}.db`;

/** Approximate uncompressed DB size, used only to render a download progress bar. */
export const DB_APPROX_BYTES = 309_000_000;
