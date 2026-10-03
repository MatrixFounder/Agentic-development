**Figure 1.** Media bucket relations: which prefix of the Media bucket each component writes or reads.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Media bucket relations
  accDescr: Which prefix of the Media bucket each component writes or reads.
  UP("Upload API<br/><small>Go service</small>")
  TH("Thumbnail service<br/><small>Python worker</small>")
  CDN["CDN<br/><small>managed edge cache</small>"]
  subgraph MB["Media bucket"]
    ORIG[("Originals prefix")]
    THUMB[("Thumbnails prefix")]
  end
  UP -->|"write"| ORIG
  TH -->|"read"| ORIG
  TH -->|"write"| THUMB
  CDN -->|"read"| THUMB
  class UP,TH wf
  class ORIG,THUMB db
  class CDN svc
  style MB fill:#7F7F7F0D,stroke:#90A4AE
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

Legend:
- rounded box = Gallery team service; rectangle = managed service
- grey frame = Media bucket; cylinder = one of its two prefixes
- arrow = a write or a read, from the component to the prefix