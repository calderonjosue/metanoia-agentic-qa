# Design: Autonomous IaC Integration

## Technical Approach

InfrastructureAgent operates as an agent extension that receives lab specifications and executes IaC workflows. StrategyManager triggers it via an async invoke mechanism when performance testing phases are detected. The agent uses a provider abstraction layer to support both Terraform and Pulumi backends.

## Architecture Decisions

### Decision: IaC Provider Abstraction via Strategy Pattern

**Choice**: Define `IaCProvider` interface with concrete implementations `TerraformProvider` and `PulumiProvider`.
**Alternatives considered**: Plugin architecture with dynamic loading; Provider factory with switch statements.
**Rationale**: Strategy pattern allows swapping providers at runtime without modifying client code. Factory adds indirection without benefit given only two providers.

### Decision: Stateless Ephemeral Labs

**Choice**: No IaC statefile persistence between labs.
**Alternatives considered**: Remote state backend (S3/DynamoDB); Local state with cleanup.
**Rationale**: Ephemeral labs require idempotent destroy cycles. Remote state adds dependencies and cost. Local state cleanup creates race conditions in parallel execution.

### Decision: Pre-execution Cost Estimation

**Choice**: Call `terraform plan` / `pulumi preview` before apply to estimate cost.
**Alternatives considered**: Fixed per-instance cost tables; AWS pricing API live lookup.
**Rationale**: Plan output includes resource counts and basic sizing. AWS pricing API adds latency and complexity. Fixed tables become stale.

### Decision: Watchdog Process for Orphan Handling

**Choice**: Separate watchdog process started alongside provision that auto-destroys after 15-min timeout.
**Alternatives considered**: Agent internal timer; CloudWatch event trigger.
**Rationale**: Agent may crash; internal timer dies with it. CloudWatch adds IAM dependencies. Separate process with independent lifecycle ensures cleanup.

## Data Flow

```
StrategyManager
    │
    ▼ (async invoke)
InfrastructureAgent
    │
    ▼
IaCProviderFactory ──► IaCProvider (Terraform | Pulumi)
    │                      │
    │                      ▼
    │                 IaCExecutor
    │                      │
    │      ┌───────────────┼───────────────┐
    │      ▼               ▼               ▼
    │   terraform        pulumi         CostEstimation
    │   apply            up              (plan/preview)
    │      │               │
    │      └───────────────┼───────────────┘
    │                     ▼
    │              LabResources
    │                     │
    ▼                     ▼
k6 Execution ◄───── Deploy & Configure
    │
    ▼
LabLifecycleManager.destroy()
    │
    ▼
Watchdog (if destroy fails within 15min → force destroy)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/agents/infrastructure_agent.py` | Create | InfrastructureAgent with IaC orchestration logic |
| `src/infrastructure/iac_providers/base.py` | Create | IaCProvider abstract base class |
| `src/infrastructure/iac_providers/terraform_provider.py` | Create | Terraform implementation |
| `src/infrastructure/iac_providers/pulumi_provider.py` | Create | Pulumi implementation |
| `src/infrastructure/lab_lifecycle_manager.py` | Create | Provision→test→destroy orchestration |
| `src/infrastructure/cost_controller.py` | Create | Budget tracking, estimation, auto-destroy |
| `src/infrastructure/watchdog.py` | Create | Orphan resource cleanup process |
| `src/agents/strategy_manager.py` | Modify | Add `invoke_infrastructure_agent()` method |
| `config/agents.yaml` | Modify | Add InfrastructureAgent definition and permissions |

## Interfaces / Contracts

```python
class IaCProvider(ABC):
    @abstractmethod
    def generate(self, lab_spec: LabSpec) -> str: ...
    
    @abstractmethod
    def validate(self, iac_code: str) -> ValidationResult: ...
    
    @abstractmethod
    def apply(self, iac_code: str, budget: float) -> LabResources: ...
    
    @abstractmethod
    def destroy(self, resources: LabResources) -> None: ...

class LabSpec(BaseModel):
    instance_count: int = Field(..., ge=1, le=20)
    instance_type: str = "t3.medium"
    k6_installed: bool = True
    userdata_script: Optional[str] = None
    budget_cap: float = Field(..., gt=0)

class LabResources(BaseModel):
    provider: str
    resource_ids: list[str]
    endpoints: list[str]
    estimated_cost: float
    actual_cost: float = 0.0
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | IaCProvider.generate(), validate(), cost estimation | Mock AWS SDK; assert valid HCL/Pulumi code |
| Integration | terraform apply/destroy cycle | Use LocalStack; verify resource creation |
| Integration | pulumi up/down cycle | Use LocalStack; verify resource creation |
| E2E | Full lab lifecycle with k6 | Provision real AWS resources (teardown mandatory) |

## Migration / Rollout

No migration required. New module with no existing data dependencies.

## Open Questions

- [ ] Should InfrastructureAgent support async execution (parallel lab provisioning)?
- [ ] Do we need AWS region selection in lab spec, or always use default?
- [ ] Should lab spec include custom AMI or always use default Amazon Linux?