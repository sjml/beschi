# Making a New Beschi Writer

## Prep

Sync this repository, and then install it locally with development packages. 

```
pip install -e '.[dev]'
```

This will let you run the test suite as well as put `beschi` on your path. 


## How-To

The [existing writers](../../beschi/writers/) should serve as good starting points. It's not especially clever code, which means it's pretty amenable to just copy-pasting an existing writer that is similar to your language and changing the strings it outputs. 

Having made a bunch of these, my way of proceeding is thus:
1. Run the test suite so you have a bunch of premade messages in the `out/data` directory to use as your examples to read. (`pytest`)
2. In the target language, write a program by hand which reads in one of the broken.*.msg files. That file contains just two `float`s, for a total of 8 bytes. Figure out the best way to parse that into a Vec2 structure native to the language. 
3. Do whatever cleanup work needs to be done to make that system more scalable. 
4. Add more types to the reading system. (Floats are generally among the trickiest, so you should be well on your way.)
5. Keep adding types until you can read the first part of one of the `basic.*.msg` files (which come from the [`example.toml` protocol](../../test/_protocols/example.toml)). You should be able to get up to the part where there are lists. 
6. Decided how best to translate the concept of "list" into your target language. In general I prefer to go with structures that are resizeable, if they exist. 
7. At this point it should be clear how to do the rest of the reading in the target language. 
8. THEN flip it around and start figuring out how to write. 

You could proceed to do an entire writer in your handwritten implementation, but this is usually the point at which I start building the generator. 

For testing:
* Running `pytest` from the root directory will run the full test suite. (`pytest -x` to stop at the first failure.)
* Note that you can set a class variable of `in_progress = True` on the builder so it will be skipped by default (unless you pass `--experimental` to pytest). 
* You can also pass `--only {my_new_language}` to pytest so it will skip the other languages and save you time. This will need to be combined with `--experimental` if you have set it as `in_progress`. 


## Generation Priorities

Making automatically generated code is a tradeoff, and with Beschi I'm actively trying to get the code as close as possible to best practices in the target language, so there's even more tradeoffs than normal.

So, the priorities go as follows:

1. Creating code that compiles with no warnings in target language. 
    - thus, all data members are renamed to snake_case when generating Rust code. (Suppressible with `--rust-no-rename`)
2. Creating code that works as expected in target language. 
    - thus, all data members are renamed to Uppercase when generating Go code to ensure that they are accessible to client code. (Suppressible with `--go-no-rename`)
3. THEN principle of least surprise. 
    - thus, data members are **not** renamed to UpperCamelCase in C#, even though it is a strong convention there, because not following the convention does not trigger any warnings or have any semantic differences.


## Admonitions

* All numbers are read and written as little-endian.
* Text is encoded as UTF-8. 
* When calculating the length of the string, make sure you are counting **bytes**, not characters. 
* The string data should **not** include a null terminator and the calculated length should also not count it.
* Feel free to ask for help. 😊
