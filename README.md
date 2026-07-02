# RouteSentry Next

RouteSentry Next maps Next.js routes to detectable authorization boundaries and flags routes that appear to rely on middleware, proxy coverage, client-side checks, or incomplete matchers.

RouteSentry Next does not prove a route is secure or insecure. It performs static authorization-boundary triage and highlights routes that need manual review.

## What It Does

- Detects basic Next.js projects with `package.json` and `app/`, `pages/`, `src/app/`, or `src/pages/`.
- Maps App Router pages, route handlers, Pages Router pages, and API routes.
- Looks for common route-level session, user, role, token, `401`, and `403` patterns.
- Parses common middleware and proxy matcher forms.
- Reports middleware-only coverage, matcher misses, and mutation endpoints without detectable route-level auth.

## What It Does Not Do

- It does not exploit CVE-2025-29927.
- It does not call external scanners, APIs, or network services.
- It does not evaluate custom authorization logic with certainty.
- It does not implement full Next.js matcher semantics.
- It does not replace manual security review.

## Why Middleware-Only Authorization Is Risky

Middleware can block many requests before they reach a route. A route-level check still matters because middleware config can miss paths, change during refactors, or fail to express per-route role rules. Sensitive handlers should validate the session or user before reading or mutating data and should return `401` or `403` when access fails.

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
routesentry scan <nextjs_project_path>
routesentry scan <path> --format table
routesentry scan <path> --format json --out routesentry-report.json
routesentry scan <path> --format markdown --out routesentry-report.md
routesentry scan <path> --format sarif --out routesentry.sarif
routesentry scan <path> --fail-on high
```

You can also run the package module:

```bash
python -m routesentry_next scan <nextjs_project_path>
```

## GitHub Action

Use the composite action to run RouteSentry Next in CI:

```yaml
name: RouteSentry Next

on:
  pull_request:
  push:
    branches: [main, master]

jobs:
  routesentry:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - uses: egeyasar0/routesentry-next@v0.1.1
        with:
          path: "."
          format: "sarif"
          output: "routesentry.sarif"
          fail-on: "high"

      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: routesentry.sarif
```

`security-events: write` is only needed when you upload SARIF to GitHub Code Scanning. SARIF output is for security-tool ingestion. RouteSentry findings are static triage signals, not proof of exploitability.

## Dry-Run Example

```text
python -m routesentry_next scan ./apps/dashboard --format table
```

Example output:

```text
Project: apps/dashboard
Next.js: 15.2.2
Score: 85
Routes: 1 | Protected-looking: 1 | Route-level auth: 0 | Middleware-only: 1 | Matcher miss: 0 | High/Medium/Low: 1/0/0
```

Example finding:

```text
RSN-001 HIGH /api/admin/users
Route appears to rely on middleware/proxy coverage without a detectable route-level authorization check.
```

Treat this as a review queue, not proof of a vulnerability. The route name, middleware matcher, and missing route-level auth pattern produced a triage signal. A reviewer still needs to inspect the route and the authorization code it calls.

SARIF output is intended for security-tool ingestion. RouteSentry findings are triage signals, not proof of exploitability.

## Supported Next.js Structures

- `app/**/page.tsx`
- `app/**/page.ts`
- `app/**/route.ts`
- `app/**/route.tsx`
- `src/app/**/page.tsx`
- `src/app/**/page.ts`
- `src/app/**/route.ts`
- `src/app/**/route.tsx`
- `pages/**/*.tsx`
- `pages/**/*.ts`
- `pages/api/**/*.ts`
- `pages/api/**/*.tsx`
- `src/pages/**/*.tsx`
- `src/pages/**/*.ts`
- `src/pages/api/**/*.ts`
- `src/pages/api/**/*.tsx`

Middleware and proxy files:

- `middleware.ts`
- `middleware.js`
- `src/middleware.ts`
- `src/middleware.js`
- `proxy.ts`
- `proxy.js`
- `src/proxy.ts`
- `src/proxy.js`

## Known Auth Patterns

RouteSentry Next checks for common patterns such as `auth()`, `getServerSession(`, `getToken(`, `currentUser(`, `auth.protect(`, `createServerClient(`, `getUser(`, `getSession(`, `requireAuth(`, `requireUser(`, `requireAdmin(`, `withAuth(`, `verifySession(`, `verifyAuth(`, `validateSession(`, session cookies, authorization headers, bearer-token checks, and `401` or `403` response branches.

It also handles shallow imported wrappers when the route imports `requireAuth`, `requireAdmin`, `withAuth`, `auth`, `getServerSession`, `currentUser`, or `createServerClient` and calls the imported local name in the same file. If the route imports one of those names but does not call it, RouteSentry Next marks the auth check as manual review.

If it finds a called pattern, it marks the route as `route_level_auth_detected`. If it does not, it reports `auth_not_detected` and leaves the route for review.

## Rules

- `RSN-001`: Protected-looking route appears covered by middleware/proxy but has no detectable route-level authorization pattern.
- `RSN-002`: Protected-looking route misses middleware/proxy matcher coverage and has no detectable route-level authorization pattern.
- `RSN-003`: Mutation API or route handler exports `POST`, `PUT`, `PATCH`, or `DELETE` without a detectable route-level authorization pattern.

## Limitations

- Matcher parsing supports common string and array forms only.
- Static pattern detection can miss custom wrappers, multi-hop imports, and indirect authorization.
- Auth detection is pattern-based and conservative. CORS response headers are not treated as authorization checks.
- Pages Router method detection supports common `req.method` comparisons and switch cases.
- Protected-looking route detection uses path names such as `/admin`, `/dashboard`, `/settings`, `/account`, `/billing`, and selected `/api/*` prefixes.
- Confidence means the static evidence matched the rule, not that the route is vulnerable.

## Roadmap

- Parse more matcher forms without claiming full Next.js semantics.
- Expand shallow wrapper detection only where tests show low false-positive risk.
- Add the optional Next.js risky-version informational check.
