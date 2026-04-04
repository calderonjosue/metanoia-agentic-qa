import * as vscode from 'vscode';

const API_BASE = 'http://localhost:3000';

export async function startSprint(sprintId?: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/sprints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sprintId })
    });
    if (!response.ok) throw new Error('Failed to start sprint');
}

export async function getStatus(): Promise<SprintStatus> {
    const response = await fetch(`${API_BASE}/api/status`);
    if (!response.ok) throw new Error('Failed to get status');
    return response.json();
}

export interface SprintStatus {
    testCount: number;
    coverage: number;
    activeAgents: number;
    status: 'idle' | 'running' | 'completed';
}

export async function runTests(testIds?: string[]): Promise<TestResult[]> {
    const response = await fetch(`${API_BASE}/api/tests/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ testIds })
    });
    if (!response.ok) throw new Error('Failed to run tests');
    return response.json();
}

export interface TestResult {
    id: string;
    name: string;
    status: 'passed' | 'failed' | 'skipped';
    duration: number;
}
