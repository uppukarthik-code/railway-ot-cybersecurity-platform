import { useEffect, useState } from "react";

import CytoscapeComponent from "react-cytoscapejs";

import cytoscape from "cytoscape";

import elk from "cytoscape-elk";

import topology from "./data/topology.json";

cytoscape.use(elk);


// ======================================================
// PURDUE COLORS
// ======================================================

const PURDUE_COLORS = {

  "L5 Enterprise": "#d9e2f3",

  "L4 Business": "#cfe2f3",

  "L3.5 Security": "#ffe599",

  "L3 Operations": "#bdd7ee",

  "L2 Telecom": "#a2c4c9",

  "L2 Station Control": "#9fc5e8",

  "L2 Interlocking": "#f4cccc",

  "L1 Interlocking": "#d9ead3",

  "L0 Field": "#b6d7a8",

  "Onboard": "#d9b3ff",
};


// ======================================================
// NODE COLOR
// ======================================================

function getNodeColor(node) {

  const criticality =
    String(
      node.criticality || ""
    ).toUpperCase();

  if (
    criticality.includes("SIL4")
  ) {

    return "#ff9999";
  }

  if (
    criticality.includes("SIL3")
  ) {

    return "#ffe599";
  }

  if (
    node.functional_domain ===
    "Cybersecurity"
  ) {

    return "#ffe599";
  }

  return (
    node.zone_color ||
    PURDUE_COLORS[
      node.purdue_level
    ] ||
    "#cccccc"
  );
}


// ======================================================
// BUILD ELEMENTS
// ======================================================

function buildElements(topology) {

  const elements = [];

  const purdueLevels =
    new Set();

  // =====================================================
  // CREATE PURDUE COMPOUND NODES
  // =====================================================

  topology.nodes.forEach(
    (node) => {

      const purdue =
        node.purdue_level ||
        "Unknown";

      purdueLevels.add(
        purdue
      );
    }
  );

  Array.from(
    purdueLevels
  ).forEach((level) => {

    elements.push({

      data: {

        id:
          `group_${level}`,

        label: level,

        isGroup: true,
      }
    });
  });

  // =====================================================
  // NODES
  // =====================================================

  topology.nodes.forEach(
    (node) => {

      elements.push({

        data: {

          id: node.id,

          parent:
            `group_${node.purdue_level}`,

          label:
            `${node.label}\n` +
            `[${node.type}]\n` +
            `${node.purdue_level || ""}\n` +
            `${node.criticality || ""}`,

          zone:
            node.zone,

          purdue:
            node.purdue_level,

          criticality:
            node.criticality,

          trusted:
            node.trusted_zone,

          safety:
            node.safety_critical,

          color:
            getNodeColor(node),
        }
      });
    }
  );

  // =====================================================
  // EDGES
  // =====================================================

  topology.connections.forEach(
    (conn, index) => {

      elements.push({

        data: {

          id:
            conn.id ||
            `e_${index}`,

          source:
            conn.source,

          target:
            conn.target,

          label:
            conn.protocol || "",

          encrypted:
            conn.encrypted,

          safety:
            conn.safety_related,

          crossZone:
            conn.cross_zone,
        }
      });
    }
  );

  return elements;
}


// ======================================================
// APP
// ======================================================

export default function App() {

  const [elements, setElements] =
    useState([]);

  const [selectedNode,
    setSelectedNode] =
    useState(null);


  // ====================================================
  // LOAD
  // ====================================================

  useEffect(() => {

    const els =
      buildElements(
        topology
      );

    setElements(els);

  }, []);


  // ====================================================
  // CY EVENTS
  // ====================================================

  function handleCy(cy) {

    cy.on(
      "tap",
      "node",
      (evt) => {

        const node =
          evt.target;

        const data =
          node.data();

        if (
          data.isGroup
        ) {
          return;
        }

        setSelectedNode(
          data
        );
      }
    );
  }


  return (

    <div
      style={{

        width: "100vw",

        height: "100vh",

        display: "flex",

        background:
          "#1e1e1e",
      }}
    >

      {/* ========================================= */}
      {/* GRAPH */}
      {/* ========================================= */}

      <div
        style={{

          flex: 1,

          height: "100%",
        }}
      >

        <CytoscapeComponent

          cy={handleCy}

          elements={elements}

          style={{

            width: "100%",

            height: "100%",
          }}

          layout={{

            name: "elk",

            fit: true,

            padding: 50,

            animate: true,

            elk: {

              algorithm:
                "layered",

              direction:
                "DOWN",

              spacing:
                80,

              edgeRouting:
                "ORTHOGONAL",
            }
          }}

          stylesheet={[

            // ======================================
            // GROUPS
            // ======================================

            {
              selector:
                ":parent",

              style: {

                label:
                  "data(label)",

                "text-valign":
                  "top",

                "text-halign":
                  "center",

                "font-size":
                  22,

                color:
                  "#ffffff",

                "background-opacity":
                  0.08,

                "border-width":
                  3,

                "border-color":
                  "#666",

                padding:
                  "30px",
              }
            },

            // ======================================
            // NODES
            // ======================================

            {
              selector:
                "node",

              style: {

                label:
                  "data(label)",

                "text-wrap":
                  "wrap",

                "text-max-width":
                  180,

                "text-valign":
                  "center",

                "text-halign":
                  "center",

                "background-color":
                  "data(color)",

                width: 170,

                height: 100,

                shape:
                  "roundrectangle",

                color:
                  "#000",

                "font-size":
                  10,

                "border-width":
                  3,

                "border-color":
                  "#333",

                "overlay-padding":
                  6,

                "z-index":
                  10,
              }
            },

            // ======================================
            // UNTRUSTED
            // ======================================

            {
              selector:
                'node[trusted = false]',

              style: {

                "border-color":
                  "#ff0000",
              }
            },

            // ======================================
            // SAFETY CRITICAL
            // ======================================

            {
              selector:
                'node[safety = true]',

              style: {

                "border-width":
                  5,
              }
            },

            // ======================================
            // EDGES
            // ======================================

            {
              selector:
                "edge",

              style: {

                label:
                  "data(label)",

                width: 2,

                color:
                  "#ffffff",

                "font-size":
                  8,

                "curve-style":
                  "taxi",

                "target-arrow-shape":
                  "triangle",

                "line-color":
                  "#888",

                "target-arrow-color":
                  "#888",

                "taxi-direction":
                  "downward",

                "taxi-turn":
                  40,
              }
            },

            // ======================================
            // ENCRYPTED
            // ======================================

            {
              selector:
                'edge[encrypted = true]',

              style: {

                "line-color":
                  "#28a745",

                "target-arrow-color":
                  "#28a745",
              }
            },

            // ======================================
            // UNENCRYPTED
            // ======================================

            {
              selector:
                'edge[encrypted = false]',

              style: {

                "line-color":
                  "#ff4444",

                "target-arrow-color":
                  "#ff4444",

                width: 4,
              }
            },

            // ======================================
            // SAFETY CONDUITS
            // ======================================

            {
              selector:
                'edge[safety = true]',

              style: {

                width: 5,
              }
            },

            // ======================================
            // CROSS ZONE
            // ======================================

            {
              selector:
                'edge[crossZone = true]',

              style: {

                "line-style":
                  "dashed",
              }
            }
          ]}
        />

      </div>


      {/* ========================================= */}
      {/* INSPECTOR PANEL */}
      {/* ========================================= */}

      <div
        style={{

          width: "320px",

          background:
            "#252526",

          color:
            "#ffffff",

          padding: "16px",

          overflowY:
            "auto",

          borderLeft:
            "2px solid #333",
        }}
      >

        <h2>
          Asset Inspector
        </h2>

        {!selectedNode && (

          <div>
            Click a node
          </div>
        )}

        {selectedNode && (

          <div>

            <h3>
              {selectedNode.label}
            </h3>

            <hr />

            <p>
              <b>Zone:</b><br />
              {selectedNode.zone}
            </p>

            <p>
              <b>Purdue:</b><br />
              {selectedNode.purdue}
            </p>

            <p>
              <b>Criticality:</b><br />
              {selectedNode.criticality}
            </p>

            <p>
              <b>Trusted:</b><br />
              {
                selectedNode.trusted
                  ? "Yes"
                  : "No"
              }
            </p>

            <p>
              <b>Safety Critical:</b><br />
              {
                selectedNode.safety
                  ? "Yes"
                  : "No"
              }
            </p>

          </div>
        )}

      </div>

    </div>
  );
}