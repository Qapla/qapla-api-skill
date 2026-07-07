# Couriers — delivery benchmarks (v2)

**Resource:** `https://api.qapla.it/v2/couriers/*`
**Auth:** Bearer JWT (see [`authentication.md`](authentication.md)).

These two endpoints are cross-merchant **network benchmarks** for a destination
Italian postal code: given a `destCap` and a list of courier codes, they tell you
which courier is fastest (`delivery-times`) or best overall
(`efficiency-index`). The data is anonymous (no PII) and shared across the whole
Qapla' network, not filtered to your own company — they are read-only, nothing is
created or changed.

> v2 surface as of `qore/api` **2.12.0** (2026-07-06). Both endpoints share the
> same request shape and origin-resolution rules; documented together to avoid
> repetition. This is distinct from the general `couriers` **resource**
> (list / get by code), which is still in flight — see
> [`endpoints.md`](endpoints.md).
>
> **Entitlement note:** both are internally billable "network analytics"
> features, but the product gate (`#[RequiresProduct]` → `403
> PRODUCT_NOT_OWNED`) is **not wired yet** in the controller (explicit `TODO` in
> the code) — for now, a valid token with the right scope is enough. Expect a
> product-ownership check to appear later; don't hardcode against its absence.

## Shared request shape

| Field | Required | Meaning |
|---|---|---|
| `destCap` | yes | 5-digit destination Italian postal code (e.g. `20100`) |
| `couriers` | no | Courier codes to compare/score, max 50. Omit (or send empty) to use the channel's shipping-enabled couriers |
| `weightKg` | no | Parcel weight in kg, must be `> 0` — selects a weight-specific band. Omit for a weight-agnostic result |
| `originCap` | no | 5-digit postal code overriding the origin. Otherwise the authenticated company's seat CAP is used |

Origin resolution is server-side and identical for both endpoints: the seat CAP
of the authenticated company, unless `originCap` overrides it. The response also
carries `originArea` (`NORD` / `CENTRO` / `SUD`, `null` if not resolvable) and
`requestedWeightBand` (e.g. `"2-5"`, `null` if `weightKg` was omitted). Speed
metrics are always **calendar days**.

## Compare delivery times — `POST /v2/couriers/delivery-times`

Scope: `delivery-times:read`. Ranks couriers **fastest-first** by lead time
(shipped→delivered — the primary/ranking metric); also reports transit time
(departed→delivered, carrier-only, history starting ~2026).

Extra request field — `detail`: `"summary"` (default) returns `best` + a slim
`ranking`; `"full"` returns the complete ranking with all percentiles, the
benchmark `level`, `weightBand`, and insufficient-data couriers appended with
`status: "insufficient_data"`.

**Response (`detail: "summary"`, default):**

```json
{
  "destCap": "20100",
  "originCap": "20121",
  "originArea": "NORD",
  "requestedWeightBand": "2-5",
  "best": {
    "courierCode": "BRT",
    "leadMedian": 2, "leadMean": 2.1,
    "transitMedian": 1, "transitMean": 1.3,
    "sampleSize": 1673
  },
  "ranking": [
    { "position": 1, "courierCode": "BRT", "leadMedian": 2, "transitMedian": 1, "sampleSize": 1673 }
  ]
}
```

`best` is `null` when no courier has sufficient data; `ranking` omits
insufficient-data couriers (ask for `detail: "full"` to see them).

Samples: [request](../examples/v2/deliveryTimes.request.json) /
[response](../examples/v2/deliveryTimes.response.json) (summary),
[request](../examples/v2/deliveryTimesFull.request.json) /
[response](../examples/v2/deliveryTimesFull.response.json) (`detail: "full"`).

In `full` mode there is **no** `best` field; every requested courier appears in
`ranking`, ordered by lead **median, then mean, then p90**, each row adding
`status` (`ok` \| `insufficient_data`), `level` (benchmark grain, finest to
coarsest: `origin_cap_dest_weight` → `origin_cap_dest` → `area_cap_weight` →
`cap_weight` → `area_cap` → `cap`), `weightBand`, `leadMean`, `transitMean`,
`leadP90`, `transitP90`, `transitSampleSize`.

Errors: `401` (bad/missing token), `403` (missing `delivery-times:read` scope),
`422` (invalid `destCap`/`originCap`, or no couriers to compare), `429`.

## Score courier efficiency — `POST /v2/couriers/efficiency-index`

Scope: `efficiency-index:read`. Same request shape, **no** `detail` param
(always full detail). Returns a **0–100 efficiency index** per courier — not
just speed — blending three sub-scores with fixed network weights **40/20/40**:

- `scoreSpeed` — from the speed median (transit if available, else lead)
- `scoreConsistency` — from the gap between p90 and median
- `scoreReliability` — from the lane's failed / stock / exception rates

`efficiencyIndex = 0.40·scoreSpeed + 0.20·scoreConsistency + 0.40·scoreReliability`,
rounded to 1 decimal.

```json
{
  "destCap": "20100",
  "originCap": "20121",
  "originArea": "NORD",
  "requestedWeightBand": "2-5",
  "ranking": [
    {
      "rank": 1, "courierCode": "BRT", "status": "ok",
      "efficiencyIndex": 87.6,
      "scoreSpeed": 86.0, "scoreConsistency": 86.0, "scoreReliability": 90.0,
      "level": "origin_cap_dest_weight", "sampleSize": 1673,
      "speedMedian": 2, "speedP90": 3,
      "failedRate": 0.02, "stockRate": 0.0, "exceptionRate": 0.04
    }
  ]
}
```

Samples: [request](../examples/v2/efficiencyIndex.request.json) /
[response](../examples/v2/efficiencyIndex.response.json).

`ranking` is ordered best-first by `efficiencyIndex`; ties share a `rank`.
Couriers whose lane cell is suppressed (fewer than 20 deliveries) or has no
usable speed are appended at the end with `status: "insufficient_data"`,
`rank: null` and null metrics.

Errors: `401`, `403` (missing `efficiency-index:read` scope), `422` (invalid
`destCap`/`originCap`, or no couriers to score), `429`.

## Notes

- `delivery-times` ranks by **speed only**; `efficiency-index` also weighs
  reliability and consistency — prefer it when the goal is picking which
  courier to actually use, not just the fastest one on paper.
- Both are network-wide benchmarks, not shipment-specific — the numbers aren't
  driven by your own shipment volume on that lane alone.
- Live reference: <https://api.qapla.dev/v2/>.
