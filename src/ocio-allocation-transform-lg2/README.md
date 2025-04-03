# ocio-allocation-transform-lg2

A copy of the OCIO AllocationTransform algorithm as Nuke's Blink script.

The algorithm exclusively handle the case where the AllocationTransform is set
to `lg2`.

## pre-requisites

- tested on Nuke 16.0 non-commercial.

## usage

- Create a Blink script node in NUke
- Copy/paste the content of [ocio-allocation-transform-lg2.blink](ocio-allocation-transform-lg2.blink) inside.
- Click the `Recompile` button.

## issues

When the offset is 0.0 and the algorithm encounter a value that is 0.0, you will get 
an infinite value which is different from OCIO behavior which will return ~-6.