import * as vscode from 'vscode';
import { registerCommands } from './commands';
import { MetanoiaPanel } from './panel';

export function activate(context: vscode.ExtensionContext) {
    registerCommands(context);
    
    context.subscriptions.push(
        vscode.window.registerWebviewPanelProvider(
            'metanoia-qa',
            new MetanoiaPanel(context)
        )
    );
}

export function deactivate() {}
