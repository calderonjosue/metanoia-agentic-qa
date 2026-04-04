# Delta for Infrastructure

## ADDED Requirements

### Requirement: InfrastructureAgent Provisioning

The system MUST provide an InfrastructureAgent capable of authoring and executing IaC code (Terraform HCL or Pulumi SDK) to provision ephemeral lab environments on AWS EC2.

### Requirement: IaC Provider Abstraction

The system SHALL provide a unified IaCProvider interface supporting both Terraform and Pulumi backends with provider-agnostic orchestration.

### Requirement: Ephemeral Lab Lifecycle

The system MUST implement a lifecycle manager supporting: provision → configure → test → destroy with automatic cleanup on timeout or failure.

### Requirement: Cost Management

The system SHALL implement budget controls including pre-execution cost estimation, hard caps, auto-destroy on overspend, and spend alerts.

### Requirement: StrategyManager Integration

The system MUST allow StrategyManager to trigger InfrastructureAgent when concurrency testing is requested via a defined trigger mechanism.

### Requirement: Ephemeral Resource Statelessness

The system SHALL NOT manage IaC statefiles for ephemeral labs, ensuring stateless provision and destroy cycles.

---

## Scenarios

### Scenario: Provision ephemeral lab with Terraform

- GIVEN budget of $10 and lab spec requesting 5 EC2 instances with k6 installed
- WHEN InfrastructureAgent receives the lab specification
- THEN it SHALL generate Terraform HCL, estimate cost ≤$8, apply within 10 minutes, and return lab endpoints

### Scenario: Provision ephemeral lab with Pulumi

- GIVEN budget of $10 and lab spec requesting 5 EC2 instances with k6 installed
- WHEN InfrastructureAgent is configured for Pulumi provider
- THEN it SHALL generate Pulumi SDK code, estimate cost ≤$8, apply within 10 minutes, and return lab endpoints

### Scenario: Cost cap enforcement

- GIVEN a running lab with $8 of estimated spend accumulated
- WHEN actual spend approaches budget cap (≥$9.50)
- THEN the system SHALL auto-destroy all lab resources within 60 seconds and emit a cost_alert

### Scenario: StrategyManager triggers InfrastructureAgent

- GIVEN StrategyManager has a test plan with performance testing focus
- WHEN the phased_approach includes a performance phase with effort.performance > 0.1
- THEN StrategyManager SHALL invoke InfrastructureAgent with lab_spec and budget_constraints

### Scenario: Resource cleanup on timeout

- GIVEN InfrastructureAgent provisions resources
- WHEN destroy is not completed within 15 minutes of test completion
- THEN the watchdog SHALL force-destroy all resources and log an orphan event

### Scenario: IaC validation before apply

- GIVEN generated IaC code (Terraform HCL or Pulumi SDK)
- WHEN InfrastructureAgent attempts to apply
- THEN it SHALL first run `terraform plan` or `pulumi preview` to validate, and abort if validation fails

### Scenario: Invalid IaC handling

- GIVEN generated IaC fails schema validation or dry-run
- WHEN InfrastructureAgent attempts to apply
- THEN it SHALL emit an error event, log the failure, and set status to failed without charges

### Scenario: Retry on rate limiting

- GIVEN Terraform or Pulumi API returns rate limit error (429)
- WHEN InfrastructureAgent receives the error
- THEN it SHALL retry with exponential backoff (max 3 retries) before declaring failure

### Scenario: Lab destruction after test

- GIVEN k6 load test completes successfully
- WHEN InfrastructureAgent receives test completion signal
- THEN it SHALL execute `terraform destroy` or `pulumi destroy` within 5 minutes and confirm cleanup

---

## MODIFIED Requirements

None.

## REMOVED Requirements

None.