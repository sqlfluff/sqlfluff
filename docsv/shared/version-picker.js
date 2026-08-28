/**
 * Version picker and stale-version notice for archived Sphinx documentation.
 *
 * Published at `/en/shared/version-picker.js`, above every version, and loaded
 * by each archived page. That is the whole point of it living here: an archived
 * version is built once and frozen, so it learns about versions published after
 * it — and picks up fixes to this file — without being rebuilt.
 *
 * The VitePress theme has its own picker component rather than loading this one.
 * Two implementations is a real cost, but the alternative is worse in both
 * directions: this file has to run inside alabaster output produced by every
 * Sphinx release SQLFluff has used since 2021, and the VitePress picker has to
 * follow the default theme's nav-bar flyouts and its client-side router. What is
 * shared is the contract — `/en/versions.json` — and the behaviour below, which
 * is kept deliberately in step with `docsv/.vitepress/theme/versions.ts`.
 *
 * Written as dependency-free ES5 against a defensive view of the DOM, because
 * the pages it runs in were built by toolchains nobody is going to re-test.
 * Anything it cannot find, it does without: the failure mode is an archived page
 * that renders exactly as Sphinx built it.
 */
(function () {
    'use strict'

    /** Where the archive index page lives, relative to the language root. */
    var VERSIONS_PAGE = 'versions.html'

    /**
     * These assets are only loaded by archived Sphinx builds, so that is the
     * builder a page is assumed to be from when the manifest does not say.
     */
    var ASSUMED_BUILDER = 'sphinx'

    // `/en/3.4.2/configuration/index.html` -> language root `/en/`, version key
    // `3.4.2`, page path `configuration/index.html`. The trailing group is
    // optional so a version root, with or without its trailing slash, is still
    // recognised rather than leaving the page without a picker.
    var location = window.location
    var match = location.pathname.match(/^(\/[^/]+\/)([^/]+)(?:\/(.*))?$/)

    if (!match) return

    var languageRoot = match[1]
    var currentKey = match[2]
    var pagePath = match[3] || ''

    function isChannel(entry) {
        return (
            entry.kind === 'channel' ||
            entry.key === 'latest' ||
            entry.key === 'stable'
        )
    }

    /**
     * Absent means listed, so entries written before the flag existed still
     * appear rather than silently emptying the picker.
     */
    function isListed(entry) {
        return entry.listed !== false
    }

    function versionTitle(entry) {
        return entry.title || entry.label || entry.key
    }

    function versionBase(entry) {
        return entry.path || languageRoot + entry.key + '/'
    }

    /**
     * Build a cross-version link, keeping the reader on the same page where
     * that is a sensible thing to attempt.
     *
     * Within one builder the page path is carried across. It may not exist in
     * the target version, and then that version's own 404 takes over — a
     * possible cost, against the certain cost of losing your place on every
     * switch.
     *
     * Across the Sphinx and VitePress boundary it stops being a possible cost
     * and becomes a certain one. The two lay out URLs differently
     * (`configuration/index.html` against `configuration/`) and the docs were
     * restructured in the rewrite, so the path is dropped and the reader lands
     * on the target version's home page instead.
     */
    function hrefFor(entry, currentBuilder) {
        var base = versionBase(entry)

        if (entry.builder && currentBuilder && entry.builder !== currentBuilder) {
            return base
        }

        return base + pagePath
    }

    function el(tag, className, text) {
        var node = document.createElement(tag)

        if (className) node.className = className
        if (text) node.appendChild(document.createTextNode(text))

        return node
    }

    /**
     * The versions offered in the picker: the listed ones, plus whichever
     * version the reader is actually on.
     *
     * Only one release per series is listed, which is what every comparable
     * project does. But most readers arrive on an old version from a search
     * engine, and a control which does not name the version you are reading
     * looks broken rather than curated — so the current entry is added back
     * whenever it was left out, in its manifest position.
     */
    function pickerEntries(versions) {
        var chosen = []

        for (var i = 0; i < versions.length; i++) {
            var entry = versions[i]

            if (isListed(entry) || entry.key === currentKey) chosen.push(entry)
        }

        return chosen
    }

    function buildPanel(entries, current, builder) {
        var panel = el('div', 'sqlfluff-vp__panel')
        panel.hidden = true

        var groups = [
            ['Channels', []],
            ['Releases', []],
        ]

        for (var i = 0; i < entries.length; i++) {
            groups[isChannel(entries[i]) ? 0 : 1][1].push(entries[i])
        }

        var showTitles = groups[0][1].length > 0 && groups[1][1].length > 0

        for (var g = 0; g < groups.length; g++) {
            var members = groups[g][1]

            if (!members.length) continue

            var group = el('div', 'sqlfluff-vp__group')

            if (showTitles) {
                group.appendChild(
                    el('p', 'sqlfluff-vp__group-title', groups[g][0])
                )
            }

            for (var m = 0; m < members.length; m++) {
                group.appendChild(buildItem(members[m], current, builder))
            }

            panel.appendChild(group)
        }

        // The way to reach the versions this list leaves out. Last, and in its
        // own group, so it reads as an escape hatch rather than as a version.
        var footer = el('div', 'sqlfluff-vp__group')
        var all = el('a', 'sqlfluff-vp__item sqlfluff-vp__item--all', 'All versions')
        all.href = languageRoot + VERSIONS_PAGE
        all.appendChild(el('span', 'sqlfluff-vp__arrow', '→'))
        footer.appendChild(all)
        panel.appendChild(footer)

        return panel
    }

    function buildItem(entry, current, builder) {
        var item = el('a', 'sqlfluff-vp__item')
        item.href = hrefFor(entry, builder)
        item.appendChild(el('span', 'sqlfluff-vp__item-title', versionTitle(entry)))

        if (entry.key === current.key) {
            item.className += ' is-current'
            item.setAttribute('aria-current', 'page')
        }

        if (entry.prerelease) {
            item.appendChild(el('span', 'sqlfluff-vp__tag', 'pre-release'))
        }

        return item
    }

    function mountPicker(panel, trigger, root) {
        function setOpen(open) {
            panel.hidden = !open
            trigger.setAttribute('aria-expanded', String(open))
        }

        trigger.addEventListener('click', function () {
            setOpen(panel.hidden)
        })

        document.addEventListener('keydown', function (event) {
            if (event.key !== 'Escape' || panel.hidden) return

            setOpen(false)
            trigger.focus()
        })

        document.addEventListener('mousedown', function (event) {
            if (panel.hidden || root.contains(event.target)) return

            setOpen(false)
        })
    }

    /**
     * Which version a reader on this page should be sent to instead, or null if
     * there is nowhere better.
     *
     * Decided from the manifest's ordering rather than from any date, matching
     * `useVersions` in the VitePress theme: releases are sorted newest-first by
     * `version_sort_key`, so anything but the first is superseded.
     */
    function recommendedFor(current, versions, stableKey) {
        var releases = []
        var stableChannel = null
        var stableRelease = null

        for (var i = 0; i < versions.length; i++) {
            var entry = versions[i]

            if (isChannel(entry)) {
                if (entry.key === 'stable') stableChannel = entry
                continue
            }

            releases.push(entry)
            if (entry.key === stableKey) stableRelease = entry
        }

        var target = stableRelease || stableChannel || releases[0] || null

        if (!target || target.key === current.key) return null

        // `latest` tracks main, and a prerelease is not what a reader landing
        // from a search result is usually after.
        if (current.key === 'latest' || current.prerelease) return target

        if (isChannel(current)) return null

        return releases.indexOf(current) > 0 ? target : null
    }

    function buildBanner(current, target, builder) {
        var banner = el('div', 'sqlfluff-vb', null)
        var isDevelopment = current.key === 'latest'

        banner.setAttribute('role', 'status')
        banner.appendChild(
            document.createTextNode(
                isDevelopment
                    ? 'You are reading the development documentation, which ' +
                      'tracks the main branch. '
                    : 'You are reading the documentation for SQLFluff ' +
                      (current.label || current.key) +
                      ', which is not the current release. '
            )
        )

        var link = el('a', null, 'Switch to ' + versionTitle(target))
        link.href = hrefFor(target, builder)
        banner.appendChild(link)

        return banner
    }

    /**
     * Alabaster has kept `.sphinxsidebarwrapper` across every vintage in this
     * project's history. The fixed-corner fallback means a page which does not
     * have it still gets a picker rather than losing it silently.
     */
    function insertPicker(root) {
        var sidebar = document.querySelector('.sphinxsidebarwrapper')

        if (sidebar) {
            sidebar.insertBefore(root, sidebar.firstChild)
            return
        }

        root.className += ' sqlfluff-vp--floating'
        document.body.appendChild(root)
    }

    function insertBanner(banner) {
        var host =
            document.querySelector('div.body') ||
            document.querySelector('.documentwrapper') ||
            document.body

        host.insertBefore(banner, host.firstChild)
    }

    function render(manifest) {
        var versions = (manifest && manifest.versions) || []
        var current = null

        for (var i = 0; i < versions.length; i++) {
            if (versions[i].key === currentKey) current = versions[i]
        }

        // A version can be live before the manifest names it — the manifest is
        // rewritten by whichever publish ran last. Standing in for the entry
        // keeps the picker working and, more importantly, keeps the page from
        // claiming to be a version it is not.
        if (!current) {
            current = {
                key: currentKey,
                label: currentKey,
                path: languageRoot + currentKey + '/',
                builder: ASSUMED_BUILDER,
            }
            versions = versions.concat([current])
        }

        var builder = current.builder || ASSUMED_BUILDER
        var entries = pickerEntries(versions)

        // Nothing to switch to. The version is still worth stating, so it
        // renders as a label rather than as a control which opens an empty list.
        var root = el('div', 'sqlfluff-vp')
        var label = isChannel(current)
            ? current.label || current.key
            : 'v' + (current.label || current.key)

        root.appendChild(el('span', 'sqlfluff-vp__label', 'Version'))

        if (entries.length < 2) {
            root.appendChild(el('span', 'sqlfluff-vp__static', label))
            insertPicker(root)
            return
        }

        var trigger = el('button', 'sqlfluff-vp__trigger', label)
        trigger.type = 'button'
        trigger.setAttribute('aria-expanded', 'false')
        trigger.appendChild(el('span', 'sqlfluff-vp__chevron', '▾'))

        var panel = buildPanel(entries, current, builder)
        root.appendChild(trigger)
        root.appendChild(panel)
        mountPicker(panel, trigger, root)
        insertPicker(root)

        var target = recommendedFor(current, versions, manifest && manifest.stable)

        if (target) insertBanner(buildBanner(current, target, builder))
    }

    function start() {
        fetch(languageRoot + 'versions.json', {
            headers: { Accept: 'application/json' },
        })
            .then(function (response) {
                if (!response.ok) throw new Error('manifest ' + response.status)

                return response.json()
            })
            .then(render)
            // An unreachable manifest leaves the page exactly as Sphinx built
            // it, which is a working page without a picker.
            .catch(function (error) {
                console.error(error)
            })
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start)
    } else {
        start()
    }
})()
