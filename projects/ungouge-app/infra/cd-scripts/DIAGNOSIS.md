# Root-Cause Diagnosis: Cloud Build Push Failures

## Summary (3 lines)

The Docker image **builds successfully** but **push fails at the attestation manifest** step.
Docker buildx v0.12+ generates provenance/SBOM attestation manifests by default. When pushing
to Artifact Registry, the HEAD request for the attestation layer returns **400 Bad Request**,
aborting the entire push even though all 11 image layers were already pushed successfully.

## Key Log Excerpt

```
d85099f0969e: Pushed
66f85aa6d668: Pushed
...
cef130c08454: Pushed
unknown: unexpected status from HEAD request to
  https://us-central1-docker.pkg.dev/v2/ungouge-app/ungouge-backend/manifests/
  sha256:7aabd5d03e54776c7a48b7fbcf1c5a8e64c26e247c90bc7cfd8e3120fdb2bc52: 400 Bad Request
PUSH_FAIL us-central1-docker.pkg.dev/ungouge-app/ungouge-backend:autodeploy-1771192731
```

The sha256 `7aabd5d...` corresponds to `exporting attestation manifest` in the build log.

## Fix

Build with `--provenance=false --sbom=false` (or `BUILDX_NO_DEFAULT_ATTESTATIONS=1`)
to suppress the attestation manifest that AR chokes on. This is the standard workaround
for AR + buildx. Alternatively, use `docker build` (legacy builder) instead of buildx.

## Secondary Issue: Existing deploy_backend.sh

The existing `infra/deploy_backend.sh` targets `gcr.io` (Container Registry), doesn't pass
`--provenance=false`, and doesn't map secrets into Cloud Run (only prints a suggestion).
The new scripts fix all of this.
