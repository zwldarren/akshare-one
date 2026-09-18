# Context

Glossary for akshare-one. Terms only — no implementation, no decisions.

## Data

**Domain** — a category of Chinese market data the package exposes: historical,
realtime, info, news, financial, insider, futures, options.

**Source** — the upstream service a caller selects by name to serve a domain:
`eastmoney`, `eastmoney_direct`, `sina`, `xueqiu`.

**Provider** — the adapter that implements a domain's interface for one source.

**Capability** — which of a domain's provider interfaces a provider implements.
Only the futures domain has more than one: historical and realtime.

**Schema** — the columns, their order, and the types a domain's DataFrame
promises, independent of which source produced it.

**Indicator** — a pure calculation over a caller-supplied OHLCV frame. Not a
domain: no source, no network, no schema of its own.

## Structure

**Registry** — the single mapping from (domain, capability, source) to a
provider, populated by providers declaring themselves.

**Public surface** — `akshare_one` and `akshare_one.indicators`. Everything
under `akshare_one.modules` is internal to the package, including the registry
and the provider base classes.
