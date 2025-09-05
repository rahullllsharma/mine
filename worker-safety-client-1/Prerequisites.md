# Topics to master

For the type-safe functional programming part of the codebase an understanding
of the following basic concepts is required.

This is intended to serve as a rough outline for the onboarding process. Not as
the comprehensive documentation.

- [ ] We might need to link some documentation and/or youtube links here that
      explains general concepts

## Function composition

Using `pipe` and `flow`

- [ ] We need a small explanation what is composition of functions, then give
      examples for pipe and flow.

## Partial application and currying

Representing functions with multiple arguments as "functions returning
functions"

- [ ] This can be merged within the context of the previous one.

- [ ] Definitely before starting explaining below contexts, we need to explain
      the meaning of itself, with keeping the types in context. Like itself can
      mean `string`, which is every possible string type. So then we can start
      explaining below items with only giving examples.

## Functor

Something that knows how to `map` over itself. Examples: `Array`, `Option`,
`Either`, `Task` etc.

## Monad

Something that knows how to `chain` it's computations (also known as `flatMap`
or `bind`). Examples: `Option`, `Either`, `Task`, `Array` etc.

## Do-notation

A syntactic sugar for `chain`ing computations. Helps to avoid nested `chain`
calls. Examples: `Option`, `Either`

## Applicative

Something that knows how to `apply` a curried function to it's arguments within
the context of the type. Examples: `Option`, `Either`, `Task`, `Array` etc.

## Semigroup

Something that knows how to `combine` itself with another instance of the same
type. Also known as `concat` or `append`.

## Monoid

Same as `Semigroup` but also has a `zero` or `empty` value.

## Foldable

Something that knows how to `fold` itself into a single value. Also known as
`reduce`.

## Alternative

Something that supports providing "fallback values" using `alt` function.
Examples `Option`, `Either`.

## Traversable

Provides `traverse` and `sequence` functions.

## Lens

Simplifies working with immutable data structures.

## Eq

Defining explicit equality logic for types.

## Ord

Defining explicit ordering logic for types.
