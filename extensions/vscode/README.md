# Metanoia-QA VS Code Extension

AI-powered QA automation for VS Code with real-time test agent monitoring.

## Installation

```bash
npm install
npm run compile
code --install-extension out/metanoia-qa-*.vsix
```

## Commands

- `Metanoia: Start Sprint` - Start a new QA sprint
- `Metanoia: View Status` - View current test status
- `Metanoia: Dashboard` - Open the main dashboard

## Configuration

```json
{
  "metanoia.apiUrl": "http://localhost:3000",
  "metanoia.autoRefresh": true,
  "metanoia.refreshInterval": 5000
}
```
