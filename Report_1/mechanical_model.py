from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def make_figure(output_dir: Path = Path(".")) -> None:
    steel_work = (26.0, 379.0)
    gumfoot_work = (231.0, 281.0)
    gumfoot_se = (10.0, 22.0)
    elastic_modulus_mpa = 70_000.0
    flow_stress_mpa = 105.0
    band_spacing_nm = 8_000.0
    recorded_strain_limit = 0.01

    elastic_strain = flow_stress_mpa / elastic_modulus_mpa
    opening_limit_nm = band_spacing_nm * (
        recorded_strain_limit - elastic_strain
    )

    def nacre_work(opening_nm):
        """Estimated tensile work per unit volume in MJ/m^3."""
        elastic_work = flow_stress_mpa**2 / (2.0 * elastic_modulus_mpa)
        subsequent_work = (
            flow_stress_mpa
            * np.asarray(opening_nm)
            / band_spacing_nm
        )
        return elastic_work + subsequent_work

    nacre_at_limit = float(nacre_work(opening_limit_nm))

    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 10.5,
        "figure.dpi": 150,
        "savefig.dpi": 300,
    })

    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(14, 5.7),
        gridspec_kw={"width_ratios": [1.4, 1]},
        constrained_layout=True,
    )

    # Panel A: reported values
    xs = np.array([0.0, 1.0, 2.7, 3.7, 5.5])
    values = [*steel_work, *gumfoot_work, nacre_at_limit]
    colors = [
        "#34699c",
        "#34699c",
        "#bd6a35",
        "#bd6a35",
        "#177e79",
    ]

    for index, (x, value, color) in enumerate(
        zip(xs, values, colors)
    ):
        if index == 4:
            style = {
                "hatch": "///",
                "fill": False,
                "linewidth": 1.7,
            }
        else:
            style = {}

        ax_a.bar(
            x,
            value,
            width=0.68,
            color=color,
            edgecolor=color,
            zorder=3,
            **style,
        )

        if index in (2, 3):
            ax_a.errorbar(
                x,
                value,
                yerr=gumfoot_se[index - 2],
                fmt="none",
                ecolor="#71401e",
                capsize=3,
                zorder=5,
            )

        label = f"{value:.2f}" if index == 4 else f"{value:.0f}"
        ax_a.annotate(
            label,
            (x, value),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax_a.set_yscale("log")
    ax_a.set_ylim(0.5, 1500)
    ax_a.set_xlim(-0.55, 6.05)
    ax_a.set_xticks(xs)
    ax_a.set_xticklabels([
        "304 steel\nNG",
        "304 steel\nbimodal",
        "Gumfoot silk\ndry",
        "Gumfoot silk\ngluey",
        "Nacre\nmodel to 1%",
    ])

    ax_a.set_ylabel(
        "Tensile work per unit volume, $W$ (MJ m$^{-3}$)"
    )
    ax_a.set_title(
        "A  |  Work to rupture (steel/silk); nacre to 1% strain",
        pad=18,
    )

    ax_a.text(
        0.98,
        0.96,
        "Steel and gumfoot silk: published curve integrals to rupture\n"
        "Nacre: simplified estimate to ~1% (strain-gauge limit)\n"
        "Gumfoot error bars: mean ± SE",
        transform=ax_a.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        bbox={
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.85,
        },
    )

    steel_ratio = steel_work[1] / steel_work[0]
    silk_increase = 100 * (
        gumfoot_work[1] / gumfoot_work[0] - 1
    )

    ax_a.annotate(
        f"{steel_ratio:.1f}×",
        xy=(0.5, 610),
        color=colors[0],
        ha="center",
        fontsize=11,
    )
    ax_a.annotate(
        f"+{silk_increase:.1f}%",
        xy=(3.2, 465),
        color=colors[2],
        ha="center",
        fontsize=11,
    )
    ax_a.grid(axis="y", which="both", alpha=0.18, zorder=0)

    # Panel B: simplified nacre calculation
    u = np.linspace(0.0, opening_limit_nm, 200)

    ax_b.plot(
        u,
        nacre_work(u),
        color="#177e79",
        lw=2.6,
    )
    ax_b.plot(
        [0, opening_limit_nm],
        [nacre_work(0), nacre_at_limit],
        "s",
        ms=7,
        markerfacecolor="white",
        markeredgecolor="#177e79",
        mew=1.5,
    )
    ax_b.axvline(
        opening_limit_nm,
        color="#177e79",
        ls=":",
        lw=1.4,
    )

    ax_b.annotate(
        "~1% total strain\nstrain gauge debonded; no rupture",
        xy=(opening_limit_nm, nacre_at_limit),
        xytext=(35, 0.78),
        arrowprops={
            "arrowstyle": "->",
            "color": "#177e79",
        },
        ha="center",
        fontsize=9.5,
    )

    ax_b.text(
        0.04,
        0.96,
        "$W(u)\\approx\\sigma_s^2/(2E)+\\sigma_s u/S$\n"
        "$E=70$ GPa, $\\sigma_s=105$ MPa, $S=8$ $\\mu$m",
        transform=ax_b.transAxes,
        va="top",
        fontsize=10,
    )

    ax_b.set_xlim(0, 74)
    ax_b.set_ylim(0, 1.1)
    ax_b.set_xlabel(
        "Inferred opening per dilatation band, $u$ (nm)"
    )
    ax_b.set_ylabel(
        "Estimated tensile work per unit volume, "
        "$W$ (MJ m$^{-3}$)"
    )
    ax_b.set_title(
        "B  |  Nacre work versus inferred band opening",
        pad=18,
    )
    ax_b.grid(alpha=0.2)

    output_dir.mkdir(parents=True, exist_ok=True)

    for suffix in ("png", "pdf"):
        fig.savefig(
            output_dir / f"tensile_work.{suffix}",
            bbox_inches="tight",
        )

    plt.close(fig)

    print(f"Steel ratio: {steel_ratio:.2f}")
    print(f"Gumfoot silk change: +{silk_increase:.1f}%")
    print(f"Nacre elastic strain: {elastic_strain:.4f}")
    print(f"Inferred band opening: {opening_limit_nm:.1f} nm")
    print(
        f"Nacre estimated work to 1%: "
        f"{nacre_at_limit:.5f} MJ/m^3"
    )

if __name__ == "__main__":
    make_figure()