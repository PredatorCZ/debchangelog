# Debian changelog resolver

Used to easily resolve git merge conflicts for debian changelogs.

Currently only pure semantic versions are supported (`MAJOR[.MINOR[.PATCH[.TWEAK]]]`).

If resolver fails, it'll use default git merger as fallback.

## Installation

Run `python3 setup.py install` command to install locally.

### Setup git for single repo

A new merge driver must be created for git config.

Firstly you must enter your local git repo.

```sh
git config merge.dchmerge.driver "dchmerge.py %O %A %B"
```

Such command will create config entry in currently used `.git/config`.

In order to use this merge driver, a new attribute needs to be set.

If not present, create `.gitattributes` file in currently used git repo.

Add line: `changelog merge=dchmerge`

This will tell git to use newly created merge driver for every `changelog` file.

### Setup git for every repo (per user)

Create merge driver:

```sh
git config --global merge.dchmerge.driver "dchmerge.py %O %A %B"
```

This command will create config entry in `~/.gitconfig`.

Locate file `~/.config/git/attributes`. If path/file doesn't exists, create it.

Add line: `changelog merge=dchmerge`

### Custom attributes locations

For more info about where and how to store attributes settings, head to [https://www.git-scm.com/docs/git-config#Documentation/git-config.txt-coreattributesFile](https://www.git-scm.com/docs/git-config#Documentation/git-config.txt-coreattributesFile)
