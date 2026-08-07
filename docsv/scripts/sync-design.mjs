/**
 * Copy the vendored SQLFluff Design assets into the VitePress public directory.
 *
 * The shared design package lives in the `vendor/sqlfluff.com` submodule and is
 * treated as read-only. This runs before `docs:dev` and `docs:build` so the
 * assets are served from this site rather than fetched from another SQLFluff
 * origin at runtime.
 */

import { cpSync, existsSync, rmSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(scriptDir, '../..')

export const DESIGN_SOURCE = resolve(
    repoRoot,
    'vendor/sqlfluff.com/packages/design/static/sqlfluff-design'
)

const target = resolve(repoRoot, 'docsv/public/sqlfluff-design')

/** Fail with actionable guidance rather than a build-time module error. */
export function assertDesignPackage() {
    if (existsSync(DESIGN_SOURCE)) return

    throw new Error(
        `Shared design package not found at ${DESIGN_SOURCE}.\n` +
        'Initialise the submodule first:\n' +
        '  git submodule update --init vendor/sqlfluff.com'
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
