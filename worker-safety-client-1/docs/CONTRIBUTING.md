# How to contribute to Worker Safety client?

## Branching and commits

> This guide only lists the best practices we follow when creating new branches
> and new commits but, atm, nothing is enforced.

### Glossary

A `type` could be either :

- `feat`: (new feature for the user, not a new feature for build script)
- `fix`: (bug fix for the user, not a fix to a build script)
- `task`: (chore/change the behavior of some part of the application that, eg,
  changing color, text, etc)
- `exploration`: (spiking or testing a new feature)

### Branch names

New branches should follow the format:
`<type>/<username>/(<jira-ticket>)-<subject>`, given that `<jira-ticket>` is
optional.

**Example**

```sh
feat/urbint-user/WS-001-intro
```

### Commit messages

For all commit messages, we follow the **Semantic Commit Messages**. So commits
messages follow the format: `<type>(<scope>): <subject>`, given that `<scope>`
is optional.

**Example**

```sh
feat: add hat wobble
^--^ ^------------^
| |
| +-> Summary in present tense.
|
+-------> Type: chore, docs, feat, fix, refactor, style, or test.
```

Click
[here](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716) for
more information about **Semantic Commit Messages**.

## Pull requests

**TL;DR** use `squash and merge`

Initially, we used the `merge request` strategy, and while it didn't present any
issues, it makes the `main` branch feel **clutter**. And, depending on the way
people use commits, it _may_ include commits that act as snapshots/backup to
some logic that doesn't add anything relevant to the main history branch.

As such, `squash and merge` will create a cleaner and leaner history tree while
still having control of which commit introduce some new feature or even when a
new bug was introduced.
