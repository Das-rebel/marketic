# Marketic Brief Schema — v1.0

The contract between Marketic (strategy brain) and any execution agent.
`generate_brief` produces this JSON; agents consume it **without calling back**.

**Compatibility rule:** within major version `1.x`, fields are additive-only —
existing keys never change type or meaning. Breaking changes bump to `2.0`.

---

## Top-level structure

```jsonc
{
  "brief_version": "1.0",              // semver of THIS schema
  "generated_at": "ISO-8601 UTC",
  "campaign": { ... },
  "brand_kit": { ... },
  "product": { ... },
  "budget": { ... },
  "posting_windows_utc": { ... },
  "execution_contract": { ... }
}
```

## Field reference

### `campaign`
| Field | Type | Notes |
|---|---|---|
| `name` | string | Campaign identifier |
| `objective` | string | e.g. `conversion`, `awareness` |
| `duration_weeks` | int | Planning horizon |

### `brand_kit`
Resolved brand tokens as substitution pairs, plus voice constraints.

| Field | Type | Notes |
|---|---|---|
| `{{brand.primary}}` … `{{brand.tagline}}` | string | 8 token keys: primary, background, accent, secondary, font, handle, name, tagline. Agents substitute these placeholders in all creative output |
| `voice_notes` | string | Tone guidance, may be empty |
| `banned_words` | string[] | Hard exclusions — agent MUST NOT emit these |

### `product`
| Field | Type |
|---|---|
| `name` | string |
| `description` | string |
| `audience` | string |
| `key_benefits` | string[] |

### `budget`
Margin-aware allocation (`roas × contribution_margin` optimized).

| Field | Type | Notes |
|---|---|---|
| `total` | number | Total spend |
| `recommended_split` | `{channel: string, amount: number}[]` | Sum equals `total` |

### `posting_windows_utc`
Map of channel → ISO datetime array (optimal send times). Optional key — absent if scheduling data unavailable; agents then choose their own times.

### `execution_contract`
Behavioral rules the agent agrees to by consuming the brief.

| Field | Type | Meaning |
|---|---|---|
| `renders_from_tokens_only` | bool | Always `true`: no hardcoded brand values allowed in output |
| `expected_outputs` | string[] | Deliverables list (e.g. static post, caption set) |
| `must_not` | string[] | Prohibited actions |

---

## Versioning policy

| Change | Version bump |
|---|---|
| New optional field added | `1.x` patch/minor |
| Field type change, field removal, semantic change | `2.0` |

Consumers SHOULD check `brief_version` and reject unknown majors.

## Lock test

`tests/test_brief_schema.py` asserts this exact key-shape on a generated brief —
any schema drift fails CI before it breaks a downstream agent.
