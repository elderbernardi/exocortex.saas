---
# OKF Canonical (mandatory)
type: memory
title: Deprecated without reason test fixture
description: "This file has deprecated true but no deprecated_reason"
tags: [test, fixture, invalid]
timestamp: 2026-05-01

# Acervo Extension (lifecycle)
class: volátil
created_at: 2026-05-01T09:00:00Z

# Deprecation (conditional) — missing deprecated_reason
deprecated: true
deprecated_at: 2026-06-19T10:30:00Z
---

This fixture has `deprecated: true` with `deprecated_at` but is missing the
required `deprecated_reason` field, to test V-052.
