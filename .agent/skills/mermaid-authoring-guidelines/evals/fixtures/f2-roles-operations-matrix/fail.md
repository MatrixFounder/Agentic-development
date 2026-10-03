```mermaid
flowchart LR
    Viewer --> READ[read pages]
    Editor --> READ
    Editor --> EDIT[edit drafts]
    Editor --> UPLOAD[upload media]
    Publisher --> READ
    Publisher --> EDIT
    Publisher --> UPLOAD
    Publisher --> PUB[publish pages]
    Publisher --> UNPUB[unpublish pages]
    Admin --> READ
    Admin --> EDIT
    Admin --> UPLOAD
    Admin --> PUB
    Admin --> UNPUB
    Admin --> USERS[manage users]
    Admin --> SETTINGS[change settings]
```
