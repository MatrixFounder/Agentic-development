### 4.2 Roles

Quarry CMS checks every request against the role of the signed-in user. Each user holds exactly
one role, and the role alone decides which operations the user may perform.
There are four roles: Viewer, Editor, Publisher and Admin.

The roles act on seven operations: read pages, edit drafts, upload media, publish pages,
unpublish pages, manage users and change settings. Editing a draft never changes the live version
of a page. Publishing a page makes its draft the live version; unpublishing the page takes it
offline.

#### 4.2.1 Permissions

- **RL-1.** A Viewer may read pages. A Viewer may perform no other operation.
- **RL-2.** An Editor may read pages, edit drafts and upload media.
- **RL-3.** An Editor may not publish pages and may not unpublish pages.
- **RL-4.** A Publisher may read pages, edit drafts, publish pages and unpublish pages.
- **RL-5.** A Publisher may not upload media.
- **RL-6.** An Admin may perform all seven operations.
- **RL-7.** Only an Admin may manage users and change settings.

The roles are not cumulative. A Publisher does not hold every permission of an Editor: RL-5
withholds upload media from the Publisher, so uploads stay with Editors and Admins, who answer for
the files they bring in.

#### 4.2.2 Completeness

This list is complete. An operation that the list does not grant to a role is denied to that
role, and the server refuses the request before any page or file changes. No other role exists;
the installer creates the first Admin account.
