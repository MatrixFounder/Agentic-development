## 2. Media storage

Fernhill Photos keeps every uploaded photo and its thumbnail in one object store. This section
describes the four components that use that store and the relations between them.

### 2.1 Components

| Component | Technology | Owner | Responsibility |
| :--- | :--- | :--- | :--- |
| Upload API | Go service | Gallery team | stores each uploaded photo as an original |
| Media bucket | object storage | Platform team | holds originals and thumbnails, one prefix each |
| Thumbnail service | Python worker | Gallery team | produces one thumbnail per original |
| CDN | managed edge cache | Platform team | serves thumbnails at the network edge |

### 2.2 Relations

- The Upload API writes originals to the Media bucket.
- The Thumbnail service reads originals from the Media bucket.
- The Thumbnail service writes thumbnails to the Media bucket.
- The CDN reads thumbnails from the Media bucket.

No other component reads or writes the Media bucket.

### 2.3 Access rules

Each component signs its requests with its own service identity. The Upload API may write only
under the originals prefix. The Thumbnail service may read the originals prefix and may write only
under the thumbnails prefix. The CDN may read only the thumbnails prefix. The Platform team grants
these permissions and reviews them whenever a component changes owner.

### 2.4 Out of scope

Image moderation, the storage classes of the Media bucket and the cache rules of the CDN are
described in §5.
