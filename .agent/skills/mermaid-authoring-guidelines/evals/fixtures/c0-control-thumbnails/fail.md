```mermaid
graph LR
    A[Upload API] -->|writes originals| B[(Media bucket)]
    B -->|reads originals| C[Thumbnail service]
    C -->|writes thumbnails| B
    B -->|serves thumbnails| D[CDN]
```
