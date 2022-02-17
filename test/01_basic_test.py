import beschi.writers


# will assert if a writer doesn't exist
# or is missing its namesake class or LANGUAGE_NAME
def test_list_writers():
    for _, writer in beschi.writers.all_writers.items():
        assert(beschi.writer.Writer in writer.__bases__)

