A custom bit-packing and unpacking code generator for C#, Go, and TypeScript. (Written in Python, naturally, because this project did not yet feature enough languages.)

Flatbuffers and their ilk are great, but the resulting data is a little bulky because of the vtables and support for changing schema while still being able to use old data. Because these messages only exist in flight and are never persisted, the client and server can stay in lockstep, so the bytestreams can be more compact. 

(Am I optimizing the wrong thing? Perhaps! But the code for creating and reading flatbuffers is also a little more cumbersome than I'd like.)

These also lose the benefit of being able to snag data out without fully deserializing, but in my use case (a) most messages are very small and (b) I basically *always* want *all* the data. If not, If either of those change, I'll reevaluate, and perhaps rue the day I decided to do my own thing and not use flatbuffers.

I'll be honest, though: it was kind of fun to write a code generator. 😝 It does its best to produce idiomatic code for each language, but probably won't win any awards from the linters. 
