**Figure 1.** Media bucket access: the three components that read or write the Media bucket, and what each one reads or writes.

```text figure
+------------+    +-------------------+        +-----+
| Upload API |    | Thumbnail service |        | CDN |
+-----+------+    +---------+---------+        +--+--+
      | writes originals    | reads originals     | reads thumbnails
      |                     | writes thumbnails   |
      v                     v                     v
+----------------------------------------------------+
|                    Media bucket                    |
|        originals prefix, thumbnails prefix         |
+----------------------------------------------------+
```

- box = a component of §2.1; the second line of the Media bucket names its two prefixes
- arrow = a read or write by a component, pointing at the Media bucket; the label says what it reads or writes
- not drawn: owners and technologies (§2.1) and the permissions that back each access (§2.3)