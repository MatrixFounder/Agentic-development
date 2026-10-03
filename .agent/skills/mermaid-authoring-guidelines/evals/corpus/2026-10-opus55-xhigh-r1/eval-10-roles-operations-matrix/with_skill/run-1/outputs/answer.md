**Table 4.2.** Permissions: which role may perform which operation under RL-1 to RL-7.

| Operation | Viewer | Editor | Publisher | Admin |
| :--- | :---: | :---: | :---: | :---: |
| Read pages | ✓ RL-1 | ✓ RL-2 | ✓ RL-4 | ✓ RL-6 |
| Edit drafts | ✗ RL-1 | ✓ RL-2 | ✓ RL-4 | ✓ RL-6 |
| Upload media | ✗ RL-1 | ✓ RL-2 | ✗ RL-5 | ✓ RL-6 |
| Publish pages | ✗ RL-1 | ✗ RL-3 | ✓ RL-4 | ✓ RL-6 |
| Unpublish pages | ✗ RL-1 | ✗ RL-3 | ✓ RL-4 | ✓ RL-6 |
| Manage users | ✗ RL-1 | ✗ RL-7 | ✗ RL-7 | ✓ RL-6 |
| Change settings | ✗ RL-1 | ✗ RL-7 | ✗ RL-7 | ✓ RL-6 |

✓ means the role may perform the operation. ✗ means the server refuses the request (§4.2.2). Each cell names the rule that decides it.