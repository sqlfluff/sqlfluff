# VitePress Documentation - Proof of Concept

This is a proof of concept (POC) for migrating SQLFluff documentation from Sphinx to VitePress.

## What's Included

This POC demonstrates:

1. **Automated Rule Documentation** - Extracts all SQLFluff rules and generates Markdown documentation
2. **Automated Dialect Documentation** - Extracts dialect info
3. **Automated CLI Documentation** - Extracts CLI commands and options
4. **API Documentation** - Uses pydoc-markdown to extract Python docstrings from the API
5. **Redirect System** - Converts Sphinx redirects to VitePress format for backward compatibility
6. **Build Pipeline** - Automated script to generate all documentation before VitePress builds

## Directory Structure

```
docsv/
├── .vitepress/
│   ├── config.ts           # Main VitePress configuration
│   ├── sidebar-rules.json  # Auto-generated sidebar config for rules
│   └── redirects.json      # Auto-generated redirects
├── scripts/
│   ├── generate-rules-docs.py    # Extract and convert rule documentation
│   ├── generate-dialect-docs.py  # Extract and convert dialect documentation
│   ├── generate-cli-docs.py      # Extract and convert CLI documentation
│   ├── extract-redirects.py      # Convert Sphinx redirects to VitePress
│   └── generate-all-docs.py      # Master build script
├── reference/
│   ├── rules/              # Auto-generated rule docs (by bundle)
│   ├── dialects/           # Auto-generated dialect docs
│   └── cli/                # Auto-generated CLI docs
│   └── api/                # Auto-generated API docs
├── public/                 # Static assets
├── pydoc-markdown.yml      # Configuration for API doc generation
├── package.json            # Node.js dependencies and scripts
└── index.md                # Home page
```

## Setup

### 1. Install Python Dependencies

Install pydoc-markdown (for API documentation):

```bash
pip install pydoc-markdown
```

### 2. Install Node.js Dependencies

```bash
cd docsv
pnpm install
```

## Usage

### Generate Documentation

Run the master build script to generate all documentation:

```bash
cd docsv
python scripts/generate-all-docs.py
```

This will:
- Extract all rules and generate `reference/rules/*.md` files
- Extract dialect and CLI documentation
- Generate API documentation with pydoc-markdown
- Extract redirects from Sphinx `conf.py`
- Create sidebar configuration

### Development Server

Start the VitePress development server with hot reload:

```bash
pnpm run docs:dev
```

Then open http://localhost:5173 in your browser.

### Build for Production

Build static HTML for deployment:

```bash
pnpm run docs:build
```

Output will be in `.vitepress/dist/`.

### Preview Production Build

Preview the production build locally:

```bash
pnpm run docs:preview
```

## Key Features Demonstrated

### Rule Documentation

- ✅ Extracts all SQLFluff rules using plugin system
- ✅ Converts RST docstrings to Markdown
- ✅ Handles code blocks, **Anti-pattern**/**Best practice** sections
- ✅ Groups rules by bundle (layout, capitalisation, etc.)
- ✅ Generates summary tables with links
- ✅ Shows aliases, groups, and fix compatibility
- ✅ Auto-generates sidebar configuration

### API Documentation

- ✅ Uses pydoc-markdown for docstring extraction
- ✅ Supports Google-style docstrings (used by SQLFluff)
- ✅ Generates clean Markdown from Python code
- ✅ Includes function signatures, parameters, and return types

### Redirects

- ✅ Parses Sphinx `rediraffe_redirects` from `conf.py`
- ✅ Converts ~90 redirects to VitePress format
- ✅ Maintains backward compatibility with permalinks
- ✅ Outputs both JSON and TypeScript formats

### Build System

- ✅ Automated pre-build step before VitePress
- ✅ Maintains separation between generated and manual content
- ✅ Fast rebuilds with VitePress hot module replacement
- ✅ Integrated npm scripts for easy workflow


## Validation Checklist

To validate this POC:

- [ ] Run `python scripts/generate-all-docs.py` - should complete without errors
- [ ] Check `reference/rules/` - should have ~10 markdown files (one per bundle)
- [ ] Verify rule documentation has proper formatting and code blocks
- [ ] Run `npm run docs:dev` - should start dev server
- [ ] Navigate to rules section - verify layout, links, and anchors work
- [ ] Check that redirects are loaded in `.vitepress/redirects.json`
- [ ] Test search functionality with rule codes (e.g., "LT01")
- [ ] Verify API documentation generated (if pydoc-markdown installed)

## Next Steps

If this POC is approved:

1. **Phase 2**: Convert remaining 43 RST files to Markdown (manual + script)
4. **Phase 3**: Implement all redirects and test thoroughly
5. **Phase 4**: Add custom Vue components for enhanced UX


## Feedback

Please test this POC and provide feedback on:

1. Documentation quality and formatting
2. Build process ease of use
3. Performance compared to Sphinx
4. Any missing features critical for migration
5. Overall approach and architecture
