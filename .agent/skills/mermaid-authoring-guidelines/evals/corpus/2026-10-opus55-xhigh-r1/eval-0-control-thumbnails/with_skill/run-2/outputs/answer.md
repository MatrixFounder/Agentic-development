**Figure 2.1.** Media bucket relations: what each component reads from or writes to the Media bucket.

```text figure
+-------------------+   writes originals         +--------------+
| Upload API        |--------------------------->|              |
+-------------------+                            |              |
                                                 |              |
                        reads originals          |              |
+-------------------+   writes thumbnails        |              |
| Thumbnail service |--------------------------->| Media bucket |
+-------------------+                            |              |
                                                 |              |
+-------------------+   reads thumbnails         |              |
| CDN               |--------------------------->|              |
+-------------------+                            +--------------+
```

- box = a component of §2.1
- arrow = requests from a component to the Media bucket; its label names what the component reads or writes