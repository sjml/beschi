* abstractify a bit so it's less wl()-y? can we use templates? 
* go -> golang?
* make the basic types built-in
    - int/uint64?
* think about how better to do the polymorphism on the typescript side 
    - TS doesn't really do it naturally... return a type along with the message? 
* check to make sure that the string encoding is properly counting bytes, not glyphs/characters/whatever
* testing framework
    - network read/write in each language? yikes.
        - Golang <-> TypeScript
        - Python <-> C#
        - C <-> C
        - Swift <-> Rust
    - matrix of read/writes -- every language writes, every language reads all the written messages
    - is there some way to test it with little-endian architecture too so we can be sure it's consistent?
* python writer
* C writer
* swift writer?
* rust writer? ugh
* command-line flags to generate different languages
    - command-line flag for ignoring messages? (regex match?)
* generic example protocol
* indentation as a flag?
* smarter encoding of message type flags so it expands automatically as needed? (if there's more than 255?)


* redo readme
    - justification
        - this a custom bit-packing and unpacking code generator for C#, Go, TypeScript, and Python. 
        - cap'n proto and flatbuffers are great, but have functionality I wasn't using and add some overhead as a result
        - it was kind of fun to write a code generator 😝
    - handles: 
        - protocol definition
        - creation of code in target languages for writing and reading messages <-> sequences of bytes
    - does not handle: 
        - error handling / verification of messages; it would not be too hard to create a checksum message type and do the verifications one level up
        - partial deserialization; for the use case that inspired this library, (a) most messages are very small and (b) I basically *always* want *all* the data. If either of those two things change, I'll re-evaluate the capabilities of this, but honestly, would probably just move to flatbuffers at that point.
        - actual network communication; you have to get the bytes from somewhere and send them somewhere yourself (basic example code is availabe in each language in the example directory)
        - versionining of messages; this is meant for situations where the client and server evolve in lockstep and messages only exist in-flight. if there's any chance these are going to be persisted and have to handle versioning, you're better off using flatbuffers or Cap'n Proto or something like that. 
    - the existing generators are not terribly clever; there's no AST or interesting data structures happening. it just iterates over the structures and writes out code to serialize/deserialize
    - NB: each generator produces valid code in each of the languages, but it may not be the most prettily formatted. If you have strong opinions on that sort of thing, you should run it through a code formatter after it generates. 
