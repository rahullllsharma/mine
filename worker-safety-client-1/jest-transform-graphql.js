// eslint-disable-next-line @typescript-eslint/no-var-requires
const loader = require("graphql-tag/loader");

module.exports = {
  process(src) {
    // call directly the webpack loader with a mocked context
    // as graphql-tag/loader leverages `this.cacheable()`
    // return loader.call({ cacheable() {} }, src);
    //
    return {
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      code: loader.call({ cacheable() {} }, src),
    };
  },
};
