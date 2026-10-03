**Permission matrix.** The operations each role may perform, with the rule of §4.2.1 that decides each cell.

| Operation | Viewer | Editor | Publisher | Admin |
| :--- | :---: | :---: | :---: | :---: |
| Read pages | yes · RL-1 | yes · RL-2 | yes · RL-4 | yes · RL-6 |
| Edit drafts | no · RL-1 | yes · RL-2 | yes · RL-4 | yes · RL-6 |
| Upload media | no · RL-1 | yes · RL-2 | no · RL-5 | yes · RL-6 |
| Publish pages | no · RL-1 | no · RL-3 | yes · RL-4 | yes · RL-6 |
| Unpublish pages | no · RL-1 | no · RL-3 | yes · RL-4 | yes · RL-6 |
| Manage users | no · RL-1 | no · RL-7 | no · RL-7 | yes · RL-6 |
| Change settings | no · RL-1 | no · RL-7 | no · RL-7 | yes · RL-6 |

`yes` means the rule grants the operation to the role, and `no` means the rule withholds it. The roles are not cumulative: the Publisher column has no upload media (RL-5). The server refuses every `no` cell before any page or file changes (§4.2.2).