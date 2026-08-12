# npm trusted publishing

The `release-npm` job in `.github/workflows/ci.yaml` is the only workflow
authorized to publish `@namche/namche-shadow`. It runs on GitHub-hosted Linux,
requests `id-token: write`, uses Node 22.22.3 and npm 11.19.0, and does not use
an `NPM_TOKEN`.

## One-time bootstrap

npm requires a package to exist before a trusted publisher can be attached.
After the initial `0.1.0` package has been reviewed and merged to `main`, an
owner of the `namche` npm organization must authenticate locally with 2FA and
publish that first version from `packages/next`:

```sh
npm login
npm publish --access public
```

Then configure the exact GitHub Actions identity. With npm CLI 11.5.1 or
newer, the equivalent of the npmjs.com form is:

```sh
npm trust github @namche/namche-shadow \
  --repo NamcheAI/namche-shadow-font \
  --file ci.yaml \
  --allow-publish \
  --yes
```

The workflow filename is only `ci.yaml`, not `.github/workflows/ci.yaml`.
Every value is case-sensitive.

## Lock down token publishing

Verify one OIDC release before changing the package's publishing access. Then
open the package settings on npmjs.com, choose **Publishing access**, select
**Require two-factor authentication and disallow tokens**, and revoke any
obsolete automation token. Trusted publishing continues to work because it
uses short-lived OIDC credentials instead of registry tokens.

Trusted publishing automatically adds provenance for this public package from
this public repository; no `--provenance` flag or npm secret is required.
