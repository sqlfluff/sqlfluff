/**
 * Shared helpers for VitePress base-path handling.
 *
 * These keep config, the main theme, and the 404 redirect handling aligned
 * when docs are built under different prefixes such as /sqlfluff/ or
 * /en/latest/.
 */

/** Normalize a docs base so it always has leading and trailing slashes. */
export function normalizeBase(
    value: string | undefined,
    fallback = '/'
): string {
    let base = value || fallback

    if (!base.startsWith('/')) {
        base = `/${base}`
    }

    if (!base.endsWith('/')) {
        base = `${base}/`
    }

    return base
}

/** Join a docs-relative path onto a normalized docs base. */
export function withDocsBase(base: string, path: string): string {
    return `${base}${path.replace(/^\//, '')}`
}

/**
 * Strip the docs base from a URL path so redirect keys can be matched against
 * the generated redirects map.
 */
export function normalizePath(path: string, base: string): string {
    const normalizedBase = normalizeBase(base)
    const [pathname] = path.split(/[?#]/, 1)

    if (pathname.startsWith(normalizedBase)) {
        return pathname.slice(normalizedBase.length).replace(/\/$/, '')
    }

    return pathname.replace(/^\//, '').replace(/\/$/, '')
}

/** Convert a redirect target back into a base-aware browser path. */
export function toRedirectPath(target: string, base: string): string {
    return withDocsBase(normalizeBase(base), target)
}