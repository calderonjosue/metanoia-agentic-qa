#!/bin/bash
# Rollback to v1.0 baseline
git checkout backup-v1.0.0 -- .
git tag -d phase1-complete phase2-complete phase3-complete 2>/dev/null
echo "Rolled back to backup-v1.0.0"
