"""Output path guards shared by the RPF9 probes."""

import os
import tempfile


class OutputCollisionError(ValueError):
    """The requested output names an input file."""


def same_path(a, b):
    try:
        if os.path.exists(a) and os.path.exists(b) and os.path.samefile(a, b):
            return True
    except OSError:
        pass
    return os.path.normcase(os.path.realpath(os.path.abspath(a))) == os.path.normcase(
        os.path.realpath(os.path.abspath(b))
    )


def guard_output(output, inputs):
    if not output:
        return
    for path in inputs:
        if path and same_path(output, path):
            raise OutputCollisionError(
                "refusing to write output over the input file %s" % path
            )


def write_atomic(path, text):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, temporary = tempfile.mkstemp(prefix=".rpf9-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
