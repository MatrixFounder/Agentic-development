```mermaid
flowchart LR
    accTitle: Relations between the media storage components
    accDescr: The Upload API writes originals to the Media bucket. The Thumbnail service reads originals from the Media bucket and writes thumbnails to it. The CDN reads thumbnails from the Media bucket.

    upload["Upload API"]
    bucket[("Media bucket")]
    thumbs["Thumbnail service"]
    cdn["CDN"]

    upload -->|"originals"| bucket
    bucket -->|"originals"| thumbs
    thumbs -->|"thumbnails"| bucket
    bucket -->|"thumbnails"| cdn
```

*Figure 2.1: Media storage relations. Arrows show the direction in which originals and thumbnails move. The Upload API and the Thumbnail service write to the Media bucket, and the Thumbnail service and the CDN read from it.*