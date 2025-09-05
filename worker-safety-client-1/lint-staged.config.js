module.exports = {
  "*.{ts,tsx}": "/bin/sh ./scripts/check-types.sh",
  "*.{js,jsx,ts,tsx,json,md,mdx,css,scss}": "prettier --write",
  "*.{js,ts,tsx,json}": "yarn lint:fix",
  "*.{js,jsx,ts,tsx}": "yarn test:unit:changed --passWithNoTests",
};
