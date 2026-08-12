/**
 * Copy the installed SQLFluff Design assets into the VitePress public directory.
 *
 * The shared design package is installed as the `@sqlfluff/design` dependency
 * and is treated as read-only. This runs before `docs:dev` and `docs:build` so
 * the assets are served from this site rather than fetched from another
 * SQLFluff origin at runtime.
 */

import { createRequire } from 'node:module'
import { cpSync, existsSync, rmSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(scriptDir, '../..')
const require = createRequire(import.meta.url)

function resolveDesignSource() {
    try {
        const manifest = require.resolve('@sqlfluff/design/package.json')
        return resolve(dirname(manifest), 'static/sqlfluff-design')
    } catch {
        return null
    }
}

export const DESIGN_SOURCE = resolveDesignSource()

const target = resolve(repoRoot, 'docsv/public/sqlfluff-design')

/** Fail with actionable guidance rather than a build-time module error. */
export function assertDesignPackage() {
    if (DESIGN_SOURCE && existsSync(DESIGN_SOURCE)) return

    throw new Error(
        `Shared design package not found${DESIGN_SOURCE ? ` at ${DESIGN_SOURCE}` : ''}.\n` +
        'Install dependencies first:\n' +
        '  corepack pnpm install'
    )
}

function sync() {
    assertDesignPackage()

    // Mirror rather than merge, so assets removed upstream do not linger.
    rmSync(target, { recursive: true, force: true })
    cpSync(DESIGN_SOURCE, target, { recursive: true })

    console.log(`Synced shared design assets to ${target}`)
}

// Only run when invoked directly, so the config can import the helpers.
if (process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))) {
    sync()
}
