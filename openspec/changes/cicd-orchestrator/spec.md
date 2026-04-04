# Delta for CI/CD Orchestration

## ADDED Requirements

### Requirement: Pipeline Orchestrator Role

Metanoia-QA SHALL operate as the central pipeline controller, not a passive participant. The system MUST evaluate code quality post-build and determine subsequent pipeline actions (merge, deploy, reject).

#### Scenario: Quality score above threshold triggers merge

- GIVEN a pull request has passed all CI checks and received a quality score
- WHEN the quality score exceeds 95%
- THEN the system SHALL instruct ReleaseAnalyst to merge the pull request automatically

#### Scenario: Quality score at or below threshold prevents merge

- GIVEN a pull request has passed all CI checks but has a quality score of 94% or lower
- WHEN the quality gate evaluates the score
- THEN the system SHALL NOT merge and SHALL report the failure

### Requirement: ReleaseAnalyst Agent Capabilities

The ReleaseAnalyst agent MUST have repository-level permissions including: read code, read PRs, merge PRs, and comment. The agent SHALL execute merge instructions from Metanoia-QA.

#### Scenario: ReleaseAnalyst merges PR on instruction

- GIVEN ReleaseAnalyst has valid repository tokens and quality gate approval
- WHEN Metanoia-QA sends a merge instruction with PR identifier
- THEN ReleaseAnalyst SHALL merge the specified pull request

### Requirement: Token Storage Security

All repository tokens MUST be stored encrypted at rest and retrieved securely at runtime. The system SHALL support token rotation without downtime.

#### Scenario: Token retrieval for merge operation

- GIVEN a merge request has been approved by the quality gate
- WHEN ReleaseAnalyst requires repository access
- THEN the system SHALL retrieve the decrypted token from secure storage

### Requirement: Agent-Driven Deployment

Deployment MUST be triggered as an agent action, not a webhook callback. The system SHALL support explicit environment targeting.

#### Scenario: Deployment triggered after successful merge

- GIVEN a pull request has been auto-merged
- WHEN ReleaseAnalyst receives the merge confirmation
- THEN ReleaseAnalyst SHALL trigger deployment to the specified target environment

### Requirement: Quality Gate Evaluation

The quality gate MUST evaluate code quality post-build and compare against the 95% threshold before any merge action is taken.

#### Scenario: Quality gate passes with 96% score

- GIVEN a build has completed and quality analysis finished
- WHEN the computed quality score is 96%
- THEN the quality gate SHALL emit an approval signal

#### Scenario: Quality gate fails with 94% score

- GIVEN a build has completed and quality analysis finished
- WHEN the computed quality score is 94%
- THEN the quality gate SHALL emit a rejection signal

### Requirement: Manual Override Capability

The system SHALL support a manual override flag that prevents auto-merge regardless of quality score.

#### Scenario: Auto-merge disabled via config flag

- GIVEN `auto_merge` is set to `false` in config
- WHEN a pull request would otherwise qualify for auto-merge
- THEN the system SHALL NOT merge and SHALL wait for manual intervention
