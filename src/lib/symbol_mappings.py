"""Canonical symbol tables for literal math-mode Unicode conversion.

The toolkit keeps the mapping in one direction and derives the inverse mapping
so both commands stay synchronized.
"""

from __future__ import annotations


LATEX2UNICODE_MAP: dict[str, str] = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ϵ",
    "zeta": "ζ",
    "eta": "η",
    "theta": "θ",
    "iota": "ι",
    "kappa": "κ",
    "lambda": "λ",
    "mu": "μ",
    "nu": "ν",
    "xi": "ξ",
    "pi": "π",
    "rho": "ρ",
    "sigma": "σ",
    "tau": "τ",
    "upsilon": "υ",
    "phi": "ϕ",
    "chi": "χ",
    "psi": "ψ",
    "omega": "ω",
    "Gamma": "Γ",
    "Delta": "Δ",
    "Theta": "Θ",
    "Lambda": "Λ",
    "Xi": "Ξ",
    "Pi": "Π",
    "Sigma": "Σ",
    "Upsilon": "Υ",
    "Phi": "Φ",
    "Psi": "Ψ",
    "Omega": "Ω",
    "int": "∫",
    "sum": "∑",
    "prod": "∏",
    "partial": "∂",
    "nabla": "∇",
    "infty": "∞",
    "leq": "≤",
    "geq": "≥",
    "neq": "≠",
    "approx": "≈",
    "in": "∈",
    "notin": "∉",
    "subset": "⊂",
    "supset": "⊃",
}

UNICODE2LATEX_MAP: dict[str, str] = {value: key for key, value in LATEX2UNICODE_MAP.items()}
