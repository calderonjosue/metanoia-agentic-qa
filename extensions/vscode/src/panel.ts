import * as vscode from 'vscode';

export class MetanoiaPanel implements vscode.WebviewPanelProvider {
    public static readonly viewType = 'metanoia-qa';
    
    constructor(private context: vscode.ExtensionContext) {}
    
    resolveWebviewPanel(panel: vscode.WebviewPanel): void {
        panel.webview.html = this.getHtmlContent();
    }
    
    private getHtmlContent(): string {
        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metanoia-QA</title>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); background: var(--vscode-editor-background); }
        h1 { color: #007acc; }
        #status { margin: 20px 0; padding: 15px; background: var(--vscode-sideBar-background); border-radius: 8px; }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-value { font-size: 24px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Metanoia-QA Dashboard</h1>
    <div id="status">
        <div class="metric">
            <div class="metric-value" id="testCount">0</div>
            <div>Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value" id="coverage">0%</div>
            <div>Coverage</div>
        </div>
        <div class="metric">
            <div class="metric-value" id="agents">0</div>
            <div>Active Agents</div>
        </div>
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        document.getElementById('testCount').textContent = '42';
        document.getElementById('coverage').textContent = '87%';
        document.getElementById('agents').textContent = '3';
    </script>
</body>
</html>`;
    }
}
