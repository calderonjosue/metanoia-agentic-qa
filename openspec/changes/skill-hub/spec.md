# Skill Hub Specification

## Purpose

Enable decentralized skill marketplace for Metanoia, allowing community-contributed skills to be discovered, installed, and managed via CLI commands.

## Requirements

### Requirement: Skill Installation

The system MUST support installing community skills via `metanoia install skill <name>` command. The system SHALL fetch the skill manifest from the registry and execute the install script.

#### Scenario: Install skill by short name

- GIVEN a community skill named "cypress-executor" exists in the registry
- WHEN the user runs `metanoia install skill cypress-executor`
- THEN the system SHALL resolve the short name to the full owner/repo path
- AND SHALL download and validate the skill-manifest.yaml
- AND SHALL execute the install script to ~/.metanoia/skills/

#### Scenario: Install skill by owner/repo

- GIVEN a community skill exists at owner/repo
- WHEN the user runs `metanoia install skill owner/repo`
- THEN the system SHALL fetch the skill-manifest.yaml from that repo
- AND SHALL validate the manifest schema
- AND SHALL execute the install script

#### Scenario: Install fails due to invalid manifest

- GIVEN a skill repository has a malformed skill-manifest.yaml
- WHEN the user attempts to install that skill
- THEN the system SHALL reject the installation
- AND SHALL display a validation error with the specific field issue

### Requirement: Skill Search

The system SHOULD support searching for community skills via `metanoia search skill <query>` command. The system MAY use a local index or query the registry API.

#### Scenario: Search returns matching skills

- GIVEN multiple community skills exist with "cypress" in name or description
- WHEN the user runs `metanoia search skill cypress`
- THEN the system SHALL display a list of matching skills
- AND SHALL include name, author, version, and description for each

#### Scenario: Search returns empty results

- GIVEN no community skills match the search query "nonexistent-skill-xyz"
- WHEN the user runs `metanoia search skill nonexistent-skill-xyz`
- THEN the system SHALL display an empty result set
- AND SHALL suggest broadening the search query

### Requirement: Skill Listing

The system MUST list all installed skills (both built-in and community) via `metanoia list skills`. Community skills SHALL be visually distinguished from built-in skills.

#### Scenario: List shows mixed built-in and community skills

- GIVEN the user has installed the "cypress-executor" community skill
- AND Metanoia has built-in skills
- WHEN the user runs `metanoia list skills`
- THEN the system SHALL display all skills
- AND community skills SHALL be marked with a indicator (e.g., [community])

### Requirement: Skill Manifest Schema

All community skills MUST provide a valid skill-manifest.yaml with: name, version, author, description, and install script fields. The system SHALL reject manifests missing required fields.

#### Scenario: Valid manifest passes validation

- GIVEN a skill-manifest.yaml with all required fields (name, version, author, description, install)
- WHEN the system validates the manifest
- THEN the manifest SHALL pass validation

#### Scenario: Missing required field fails validation

- GIVEN a skill-manifest.yaml missing the "author" field
- WHEN the system validates the manifest
- THEN validation SHALL fail
- AND the error SHALL indicate "author" is missing

### Requirement: Skill Cache

Installed community skills MUST be cached locally in ~/.metanoia/skills/. The system SHOULD support cache invalidation based on TTL.

#### Scenario: Installed skill is cached

- GIVEN a community skill has been successfully installed
- WHEN installation completes
- THEN the skill files SHALL be present in ~/.metanoia/skills/<skill-name>/
- AND the manifest SHALL be cached

### Requirement: Security Confirmation

The system SHALL prompt for user confirmation before executing install scripts from community skills. The system MUST allow skipping this prompt via a flag.

#### Scenario: Installation prompts for confirmation

- GIVEN a user attempts to install an unverified community skill
- WHEN the install command runs without --yes flag
- THEN the system SHALL prompt "Are you sure you want to install <skill> from <author>?"
- AND SHALL wait for user confirmation

#### Scenario: Installation skips confirmation with flag

- GIVEN a user attempts to install a community skill with --yes flag
- WHEN the install command runs
- THEN the system SHALL NOT prompt for confirmation
- AND SHALL proceed directly with installation

### Requirement: Rollback Capability

The system MUST support removing an installed community skill. Uninstalling a skill MUST remove files from ~/.metanoia/skills/<skill-name>/.

#### Scenario: Uninstall removes skill files

- GIVEN a community skill "cypress-executor" is installed
- WHEN the user runs `metanoia uninstall skill cypress-executor`
- THEN the system SHALL remove ~/.metanoia/skills/cypress-executor/
- AND SHALL update the skill registry cache
