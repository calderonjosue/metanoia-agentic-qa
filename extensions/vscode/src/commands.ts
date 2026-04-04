import * as vscode from 'vscode';

export function registerCommands(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand('metanoia.startSprint', async () => {
            const config = vscode.workspace.getConfiguration('metanoia');
            const apiUrl = config.get<string>('apiUrl', 'http://localhost:3000');
            
            try {
                vscode.window.showInformationMessage('Starting Metanoia-QA Sprint...');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to start sprint: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('metanoia.viewStatus', async () => {
            vscode.window.showInformationMessage('Metanoia-QA Status: Running');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('metanoia.viewDashboard', async () => {
            const panel = vscode.window.createWebviewPanel(
                'metanoia-qa',
                'Metanoia-QA Dashboard',
                vscode.ViewColumn.One,
                {}
            );
            panel.webview.html = getDashboardHtml();
        })
    );
}

function getDashboardHtml(): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; }
        h1 { color: var(--vscode-foreground); }
        .status { margin: 20px 0; }
        .agent { padding: 10px; margin: 5px 0; background: var(--vscode-editor-background); border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Metanoia-QA Dashboard</h1>
    <div class="status">
        <div class="agent">Test Agent: Idle</div>
        <div class="agent">Coverage Agent: Idle</div>
        <div class="agent">Regression Agent: Idle</div>
    </div>
</body>
</html>`;
}
