#!/usr/bin/env node
const fs = require('fs');

try {
    const input = JSON.parse(fs.readFileSync(0, 'utf-8'));
    const messages = input.llm_request.messages || [];
    const lastMsg = messages.reverse().find(m => m.role === 'user');

    if (!lastMsg) {
        console.log(JSON.stringify({}));
        process.exit(0);
    }

    const text = lastMsg.content.toLowerCase();
    const allowed = ['write_todos']; // Memory is always allowed

    // Simple Intent Logic
    if (text.includes('read') || text.includes('check')) {
        allowed.push('read_file', 'list_directory');
    }

    if (allowed.length > 1) {
        console.log(JSON.stringify({
            hookSpecificOutput: {
                toolConfig: {
                    mode: 'ANY',
                    allowedFunctionNames: allowed
                }
            }
        }));
    } else {
        console.log(JSON.stringify({}));
    }
} catch (e) {
    console.error(e);
    process.exit(2);
}
