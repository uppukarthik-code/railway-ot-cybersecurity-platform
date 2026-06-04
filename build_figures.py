# -*- coding: utf-8 -*-
"""Render the four required figures as PNGs for the reviewed manuscript."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

os.makedirs("figs", exist_ok=True)
NAVY = "#102A43"; STEEL = "#334E68"; TEAL = "#0B7285"; RED = "#B02A2A"
AMBER = "#B7791F"; GREY = "#627D98"; LIGHT = "#F0F4F8"

def box(ax, x, y, w, h, text, fc=LIGHT, ec=NAVY, tc=NAVY, fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=tc, weight=("bold" if bold else "normal"), wrap=True)

def arrow(ax, x1, y1, x2, y2, color=STEEL, style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=12, color=color, lw=lw, linestyle=ls))

def save(fig, name):
    fig.savefig("figs/%s.png" % name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------- Figure 1: Zone & conduit reference model ----------------
fig, ax = plt.subplots(figsize=(7.6, 5.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 11); ax.axis("off")
ax.set_title("Figure 1.  IEC 62443 zone-and-conduit reference model for railway signalling\n"
             "(EN 50159 transmission category annotated on each conduit)", fontsize=9.5, weight="bold")
zones = [
    (3.0, 9.7, 4.0, 0.9, "Enterprise  (L5)", "#E8EDF2"),
    (1.2, 8.4, 3.4, 0.9, "IDMZ  (L3.5)", "#DDE7EE"),
    (5.4, 8.4, 3.4, 0.9, "Security-Management / SOC  (L3.5)", "#DDE7EE"),
    (3.0, 7.1, 4.0, 0.9, "Operations: TMS / NMS / EWS  (L3)", "#D6E6E8"),
    (0.6, 5.6, 3.8, 0.9, "Telecom Core: MPLS  (L2)", "#D6E6E8"),
    (5.6, 5.6, 3.8, 0.9, "Radio Access: BTS / radio gw  (L1)", "#F3E2C7"),
    (2.6, 4.0, 4.8, 0.9, "Interlocking: EI / S-Kavach  (L2/L1)", "#F6D9D9"),
    (0.6, 2.4, 3.8, 0.9, "Field: track circuit / axle counter / RFID balise  (L0)", "#F6D9D9"),
    (5.6, 2.4, 3.8, 0.9, "Onboard: L-Kavach / DMI / BIU  (mobile)", "#F6D9D9"),
]
for x, y, w, h, t, c in zones:
    box(ax, x, y, w, h, t, fc=c, fs=8.2, bold=True)
conduits = [
    (5.0, 9.7, 4.4, 9.3, "C1", "Enterprise-IDMZ"),
    (3.0, 8.4, 5.0, 7.1, "C2", "IDMZ-Operations"),
    (5.0, 7.1, 5.0, 6.5, "Cat 1", "Ops-Interlocking"),
    (4.6, 6.0, 5.6, 6.0, "Cat 2", "Telecom-Radio"),
    (7.5, 5.6, 5.0, 4.9, "", "Radio-Interlocking(via gw)"),
    (4.8, 4.0, 2.5, 3.3, "Cat 1", "Interlocking-Field"),
    (7.5, 4.0, 7.5, 3.3, "Cat 3", "Kavach RF / Onboard"),
]
arrow(ax, 5.0, 9.7, 4.4, 9.3); ax.text(4.0, 9.55, "firewall/inspection", fontsize=6.6, color=GREY)
arrow(ax, 3.4, 8.4, 4.6, 7.55); ax.text(2.0, 7.95, "fw/insp", fontsize=6.6, color=GREY)
arrow(ax, 5.0, 7.1, 5.0, 6.5, color=RED); ax.text(5.1, 6.75, "Cat 1: fw,insp,integrity,auth", fontsize=6.6, color=RED)
arrow(ax, 4.4, 6.05, 5.6, 6.05, color=AMBER); ax.text(3.7, 6.2, "Cat 2", fontsize=6.8, color=AMBER)
arrow(ax, 4.6, 4.4, 3.2, 3.3, color=RED); ax.text(2.4, 3.95, "Cat 1", fontsize=6.8, color=RED)
arrow(ax, 7.5, 5.6, 7.5, 3.3, color=RED, ls=(0,(4,2))); ax.text(7.6, 4.5, "Cat 3: open RF\nintegrity+replay+auth\n+timeliness+RF-anomaly", fontsize=6.4, color=RED)
arrow(ax, 6.6, 4.45, 7.5, 4.45, color=TEAL); ax.text(6.4, 4.62, "Kavach assoc.", fontsize=6.4, color=TEAL)
ax.text(0.2, 0.9, "Cat 1 = closed trusted   Cat 2 = controlled   Cat 3 = open (cryptographic + timeliness defences mandatory)",
        fontsize=7.2, color=NAVY)
save(fig, "fig1_zones")

# ---------------- Figure 2: Three-echelon OT-SOC topology ----------------
fig, ax = plt.subplots(figsize=(7.6, 5.0)); ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
ax.set_title("Figure 2.  Three-echelon OT-SOC topology with passive collection and "
             "unidirectional log export", fontsize=9.5, weight="bold")
box(ax, 3.0, 8.6, 4.0, 1.0, "E3  National OT-SOC (RDSO)\narchitecture custody, ISAC, KPI", fc="#DDE7EE", fs=8, bold=True)
box(ax, 1.2, 6.4, 3.3, 1.0, "E2  Zonal OT-SOC\nSIEM, correlation, IR", fc="#D6E6E8", fs=8, bold=True)
box(ax, 5.5, 6.4, 3.3, 1.0, "E2  Zonal OT-SOC\nSIEM, correlation, IR", fc="#D6E6E8", fs=8, bold=True)
for x in (0.6, 3.4, 6.2):
    box(ax, x, 4.2, 2.6, 0.9, "E1  Station/Wayside\nTAP/SPAN + diode", fc="#EAF2EC", fs=7.4, bold=True)
box(ax, 2.0, 1.8, 6.0, 1.1, "Vital OT (passive TAP only):  EI / S-Kavach / object controllers / field / onboard",
    fc="#F6D9D9", fs=8, bold=True)
# diode arrows upward
for x in (1.9, 4.7, 7.5):
    arrow(ax, x, 2.9, x, 4.2, color=TEAL)
ax.text(8.1, 3.4, "data diode\n(logs UP only)", fontsize=6.8, color=TEAL)
arrow(ax, 1.9, 5.1, 2.8, 6.4, color=TEAL); arrow(ax, 4.7, 5.1, 3.0, 6.5, color=TEAL)
arrow(ax, 7.5, 5.1, 7.0, 6.4, color=TEAL)
arrow(ax, 2.8, 7.4, 4.6, 8.6, color=TEAL); arrow(ax, 7.0, 7.4, 5.4, 8.6, color=TEAL)
# OOB mgmt downward (dashed)
arrow(ax, 8.6, 8.6, 8.6, 3.0, color=GREY, ls=(0,(3,3)))
ax.text(8.7, 6.0, "OOB mgmt\n(scheduled,\nchange-controlled)", fontsize=6.4, color=GREY)
ax.text(0.2, 0.7, "Log flow strictly upward by data diode; no online downward path to the vital tier; "
        "TAP (not SPAN) on SIL-4 segments.", fontsize=7.0, color=NAVY)
save(fig, "fig2_echelons")

# ---------------- Figure 3: Kavach legitimate vs forbidden ----------------
fig, ax = plt.subplots(figsize=(7.6, 4.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
ax.set_title("Figure 3.  Kavach communication architecture: legitimate end-to-end safety association "
             "vs forbidden direct edge", fontsize=9.5, weight="bold")
box(ax, 0.4, 5.6, 2.4, 1.0, "S-Kavach\n(wayside, SIL-4)", fc="#F6D9D9", fs=8, bold=True)
box(ax, 0.4, 3.0, 2.4, 1.0, "Electronic\nInterlocking (SIL-4)", fc="#F6D9D9", fs=8, bold=True)
box(ax, 3.6, 4.3, 2.0, 1.0, "Radio gateway", fc="#F3E2C7", fs=8, bold=True)
box(ax, 6.1, 4.3, 1.8, 1.0, "BTS / radio\n(L1)", fc="#F3E2C7", fs=8, bold=True)
box(ax, 8.2, 1.4, 1.6, 1.0, "L-Kavach\n(onboard)", fc="#F6D9D9", fs=8, bold=True)
arrow(ax, 1.6, 5.6, 1.6, 4.0, color=RED); ax.text(1.7, 4.75, "Cat 1\nEI iface", fontsize=6.6, color=RED)
arrow(ax, 2.8, 6.0, 3.6, 5.0, color=AMBER); ax.text(2.7, 6.15, "backhaul (Cat 2)", fontsize=6.4, color=AMBER)
arrow(ax, 5.6, 4.8, 6.1, 4.8, color=AMBER)
arrow(ax, 7.0, 4.3, 8.6, 2.4, color=RED, ls=(0,(4,2))); ax.text(7.2, 3.2, "Cat 3 open RF", fontsize=6.6, color=RED)
# legitimate end-to-end association
arrow(ax, 2.0, 5.6, 8.2, 2.2, color=TEAL, ls=(0,(2,2)), lw=1.2)
ax.text(3.6, 3.0, "LEGITIMATE end-to-end Kavach safety association\n(EN 50159 open-transmission safety layer)",
        fontsize=6.8, color=TEAL)
# forbidden direct edge
arrow(ax, 2.8, 5.9, 6.1, 5.0, color=RED, lw=2.4)
ax.text(3.0, 6.6, "FORBIDDEN: S-Kavach -> BTS direct edge\n(bypasses radio gateway & rf-transition boundary)",
        fontsize=7.0, color=RED, weight="bold")
ax.plot([4.2, 4.6], [5.45, 5.65], color=RED, lw=2.4); ax.plot([4.6, 4.2], [5.45, 5.65], color=RED, lw=2.4)
save(fig, "fig3_kavach")

# ---------------- Figure 4: Four-gate IR flow ----------------
fig, ax = plt.subplots(figsize=(7.6, 4.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 9); ax.axis("off")
ax.set_title("Figure 4.  Four-gate, safety-first incident-response flow", fontsize=9.5, weight="bold")
box(ax, 3.2, 7.8, 3.6, 0.9, "Detection + enrichment (OT-SOC)", fc="#EAF2EC", fs=8.2, bold=True)
box(ax, 3.2, 6.3, 3.6, 0.9, "G1  Safety assessment\n(Functional-Safety engineer)", fc="#F6D9D9", fs=8, bold=True)
box(ax, 3.2, 4.8, 3.6, 0.9, "G2  Operational-impact\n(Divisional Control + SOC)", fc="#F3E2C7", fs=8, bold=True)
box(ax, 3.2, 3.3, 3.6, 0.9, "G3  Containment decision\n(SOC Lead + Ops Lead)", fc="#DDE7EE", fs=8, bold=True)
box(ax, 3.2, 1.8, 3.6, 0.9, "G4  Recovery authorisation\n(RDSO / Divisional safety)", fc="#D6E6E8", fs=8, bold=True)
for y in (7.8, 6.3, 4.8, 3.3):
    arrow(ax, 5.0, y, 5.0, y-0.6, color=STEEL)
box(ax, 7.4, 6.3, 2.4, 0.9, "Manual protective action\nunder safe-working rules", fc="#FBEED9", fs=7.4)
arrow(ax, 6.8, 6.75, 7.4, 6.75, color=GREY, ls=(0,(3,3)))
ax.text(0.2, 0.7, "No gate permits an action that interrupts a vital path or induces a wrong-side state; "
        "SOC advises, signalling operations acts.", fontsize=7.0, color=NAVY)
save(fig, "fig4_fourgate")

print("FIGURES:", os.listdir("figs"))
