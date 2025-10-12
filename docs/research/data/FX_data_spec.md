# FX Market Data Ingestion Specification

## 1. Candidate Liquidity Venues and Brokers

| Venue/Broker | Access Model & Licensing | Typical Feed Characteristics | Notes |
| --- | --- | --- | --- |
| **LMAX Exchange** | Requires institutional account; FCA regulated MTF. API access via FIX for trading, proprietary market data agreements. | Depth up to 20 levels per side, millisecond timestamp precision, 24/5 coverage with weekend maintenance gap. | Known for low-latency matching in LD4/NY4. Raw market data fees apply; redistribution restrictions. |
| **Currenex** | Prime-of-prime or bank-sponsored access; licensing through State Street. FIX & API agreements required. | Depth usually 10+ levels per side depending on LPs, millisecond timestamps, occasional LP-specific pauses around roll events. | Supports multiple LP pools (ESP, disclosed, anonymous). Data entitlements tied to LP relationships. |
| **EBS Direct/Market** | Requires bilateral agreement with CME Group; must satisfy capital and regulatory checks. | Up to 10 levels depth, microsecond timestamps on EBS Live Ultra, localized outages during maintenance. | Split between EBS Market (central limit order book) and EBS Direct (streaming). Regional matching engines (NY, London, Tokyo). |
| **Refinitiv FXall** | Subscription via Refinitiv, with KYC and regulatory approval. Data redistribution tightly controlled. | Quote streams per LP, usually top-of-book with optional depth snapshots; millisecond timestamps, weekend closure. | Primarily RFQ/ESP; depth limited to quoted tiers. |
| **Integral OCX** | Requires prime broker or direct relationship; contractual licensing with Integral. | Multi-level depth (5-10 levels) with millisecond timestamps; supports disclosed and anonymous pools. | Provides consolidated liquidity hubs (NY4, LD4, TY3). |
| **Cboe FX** | Institutional onboarding with credit intermediary; FIX/ITCH market data licensing. | Depth up to 10 levels, sub-millisecond timestamps, rolling maintenance windows. | Offers both firm and non-firm liquidity flags. |
| **Hotspot/Cboe FX Central** | Similar onboarding to Cboe FX; additional fees for Central limit order book access. | Central order book depth (10 levels) with microsecond timestamps; weekend downtime. | Central book emphasizes firm liquidity; data subject to redistribution limits. |
| **FastMatch (Euronext FX)** | Requires onboarding via Euronext; regulatory approvals and FIX data agreements. | 10 levels depth with microsecond timestamp precision; daily maintenance window. | Matching centers NY4, LD4, TY3. |

### Licensing and Compliance Considerations
- **Regulatory Oversight:** Most venues operate under FCA, NFA, or equivalent oversight. Entities must ensure local regulatory authorization for market data usage and trading.
- **Redistribution Restrictions:** Raw data redistribution often prohibited without additional licensing. Internal research typically allowed under non-display agreements.
- **Data Storage Obligations:** Some venues mandate secure storage, audit trails, and prompt deletion when agreements terminate.
- **Connectivity:** Co-location or cross-connect contracts may be necessary for low-latency feeds.

### Expected Feed Characteristics Summary
- **Depth Levels:** Ranges from top-of-book only (RFQ style) up to ~20 levels per side on central limit order books.
- **Timestamp Precision:** Millisecond precision is standard; microsecond available on premium feeds (EBS Live Ultra, Cboe FX).
- **Coverage Gaps:** Regular weekend downtime (NY close to Asian open), daily maintenance windows, and occasional venue-specific pauses during roll or system upgrades.

## 2. Ingestion Architecture

### Data Acquisition & Transport
- **Connectivity:** Use dedicated VPN or cross-connect to venue gateways; redundant primary/secondary connections for resiliency.
- **Protocol Handling:** Support FIX and proprietary binary feeds via modular adapters. Implement sequence tracking and gap request mechanisms (e.g., FIX SequenceReset, TCP recovery).
- **Ingestion Framework:** Real-time ingestion microservice written in TypeScript/Node.js or Rust with pluggable parsers. Deploy within Kubernetes for horizontal scaling.

### Storage Format
- **Raw Capture:** Append-only parquet files partitioned by venue/date/hour stored in object storage (e.g., S3-compatible). Include schema with `timestamp`, `instrument`, `side`, `level`, `price`, `size`, `sequence_id`, `venue_metadata`.
- **Normalized Book:** Maintain columnar storage (Parquet/Iceberg) for consolidated order book snapshots and trades with derived fields (mid, spread, imbalance).
- **Metadata Catalog:** Use Hive/Glue-compatible metastore to enable analytical queries and retention policies.

### Latency Expectations
- **Ingestion-to-Storage:** <250 ms for raw capture to hit durable storage in normal operations.
- **Normalization Pipeline:** <1 s end-to-end for enriched snapshots; nightly backfill jobs allowed for non-real-time analytics.
- **Replay & Analytics:** Query latency <5 s for recent data; offline batch processing via Spark/Trino.

### Replay Tooling
- **Stream Replayer:** Implement Kafka-based topic per venue with event time ordering enabling deterministic replays. Support speed-up/slowdown factors and scenario-based filtering (instrument, time window).
- **Backtest Integration:** Provide Python SDK to stream historical book updates into simulation engines; include event checkpointing.
- **Failure Recovery:** Automated replays triggered on detected gaps, using last good sequence checkpoint.

### Quality Control (QC) Checks
- **Missing Data:**
  - Sequence number monitoring with alerting on gaps/duplicates.
  - Heartbeat tracking; escalate if no updates within expected heartbeat window (e.g., 1 s during active sessions).
- **Outliers:**
  - Z-score/median absolute deviation checks on spreads, price changes, and size jumps.
  - Cross-venue validation to flag deviations beyond configurable thresholds (e.g., >3x rolling median spread).
- **Timestamp Jitter:**
  - Monitor inter-arrival times; compute jitter metrics vs. venue-provided timestamps.
  - Detect clock skew by comparing system capture time vs. feed timestamps; trigger NTP resync alerts if skew >1 ms.
- **Data Completeness Audits:**
  - Daily reconciliation of expected vs. recorded files/rows.
  - Summaries per instrument-hour for update counts to highlight sparse periods.

## 3. Transaction-Cost Calibration Workflow

### Objectives
- Validate internal spread + slippage model using live broker quotes and executed tickets.

### Data Inputs
- **Quote Capture:** Store top-of-book and depth snapshots per venue with timestamps synchronized to trading engine.
- **Execution Records:** Collect trade confirmations (fills, partial fills) with execution venue, LP identifier, and latency metrics.
- **Reference Benchmarks:** Optional independent mid-price (e.g., EBS, Refinitiv) for fair-value comparison.

### Calibration Steps
1. **Session Definition:** Segment trading sessions by strategy, instrument, and market regime (e.g., Tokyo, London, New York).
2. **Sample Selection:**
   - Random stratified sampling of quote windows around executed trades (e.g., ±500 ms) to capture prevailing spreads.
   - Include non-trading intervals to evaluate opportunity cost and streaming spread changes.
3. **Model Inputs Computation:**
   - Compute realized spread (mid-price vs. execution) and slippage (expected vs. realized price) per trade.
   - Derive liquidity metrics (depth at quote, quote update frequency).
4. **Calibration:**
   - Fit parameters of spread+slippage model (e.g., linear/quadratic impact vs. trade size) per session.
   - Use cross-validation across sessions; ensure model generalizes to unseen days.
5. **Validation:**
   - Compare model-predicted costs against out-of-sample executions; target error bounds (e.g., <10% MAPE).
   - Cross-venue sanity checks using aggregated quotes when multiple brokers available.
6. **Feedback Loop:**
   - Update routing logic or strategy parameters based on calibrated cost curves.
   - Schedule monthly recalibration or triggered recalibration when QC alerts show structural changes in spreads/slippage.

### Tooling & Governance
- **Analytics Stack:** Use Python notebooks with Pandas/PySpark for analysis; store results in version-controlled reports (MLflow/Weights & Biases).
- **Audit Trail:** Maintain reproducible datasets and code for each calibration batch; log parameter changes and approvals.
- **Integration:** Expose calibrated cost curves via internal API consumed by risk and strategy modules.

