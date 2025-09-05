// until we generate codecs directly from graphql schema,
// we need to check that codec types at least have correct keys
// example: type Check = CheckKeys<Entity, EntityDto>;
// where Entity is a type from codec and EntityDto is a type generated from graphql schema
// it will cause a compilation error if Entity has keys that are missing from the generated EntityDto type
export type CheckKeys<_T1 extends _T2, _T2> = never;
