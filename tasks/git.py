from invoke import task
from faasmctl.util.env import DEV_PROJ_ROOT
from faasmctl.util.faasm import get_version as get_faasm_version
from faasmctl.util.version import get_version
from os.path import join
from subprocess import run

VERSIONED_FILES = [
    "pyproject.toml",
    "README.md",
    "faasmctl/util/version.py",
]


@task
def tag(ctx, force=False):
    """
    Creates git tag from the current tree
    """
    version = get_version()
    tag_name = "v{}".format(version)
    run(
        "git tag {} {}".format("--force" if force else "", tag_name),
        shell=True,
        check=True,
        cwd=DEV_PROJ_ROOT,
    )

    run(
        "git push {} origin {}".format("--force" if force else "", tag_name),
        shell=True,
        check=True,
        cwd=DEV_PROJ_ROOT,
    )


@task
def bump(ctx, patch=False, minor=False, major=False):
    """
    Bump the code version by --patch, --minor, or --major
    """
    old_ver = get_version()
    new_ver_parts = old_ver.split(".")

    if patch:
        idx = 2
    elif minor:
        idx = 1
    elif major:
        idx = 0
    else:
        raise RuntimeError("Must set one in: --[patch,minor,major]")

    # Change the corresponding idx
    new_ver_parts[idx] = str(int(new_ver_parts[idx]) + 1)

    # Zero-out the following version numbers (i.e. lower priority). This is
    # because if we tag a new major release, we want to zero-out the minor
    # and patch versions (e.g. 0.2.0 comes after 0.1.9)
    for next_idx in range(idx + 1, 3):
        new_ver_parts[next_idx] = "0"

    new_ver = ".".join(new_ver_parts)

    for f in VERSIONED_FILES:
        sed_cmd = "sed -i 's/{}/{}/g' {}".format(old_ver, new_ver, f)
        run(sed_cmd, shell=True, check=True, cwd=DEV_PROJ_ROOT)


@task
def bump_dep(ctx, faasm=None):
    """
    Bump the version of a tracked dependency
    """
    if faasm is not None:
        new_ver = faasm
        old_ver = get_faasm_version()

        files_to_check = [
            join(DEV_PROJ_ROOT, "faasmctl", "util", "faasm.py"),
            join(DEV_PROJ_ROOT, "bin", "gen_proto_files.py"),
        ]

        for f in files_to_check:
            sed_cmd = "sed -i 's/{}/{}/g' {}".format(old_ver, new_ver, f)
            run(sed_cmd, shell=True, check=True)
