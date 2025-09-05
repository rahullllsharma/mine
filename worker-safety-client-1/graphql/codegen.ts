import type { CodegenConfig } from "@graphql-codegen/cli";

const { access_token } = JSON.parse(process.env.GRAPHQL_AUTH_RESPONSE || "{}");

if (!access_token) {
  console.error("Failed to get access token");
}

const config: CodegenConfig = {
  schema: [
    {
      "http://localhost:8001/graphql": {
        headers: {
          Authorization: `Bearer ${access_token}` || "",
        },
      },
    },
  ],
  documents: ["./graphql/**/*.gql", "./graphql/**/*.graphql"],
  generates: {
    "src/api/generated/types.ts": {
      plugins: [
        "typescript",
        "typescript-operations",
        "typescript-graphql-request",
      ],
    },
  },
};
export default config;
