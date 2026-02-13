#!/usr/bin/env node
const fs = require('fs');

try {
    const input = JSON.parse(fs.readFileSync(0));
    const response = input.prompt_response || '';

    // Example: Check if the agent forgot to include a summary
    if (!response.includes('Summary:')) {
        console.log(
            JSON.stringify({
                decision: 'block', // Triggers an automatic retry turn
                reason: 'Your response is missing a Summary section. Please add one.',
                systemMessage: '🔄 Requesting missing summary from agent...',
            }),
        );
        process.exit(0);
    }

    console.log(JSON.stringify({ decision: 'allow' }));
} catch (e) {
    console.error(e);
    process.exit(2);
}
