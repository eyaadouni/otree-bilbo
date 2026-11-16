"""Contrôle qualité et premiers résultats à partir de l'export « irrigation » d'oTree.

Usage : python analysis/analyse.py chemin/vers/irrigation_custom.csv
Produit : un rapport dans le terminal et analysis/contributions.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ENDOWMENT = 20
FAST_SECONDS = 1.5  # une décision plus rapide est suspecte (clic sans lire)


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Signale les lignes à vérifier avant l'analyse."""
    flags = pd.DataFrame(index=df.index)
    flags["hors_bornes"] = ~df["contribution"].between(0, ENDOWMENT)
    flags["trop_rapide"] = df["decision_seconds"] < FAST_SECONDS
    flags["temps_manquant"] = df["decision_seconds"].isna()
    print(f"{len(df)} décisions, {df['participant'].nunique()} participants, {df['session'].nunique()} sessions")
    for col in flags:
        print(f"  {col:15s} {int(flags[col].sum())}")
    return flags


def main(path: str) -> None:
    df = pd.read_csv(path)
    quality_report(df)

    table = df.pivot_table(index="round", columns="condition", values="contribution", aggfunc="mean")
    print("\nContribution moyenne par tour (sur 20) :")
    print(table.round(2))

    fig, ax = plt.subplots(figsize=(6, 3.5))
    for cond, color in [("base", "#2a78d6"), ("norme", "#eb6834")]:
        if cond in table:
            ax.plot(table.index, table[cond], marker="o", lw=2, color=color, label=cond)
    ax.set_xlabel("Tour")
    ax.set_ylabel("Contribution moyenne")
    ax.set_ylim(0, ENDOWMENT)
    ax.set_xticks(table.index)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    out = Path(__file__).with_name("contributions.png")
    fig.savefig(out, dpi=150)
    print(f"\nGraphique : {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "irrigation_custom.csv")
