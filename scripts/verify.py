# This gets run as part of "make test" after the sample buffers have
#  been written to disk.

import os
import sys
import filecmp
import glob
import subprocess


if __name__ == "__main__":
    base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
    os.chdir(base_path)

    languages = sys.argv[1:]
    data_path = os.path.join(base_path, "out", "data")
    messages = (glob.glob(os.path.join(data_path, "*.msg")))

    for m in messages:
        os.remove(m)

    for lang in languages:
        os.chdir(os.path.join(base_path, "test", lang))
        status = subprocess.run(["make", "generate"], capture_output=True)
        if not status.returncode == 0:
            sys.stderr.write(status.stderr.decode("utf-8"))
        if not os.path.exists(os.path.join(data_path, "test.%s.msg" % lang)):
            sys.stderr.write("❌  %s didn't generate any files!\n" % lang)
            sys.exit(1)

    print("✅  All implementations produce output!")

    filecmp.clear_cache()
    messages = (glob.glob(os.path.join(data_path, "*.msg")))
    for i in range(len(messages)):
        j = i + 1
        if j >= len(messages):
            j -= len(messages)
        if not filecmp.cmp(messages[i], messages[j], False):
            sys.stderr.write("❌  %s and %s are not equal.\n" % (messages[i], messages[j]))
            sys.exit(1)

    print("✅  Produced test files are all identical!")

    for lang in languages:
        os.chdir(os.path.join(base_path, "test", lang))
        status = subprocess.run(["make", "read"], capture_output=True)
        if not status.returncode == 0:
            sys.stderr.write(status.stderr.decode("utf-8"))
            sys.stderr.write("❌  %s failed to read its own input.\n" % lang)
            sys.exit(1)

    print("✅  Input functions check out!")

    print("\n🎉  All good!")
