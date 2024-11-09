# Using Beschi with C

(You can see [an example C file](../generated_examples/c_example.h) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/c/).)


## Data Types

The base data types map to C accordingly: 

| Protocol Type | C type     |
|---------------|------------|
| `byte`        | `uint8_t`  |
| `bool`        | `bool`     |
| `int16`       | `uint16_t` |
| `uint16`      | `int16_t`  |
| `int32`       | `uint32_t` |
| `uint32`      | `int32_t`  |
| `int64`       | `uint64_t` |
| `uint64`      | `int64_t`  |
| `float`       | `float`    |
| `double`      | `double`   |
| `string`      | `char*`    |

Note that this requires the `stdint.h` and `stdbool.h` header files, which are standard for C99. 


## Caveats

* Unsurprisingly, C code that uses Beschi messages tends to be much more verbose than code from more modern languages. The syntax is a bit different, too, because of the lack of multiple return values and exceptions in C. 
    - Nearly all functions require you to pass in pointers to your objects, and return a `{namespace}_err_t` that you should check is equal to `{NAMESPACE}_ERR_OK` before you use those objects. 
    - Take a look at the test harnesses to see how it works, in general. 
* As always, C makes it far easier to mess things up if you don't pay close attention. Feed the wrong kind of data to a function and it will *try* to recover gracefully and return an error, but it's also just as likely that you'll crash. 
* There are a lot of variants of C, and the generated code is not tested across all of them. It makes the following assumptions:
    - A C99 compiler (makes use of variable declaration in loops and designated initializers)
    - IEEE-754 floating point numbers (a pretty safe assumption, but if you're running on some exotic hardware, this might fail)
    - Little-endian processor (a less safe assumption, but in general is ok; would like to fix this at some point anyway)
* The generated code tries to be as straightforward as possible, avoiding macros and unnecessary terseness, so it shouldn't be terribly hard to debug if there's a problem with it.
* C doesn't support any kind of namespacing other than prefixing functions/structs/variables with a string, so that's what the generated code does. You may want to use a shorter namespace string if you're planning to use C code, so as to save some horizontal space in your code editor. 
* The code generated is an [STB-style](https://github.com/nothings/stb/) single-file header library. If you've never used one before, it's actually pretty simple. You `#include "MyGeneratedFile.h"` wherever you need to use the structures and functions, like you normally would with a library. But instead of having a separate file to compile, all the implementation is in the same file, just behind a definition guard. So to actually link the implementation code, in **exactly** one file, `#define {NAMESPACE}_IMPLEMENTATION` **before** you include it. 
* The layout of the structs (mostly) mirrors the way they are declared in the protocol file, which may raise warnings about padding if you compile with warnings all the way up. If memory alignment is important to you, you may want to play with the declaration order. 
    - Exceptions are: 
        - Every message struct has an additional byte (`_mt`) at the start, used to identify it if its in a `void**` array. 
        - Every string and list have an associated `{varname}_len` variable storing their length, right before them in the array. 
        - Lists of strings have a second variable of `{varname}_els_len` recording the lengths of each element in the array. 
        - You probably shouldn't declare members in the protocol that would shadow these variables, but I'm not the boss of you. 
* With the various length variables: they will be set properly when reading a message out of a buffer, but ***you are responsible*** for making sure they are correct before they go into a buffer. C has no way to track the length of arrays (without introducing another dependency), so it's up to you. 
* The calculated length for strings should *not* include the null terminator. 
* When declaring an instance of a message, it's probably best to use the generated constant `{namespace}_{message_name}_default` to make sure that its members are initialized and that its identifying byte is set correctly. Otherwise things might break. 
* Reading a message from a buffer copies all the data it needs, so the buffer can be discarded safely afterwards. This *does* mean, though, that the reading functions will allocate memory if there are lists or strings in the structure. They will need to be `free`-ed or will leak. 
    - Every message struct has an associated `{namespace}_Destroy{message_type}` function that handles that for you. 
* `ProcessRawBytes` fills an array of pointers to `void` (`void**`), so you need to pass it a *pointer* to such an array, a `void***`. I know, I know. Anyway, once it's filled, you can check each one for its type with `{namespace}_GetMessageType` and then cast as you need to. 
    - Note that each of the messages in the resulting list has been allocated, so will need to be freed. (Probably best to use their aforementioned `_Destroy` functions.)
    - There is also a `{namespace}_DestroyMessageList` to help with cleaning that up the whole list if you want to do it that way.
