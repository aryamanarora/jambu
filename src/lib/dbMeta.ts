// Metadata shared between the main thread and the SQLite worker.
//
// DB_VERSION namespaces the copy cached in OPFS. Bump it whenever the deployed database changes
// so returning visitors re-download instead of querying a stale cached copy.
export const DB_VERSION = '39';

/** Path of the DB inside the OPFS SAHPool VFS (versioned for cache-busting). */
export const OPFS_DB_PATH = `/jambu-v${DB_VERSION}.db`;

/** Exact sizes for the downloadable Zstandard artifact and its local SQLite image. */
export const DB_DOWNLOAD_BYTES = 60_765_561; // static/db/jambu.db.zst, db-v39
export const DB_LOCAL_BYTES = 169_197_568; // expanded SQLite image
