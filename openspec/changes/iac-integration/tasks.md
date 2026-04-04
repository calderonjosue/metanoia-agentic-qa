# Tasks: Autonomous IaC Integration

## Phase 1: Infrastructure Types and Interfaces

- [ ] 1.1 Define `LabSpec` and `LabResources` models in `src/infrastructure/models.py`
- [ ] 1.2 Create `IaCProvider` abstract base class in `src/infrastructure/iac_providers/base.py`
- [ ] 1.3 Define `ValidationResult` and `CostEstimate` types in `src/infrastructure/iac_providers/base.py`
- [ ] 1.4 Add InfrastructureAgent type to `AgentType` enum in `src/agents/base.py`

## Phase 2: Terraform Provider Implementation

- [ ] 2.1 Create `TerraformProvider` class in `src/infrastructure/iac_providers/terraform_provider.py`
- [ ] 2.2 Implement `generate()` to produce Terraform HCL from `LabSpec`
- [ ] 2.3 Implement `validate()` to run `terraform plan` and parse output
- [ ] 2.4 Implement `apply()` to run `terraform apply` and capture resource IDs
- [ ] 2.5 Implement `destroy()` to run `terraform destroy`

## Phase 3: Pulumi Provider Implementation

- [ ] 3.1 Create `PulumiProvider` class in `src/infrastructure/iac_providers/pulumi_provider.py`
- [ ] 3.2 Implement `generate()` to produce Pulumi SDK Python code from `LabSpec`
- [ ] 3.3 Implement `validate()` to run `pulumi preview` and parse output
- [ ] 3.4 Implement `apply()` to run `pulumi up` and capture resource IDs
- [ ] 3.5 Implement `destroy()` to run `pulumi destroy`

## Phase 4: Lab Lifecycle and Cost Management

- [ ] 4.1 Create `LabLifecycleManager` in `src/infrastructure/lab_lifecycle_manager.py`
- [ ] 4.2 Implement provision → configure → test → destroy flow
- [ ] 4.3 Create `CostController` in `src/infrastructure/cost_controller.py`
- [ ] 4.4 Implement cost estimation from plan/preview output
- [ ] 4.5 Implement budget cap enforcement with auto-destroy on overspend
- [ ] 4.6 Create `Watchdog` process in `src/infrastructure/watchdog.py`
- [ ] 4.7 Implement 15-minute timeout force-destroy logic

## Phase 5: InfrastructureAgent Implementation

- [ ] 5.1 Create `InfrastructureAgent` class in `src/agents/infrastructure_agent.py`
- [ ] 5.2 Implement `execute()` to accept lab spec and orchestrate lifecycle
- [ ] 5.3 Implement provider selection based on config (terraform vs pulumi)
- [ ] 5.4 Integrate cost estimation before apply
- [ ] 5.5 Handle destroy completion and resource verification

## Phase 6: StrategyManager Integration

- [ ] 6.1 Add `invoke_infrastructure_agent()` method to `StrategyManager`
- [ ] 6.2 Detect performance testing phases (effort.performance > 0.1)
- [ ] 6.3 Construct lab spec from test plan context
- [ ] 6.4 Pass budget constraints from config/defaults

## Phase 7: Configuration

- [ ] 7.1 Add InfrastructureAgent definition to `config/agents.yaml`
- [ ] 7.2 Define default budget cap ($10), timeout (15 min), instance limits
- [ ] 7.3 Add AWS credentials configuration requirements to docs

## Phase 8: Testing

- [ ] 8.1 Write unit tests for `TerraformProvider.generate()` with mocked LabSpec
- [ ] 8.2 Write unit tests for `PulumiProvider.generate()` with mocked LabSpec
- [ ] 8.3 Write unit tests for `CostController.estimate_from_plan_output()`
- [ ] 8.4 Write integration tests for `LabLifecycleManager` with LocalStack
- [ ] 8.5 Write E2E test for full provision→k6→destroy cycle (skip if no AWS creds)