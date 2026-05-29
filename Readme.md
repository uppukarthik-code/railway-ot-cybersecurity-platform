Railway OT Cybersecurity Topology Generator

A Python-based Railway OT Cybersecurity Architecture Generation and Validation Platform that generates structured railway signalling and telecom architectures from natural-language descriptions and validates them against IEC 62443, EN 50126, EN 50129, EN 50159, Purdue Model, and Kavach cybersecurity and safety design principles.

The platform combines AI-assisted architecture generation with deterministic validation, producing deployment-ready topology models suitable for cybersecurity assessments, architecture reviews, threat modeling, and compliance verification.

⸻

Overview

The system transforms natural-language descriptions into structured Railway OT architectures and performs multi-layer validation against cybersecurity, safety, zoning, communication, and rendering rules.

Workflow

Natural Language Description
            │
            ▼
     AI Topology Generation
            │
            ▼
     Structured JSON Model
            │
            ▼
     Security Enrichment
            │
            ▼
     Validation Pipeline
            │
            ▼
     Compliance Report
            │
            ▼
     Graphviz / DrawIO Output

⸻

Key Features

Architecture Generation

* Natural-language-to-topology generation
* Railway signalling architecture modeling
* Kavach architecture generation
* Purdue Model classification
* IEC 62443 zone and conduit modeling
* Structured JSON topology generation

Railway Domain Support

Supports modeling of:

* Electronic Interlocking
* Object Controllers
* S-Kavach
* L-Kavach
* Axle Counter Systems
* Track Circuits
* Point Machines
* Signal Controllers
* Radio Gateways
* MPLS Networks
* Telecom Gateways
* Railway Radio Base Stations
* Engineering Workstations
* Operations Systems
* Security Infrastructure
* PKI Infrastructure
* Onboard ATP Equipment

Cybersecurity Validation

* IEC 62443 Zone Validation
* IEC 62443 Conduit Validation
* Trust Boundary Enforcement
* Security Monitoring Requirements
* Cross-Zone Flow Validation
* Engineering Access Validation
* Security Control Verification
* PKI Trust Chain Validation

Railway Safety Validation

* EN 50159 Communication Protection
* Open Transmission Validation
* Safety Flow Validation
* Vital System Isolation
* Safety Domain Separation
* Safety Communication Integrity Verification
* Replay Protection Verification
* Radio Safety Protection Validation

Rendering Support

* Graphviz generation
* DrawIO generation
* Purdue visualization
* Zone visualization
* Detached-domain rendering
* Rendering safety validation

⸻

Supported Standards

IEC 62443

Industrial Automation and Control System cybersecurity:

* Zones and Conduits
* Security Levels
* Defense-in-Depth
* Trust Boundaries
* Security Segmentation
* Security Monitoring

EN 50126

Railway RAMS lifecycle concepts:

* System decomposition
* Functional architecture support
* Safety-related system classification

EN 50129

Railway safety integrity concepts:

* SIL-aware asset modeling
* Safety-critical system identification
* Vital system segregation

EN 50159

Safety-related communication systems:

* Open transmission systems
* Integrity protection
* Replay protection
* Authentication controls
* Communication risk mitigation

Purdue Model

Industrial network hierarchy:

* Enterprise Layer
* Business Layer
* IDMZ Layer
* Security Layer
* Operations Layer
* Telecom Layer
* Interlocking Layer
* Field Layer
* Onboard Layer

Kavach

Indian Automatic Train Protection architecture:

* S-Kavach
* L-Kavach
* Radio Communications
* RFID Infrastructure
* Interlocking Interfaces
* Safety Communication Flows

⸻

Validation Pipeline

1. Asset Validation

Validates:

* Node integrity
* Asset type correctness
* Required attributes
* Safety metadata
* Graph consistency

Validator:

asset_validator.py

⸻

2. Zone Validation

Validates:

* Asset-to-zone consistency
* Zone assignment correctness
* Detached-domain zoning
* External hosting restrictions

Validator:

zone_validator.py

⸻

3. Purdue Validation

Validates:

* Purdue hierarchy compliance
* Zone-to-Purdue consistency
* Detached Purdue domains
* Purdue placement rules

Validator:

purdue_validator.py

⸻

4. Protocol Validation

Validates:

* Protocol compatibility
* Transport compatibility
* Media compatibility
* Bearer compatibility
* Communication stack consistency

Validator:

protocol_validator.py

⸻

5. Link Validation

Validates:

* Allowed flows
* Required flows
* Trust boundaries
* Firewall requirements
* Inspection requirements
* Conduit controls
* Open transmission protections
* Safety communications

Validator:

link_validator.py

⸻

6. Render Validation

Validates:

* Graph integrity
* Graphviz safety
* DrawIO safety
* Detached-domain rendering
* Render metadata correctness

Validator:

render_validator.py

⸻

Example Assets

Electronic Interlocking
Object Controller
S-Kavach
L-Kavach
Axle Counter Evaluator
Axle Counter Head
Track Circuit
Point Machine Controller
Signal Controller
Train Radio
Radio Gateway
Radio Base Station
MPLS Router
Telecom Gateway
Engineering Workstation
Operations Workstation
SIEM
SOC Server
Certificate Authority
VPN Gateway
Jump Host
Firewall
Data Diode

⸻

Example Zones

enterprise_it
business_systems
idmz
security_management
operations
maintenance
engineering
telecom_core
radio_access
interlocking
field
onboard
external_security

⸻

Example Purdue Levels

L5 Enterprise
L4 Business
L3.5 IDMZ
L3.5 Security
L3 Operations
L2 Telecom
L1 Telecom
L2 Interlocking
L1 Interlocking
L0 Field
Onboard

⸻

Project Structure

project/
│
├── ontology.py
├── aliases.py
│
├── asset_validator.py
├── zone_validator.py
├── purdue_validator.py
├── protocol_validator.py
├── link_validator.py
├── render_validator.py
│
├── railway_rules.py
├── security_enrichment.py
│
├── topology_generator.py
├── graphviz_renderer.py
├── drawio_renderer.py
│
├── examples/
│
└── outputs/

⸻

Typical Use Cases

Cybersecurity Architecture Review

Generate and validate:

* IEC 62443 architectures
* Railway OT security zones
* Trust boundaries
* Security conduits

Kavach Security Assessment

Evaluate:

* Communication paths
* Safety flows
* Radio interfaces
* Security controls

Purdue Modeling

Automatically generate:

* Purdue-aligned architectures
* Zone segmentation diagrams
* Trust-domain visualizations

Threat Modeling

Identify:

* Open transmission risks
* Trust boundary violations
* Missing security controls
* Unsafe safety communication paths

⸻

Output Artifacts

The platform can generate:

* Structured JSON topology
* Validation reports
* Compliance reports
* Graphviz diagrams
* DrawIO diagrams
* Purdue architecture views
* Zone/conduit views
* Security architecture views

⸻

Intended Audience

* Railway Signalling Engineers
* Cybersecurity Engineers
* IEC 62443 Practitioners
* EN 50159 Assessors
* RAMS Engineers
* Functional Safety Engineers
* Security Architects
* Kavach Design Teams
* Railway Operators
* Infrastructure Managers

⸻

Disclaimer

This tool assists with architecture generation and compliance validation but does not replace formal cybersecurity assessment, safety assurance, independent verification, or regulatory approval processes.

Final compliance decisions remain the responsibility of qualified engineering, cybersecurity, safety, and regulatory authorities.