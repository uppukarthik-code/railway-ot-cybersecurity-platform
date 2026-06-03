Railway OT Cybersecurity Platform



Mission



This repository implements a standards-based railway OT cybersecurity architecture and validation framework.



The objective is to model, validate, and assess railway signalling systems against:



1\. EN 50126

2\. EN 50129

3\. EN 50159

4\. IEC 62443

5\. TS 50701

6\. Kavach Architecture



The system shall distinguish between:



\* Real security findings

\* Real safety findings

\* Ontology defects

\* Modelling defects

\* Validator defects



The tool shall never suppress genuine security or safety findings.



⸻



Architecture Authority



ontology.py



Semantic authority.



Responsible for:



\* Asset types

\* Protocol definitions

\* Conduit classes

\* Purdue levels

\* Zones

\* Security profiles



Never duplicate ontology logic elsewhere.



⸻



railway\_rules.py



Governance authority.



Responsible for:



\* IEC 62443 policy

\* EN 50159 policy

\* Trust boundaries

\* Flow rules

\* Mandatory links

\* Safety classifications



Never duplicate governance logic elsewhere.



⸻



validator.py



Enforcement authority.



Responsible for:



\* Validation

\* Findings

\* Compliance assessment



Never implement policy decisions inside validators.



Validators enforce rules.

They do not create rules.



⸻



Standards Hierarchy



When standards conflict, apply the following precedence:



1\. EN 50126

2\. EN 50129

3\. EN 50159

4\. IEC 62443

5\. TS 50701

6\. Kavach Architecture



⸻



Mandatory Review Process



Before any code change:



1\. Identify root cause

2\. Trace source of truth

3\. Verify no ontology duplication

4\. Verify no governance duplication

5\. Verify no validator duplication

6\. Run validators

7\. Capture before state

8\. Implement change

9\. Capture after state

10\. Produce engineering report



⸻



Findings Classification



Classify every finding as exactly one of:



A — Genuine Security Gap



Real cybersecurity weakness.



Examples:



\* Missing MFA

\* Missing authentication

\* Missing encryption

\* Missing monitoring



Never suppress automatically.



⸻



B — Genuine Safety Gap



Real EN 50159 / EN 50126 issue.



Examples:



\* Missing replay protection

\* Missing latency monitoring

\* Missing safety controls



Never suppress automatically.



⸻



C — Ontology Defect



Semantic model is wrong.



Examples:



\* Incorrect protocol capability

\* Incorrect conduit classification

\* Missing protocol metadata



Fix automatically when supported by standards.



⸻



D — Modelling Defect



Topology or architecture representation error.



Examples:



\* Wrong protocol assignment

\* Missing governance flow

\* Missing architecture relationship



Fix automatically when supported by standards.



⸻



E — Validator Defect



Validation logic incorrect.



Examples:



\* Wrong field names

\* Wrong capability checks

\* False positives

\* False negatives



Fix automatically.



⸻



Engineering Rules



Never:



\* Remove security requirements

\* Relax EN 50159 protections

\* Relax IEC 62443 requirements

\* Downgrade SIL classifications

\* Convert safety flows into non-safety flows

\* Add undocumented exemptions

\* Hide genuine findings



Always:



\* Preserve SIL4 boundaries

\* Preserve trust boundaries

\* Preserve IEC 62443 zoning

\* Preserve conduit profiles

\* Preserve safety classifications

\* Preserve governance authority

\* Preserve ontology authority



⸻



Review Findings Command



When asked:



Review findings



Perform:



1\. Root cause analysis

2\. Standards mapping

3\. Classification



A = Genuine Security Gap



B = Genuine Safety Gap



C = Ontology Defect



D = Modelling Defect



E = Validator Defect



For every finding provide:



\* Root cause

\* Applicable standard

\* Risk level

\* Recommended fix

\* Whether fix should be applied



Output:



\* Findings grouped by A/B/C/D/E

\* Fix recommendations

\* Standards rationale

\* Risk if ignored



Never suppress A or B findings.



Target state:



\* A findings = engineering backlog

\* B findings = safety backlog

\* C findings = 0

\* D findings = 0

\* E findings = 0

