**Table 4.2.** Permissions: which role may perform which operation under RL-1 to RL-7.

| Operation | Viewer | Editor | Publisher | Admin |
| :--- | :---: | :---: | :---: | :---: |
| Read pages | **yes** · RL-1 | **yes** · RL-2 | **yes** · RL-4 | **yes** · RL-6 |
| Edit drafts | no · RL-1 | **yes** · RL-2 | **yes** · RL-4 | **yes** · RL-6 |
| Upload media | no · RL-1 | **yes** · RL-2 | no · RL-5 | **yes** · RL-6 |
| Publish pages | no · RL-1 | no · RL-3 | **yes** · RL-4 | **yes** · RL-6 |
| Unpublish pages | no · RL-1 | no · RL-3 | **yes** · RL-4 | **yes** · RL-6 |
| Manage users | no · RL-1 | no · RL-7 | no · RL-7 | **yes** · RL-6 |
| Change settings | no · RL-1 | no · RL-7 | no · RL-7 | **yes** · RL-6 |

**yes**: the role may perform the operation. no: the server refuses the request before any page or file changes (§4.2.2). Each cell names the rule that decides it.