# Design: Metanoia Skill Hub CLI

## Technical Approach

Implement a Docker Hub-inspired registry pattern where skills are GitHub repositories containing a `skill-manifest.yaml`. The CLI resolves short names via a manifest index, downloads manifests, validates schemas, and executes install scripts to a local cache.

## Architecture Decisions

### Decision: GitHub as Registry Backend

**Choice**: Use GitHub repositories with `skill-manifest.yaml` as the skill registry
**Alternatives considered**: Centralized database, dedicated registry service, npm-style package registry
**Rationale**: Zero hosting infrastructure, leverages existing GitHub CLI (`gh`) or git, natural versioning via git tags/releases, easy for community to contribute

### Decision: Local Cache in ~/.metanoia/skills/

**Choice**: Cache installed skills locally in user home directory
**Alternatives considered**: Project-local node_modules-style, centralized system cache
**Rationale**: User isolation (each user manages own skills), works across projects, easy rollback (delete directory)

### Decision: YAML Manifest Schema

**Choice**: `skill-manifest.yaml` with name, version, author, description, install
**Alternatives considered**: JSON schema, TypeScript definition file
**Rationale**: Human-readable, widely supported, easy to validate without TypeScript compilation, familiar format (similar to package.json)

### Decision: Shell Script for Installation

**Choice**: Allow install script execution within skill package
**Alternatives considered**: Structured copy-only install, declarative file mapping
**Rationale**: Flexibility for complex setups (compile TypeScript, link binaries, configure hooks), matches Docker Hub RUN command model

## Data Flow

```
User: metanoia install skill cypress-executor
           │
           ▼
┌─────────────────────────────────────────┐
│  SkillResolver: Resolve short name      │
│  - Check local manifest index            │
│  - Fallback: query known skill repos    │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  ManifestFetcher: Download manifest     │
│  - gh repo view owner/skill --json      │
│  - Or: git clone --depth 1              │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  ManifestValidator: Validate schema     │
│  - Check required fields                │
│  - Verify version format                │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  ConfirmationPrompt (if --yes not set) │
│  - Display skill info                   │
│  - Await user input                     │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  InstallExecutor: Run install script    │
│  - Execute in ~/.metanoia/skills/name  │
│  - Capture output, check exit code      │
└─────────────────────────────────────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/cli/commands/install-skill.ts` | Create | `metanoia install skill` command |
| `src/cli/commands/search-skill.ts` | Create | `metanoia search skill` command |
| `src/cli/commands/uninstall-skill.ts` | Create | `metanoia uninstall skill` command |
| `src/cli/commands/list-skills.ts` | Modify | Add community skill indicator |
| `src/schemas/skill-manifest.ts` | Create | Manifest validation schema |
| `src/skill-manager.ts` | Create | Registry lookup, install, cache logic |
| `src/skill-resolver.ts` | Create | Name resolution (short → owner/repo) |
| `~/.metanoia/skills/` | Create | Local skill cache directory |

## Interfaces / Contracts

```typescript
interface SkillManifest {
  name: string;        // Required: skill identifier
  version: string;     // Required: semver
  author: string;      // Required: author name/handle
  description: string; // Required: short description
  install: string;     // Required: shell command to install
  homepage?: string;   // Optional: project page
  repository?: string; // Optional: git repository URL
}

interface InstalledSkill {
  manifest: SkillManifest;
  installedAt: Date;
  sourceRepo: string;
}
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Manifest validation | Jest: valid/invalid YAML cases |
| Unit | Name resolution | Jest: mock manifest index |
| Integration | Install flow | Mock git/gh, verify file creation |
| E2E | Full install | `metanoia install skill test-skill` |

## Migration / Rollout

No migration required. New CLI commands are additive. Existing functionality unchanged.

## Open Questions

- [ ] Should we maintain a manifest index for short-name resolution, or always require owner/repo?
- [ ] What is the TTL for cache invalidation? Default 24h?
- [ ] Do we need to sandbox install script execution (e.g., Docker container)?
