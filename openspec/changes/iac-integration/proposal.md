# Proposal: Autonomous IaC Integration

## Intent

Enable agents to autonomously build and tear down test infrastructure on-demand. InfrastructureAgent writes/executes Terraform or Pulumi to provision ephemeral labs—5 EC2 instances, deploy app, run k6 load tests, then destroy everything. StrategyManager triggers this when concurrency testing is needed, eliminating manual infra setup and ensuring consistent, repeatable lab environments.

## Scope

### In Scope
- **InfrastructureAgent**: New agent that authors and executes IaC (Terraform/Pulumi) programmatically
- **IaC Provider Abstraction**: Unified interface supporting both Terraform and Pulumi backends
- **Ephemeral Lab Lifecycle**: Provision → Configure → Test → Destroy with cost tracking
- **Cost Management**: Budget caps, auto-destroy on overspend, spend alerts
- **StrategyManager Integration**: Trigger mechanism for InfrastructureAgent when concurrency testing requested

### Out of Scope
- Multi-cloud support beyond AWS EC2 (future: GCP, Azure)
- Persistent infrastructure management
- IaC statefile management (stateless ephemeral labs)
- Direct Kubernetes cluster provisioning

## Approach

Agent-based IaC automation where InfrastructureAgent:
1. Accepts high-level intent (e.g., "5 EC2 instances with k6 running")
2. Generates domain-specific IaC code (HCL for Terraform, Pulumi SDK for Pulumi)
3. Executes `terraform apply` / `pulumi up` via local process or remote backend
4. Waits for resources, deploys test app via userdata/SSM
5. Executes k6 against target
6. Captures metrics, destroys all resources

**StrategyManager** monitors test requests; when concurrency scenarios detected, it instantiates InfrastructureAgent with lab spec and budget constraints.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `agents/infrastructure/` | New | InfrastructureAgent implementation |
| `infrastructure/iac-providers/` | New | Terraform/Pulumi abstraction layer |
| `infrastructure/lab-lifecycle/` | New | Provision→test→destroy orchestration |
| `cost-control/` | New | Budget tracking, auto-destroy guards |
| `agents/strategy/` | Modified | StrategyManager triggers InfrastructureAgent |
| `config/agents.yaml` | Modified | Agent definitions and permissions |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| IaC execution exceeds budget | Medium | Hard budget cap + auto-destroy; cost estimation before apply |
| Terraform/Pulumi API rate limits | Low | Implement retry with exponential backoff |
| Resource cleanup failures | Medium | Force-destroy on timeout; orphan tracking |
| Agent generates invalid IaC | Low | Schema validation + dry-run before apply |

## Rollback Plan

- InfrastructureAgent logs all `terraform destroy` / `pulumi destroy` commands
- On failure: re-run destroy with `--force` flag
- Orphaned resources detected via cloud provider API scan and tagged cleanup
- If agent crashes mid-execution: watchdog process terminates remaining resources after 15-min timeout

## Dependencies

- AWS credentials configured for terraform/pulumi (STS assume-role)
- k6 binary available in execution environment
- Terraform ≥1.5 or Pulumi ≥3.80 installed

## Success Criteria

- [ ] InfrastructureAgent provisions 5 EC2 instances within 10 minutes
- [ ] k6 load test executes against deployed app
- [ ] All resources destroyed within 5 minutes of test completion
- [ ] Total lab cost stays under configured budget (default: $10)
- [ ] StrategyManager successfully triggers InfrastructureAgent on concurrency test request
