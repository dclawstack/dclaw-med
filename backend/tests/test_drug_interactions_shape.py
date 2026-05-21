"""Tests for /api/v1/med/drug/interactions response shape.

Role-gating for this endpoint is already covered in test_router_guards.py
(receptionist → 403, nurse → 200, anonymous → 401). This file asserts
the *response contract*: severity ∈ the canonical bands, recommendation
is surfaced, and the rollup fields agree with the per-row list.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


INTERACTIONS = "/api/v1/med/drug/interactions"
SEVERITIES = {"minor", "moderate", "major", "contraindicated"}


@pytest.mark.asyncio
async def test_known_pair_returns_severity_and_recommendation(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    """warfarin + aspirin is in the canonical interaction table —
    response must include severity and a recommendation."""
    res = await client.post(
        INTERACTIONS,
        headers=doctor_headers,
        json={"drugs": ["warfarin", "aspirin"]},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total_interactions"] == len(body["interactions_found"]) >= 1
    assert body["highest_severity"] in SEVERITIES

    hit = body["interactions_found"][0]
    assert hit["severity"] in SEVERITIES
    assert isinstance(hit["recommendation"], str) and hit["recommendation"]
    # The canonical pair should be the one returned, in either order.
    assert {hit["drug_a"].lower(), hit["drug_b"].lower()} == {"warfarin", "aspirin"}


@pytest.mark.parametrize(
    "drugs",
    [
        # Pairs declared NON-alphabetically in ``_RAW_INTERACTIONS``.
        # Regression for the bug where ``tuple(sorted(...))`` lookup
        # missed these entirely. Each pair is in the canonical table.
        ["warfarin", "aspirin"],
        ["warfarin", "ibuprofen"],
        ["simvastatin", "clarithromycin"],
        ["prednisone", "nsaid"],
        ["phenytoin", "fluconazole"],
        ["sertraline", "linezolid"],
    ],
)
@pytest.mark.asyncio
async def test_pairs_declared_non_alphabetically_still_match(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    drugs: list[str],
) -> None:
    res = await client.post(
        INTERACTIONS, headers=doctor_headers, json={"drugs": drugs}
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total_interactions"] >= 1, (
        f"Lookup missed {drugs} — key-sorting bug regressed."
    )


@pytest.mark.asyncio
async def test_unknown_pair_returns_empty_interactions(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    """Two drugs the service doesn't know about → empty result with
    total_interactions=0, not a 404 or 500."""
    res = await client.post(
        INTERACTIONS,
        headers=doctor_headers,
        json={"drugs": ["unicornium", "phantasmagorin"]},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["interactions_found"] == []
    assert body["total_interactions"] == 0
    assert body["highest_severity"] is None


@pytest.mark.asyncio
async def test_too_few_drugs_rejected(
    client: AsyncClient, doctor_headers: dict[str, str]
) -> None:
    """The request schema requires at least 2 drugs."""
    res = await client.post(
        INTERACTIONS, headers=doctor_headers, json={"drugs": ["aspirin"]}
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_anonymous_rejected(client: AsyncClient) -> None:
    res = await client.post(
        INTERACTIONS, json={"drugs": ["warfarin", "aspirin"]}
    )
    assert res.status_code == 401
