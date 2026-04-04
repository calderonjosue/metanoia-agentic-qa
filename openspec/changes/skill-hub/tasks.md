# Tasks: Metanoia Skill Hub CLI

## Phase 1: Infrastructure

- [ ] 1.1 Create `src/schemas/skill-manifest.ts` with TypeScript interface and Zod validation
- [ ] 1.2 Create `~/.metanoia/skills/` directory structure with .gitkeep
- [ ] 1.3 Add skill manifest schema to `openspec/specs/` if not exists

## Phase 2: Core Implementation

- [ ] 2.1 Create `src/skill-resolver.ts` for short-name to owner/repo resolution
- [ ] 2.2 Create `src/skill-manager.ts` with install, uninstall, list, search methods
- [ ] 2.3 Create `src/cli/commands/install-skill.ts` command handler
- [ ] 2.4 Create `src/cli/commands/search-skill.ts` command handler
- [ ] 2.5 Create `src/cli/commands/uninstall-skill.ts` command handler
- [ ] 2.6 Modify `src/cli/commands/list-skills.ts` to show community indicator

## Phase 3: Integration & Safety

- [ ] 3.1 Add user confirmation prompt for unverified community skills
- [ ] 3.2 Add `--yes` flag to skip confirmation prompt
- [ ] 3.3 Implement cache TTL logic with configurable duration
- [ ] 3.4 Wire new commands into CLI main entry point

## Phase 4: Testing

- [ ] 4.1 Write unit tests for `skill-manifest.ts` validation (valid/invalid cases)
- [ ] 4.2 Write unit tests for `skill-resolver.ts` name resolution
- [ ] 4.3 Write integration tests for install flow (mock git/gh)
- [ ] 4.4 Test end-to-end: `metanoia install skill` and `metanoia list skills`

## Phase 5: Documentation

- [ ] 5.1 Add skill hub documentation to `docs/` (publishing guide, manifest schema)
- [ ] 5.2 Document `~/.metanoia/skills/` structure and rollback procedure
