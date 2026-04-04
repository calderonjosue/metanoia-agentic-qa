# Proposal: Metanoia Skill Hub CLI

## Intent

Create a decentralized marketplace for Metanoia skills, enabling community contributions via CLI commands like `metanoia install skill cypress-executor`. Inspired by Docker Hub's registry model.

## Scope

### In Scope
- CLI command: `metanoia install skill <name>` to fetch and install community skills
- Registry format: `skill-manifest.yaml` with name, version, author, description, and install script
- Skill schema: standardized structure for skill packages
- Local skill cache: `~/.metanoia/skills/` directory for installed community skills
- Search command: `metanoia search skill <query>` to discover community skills

### Out of Scope
- Hosting infrastructure (uses GitHub releases/gist as backend)
- Skill ratings/reviews
- Official skill certification
-付费技能/featured skills

## Approach

Follow Docker Hub pattern:
1. Skills published to GitHub repos with `skill-manifest.yaml` in root
2. CLI resolves `metanoia skill install <owner/repo>` or `metanoia install skill <name>` (shortcut)
3. Downloads manifest, validates schema, runs install script to `~/.metanoia/skills/`
4. Installed skills appear in `metanoia list skills`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/cli/commands/` | New | `install-skill.ts` command |
| `src/cli/commands/` | New | `search-skill.ts` command |
| `src/schemas/` | New | `skill-manifest.ts` schema |
| `src/skill-manager.ts` | New | Handles registry lookup and installation |
| `~/.metanoia/skills/` | New | Local skill cache directory |
| `docs/` | Modified | Add skill hub documentation |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Malicious community skills | Low | Sandbox execution, user confirmation prompt |
| Breaking skill schema changes | Low | Version field in manifest, migration guide |
| GitHub API rate limits | Medium | Local cache with TTL, fallback to direct repo clone |

## Rollback Plan

1. Remove installed skill from `~/.metanoia/skills/<skill-name>/`
2. Delete skill cache entry
3. User can re-install official skills via `metanoia init`

## Dependencies

- GitHub CLI (`gh`) or git for repo access
- Existing skill loader infrastructure

## Success Criteria

- [ ] `metanoia install skill cypress-executor` installs a test skill successfully
- [ ] `metanoia list skills` shows both built-in and community skills
- [ ] `metanoia search skill <query>` returns matching results from known repos
- [ ] Documentation explains how to publish a community skill
