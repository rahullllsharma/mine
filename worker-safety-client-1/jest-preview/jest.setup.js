import "@testing-library/jest-dom/extend-expect";
import { jestPreviewConfigure } from "jest-preview";

import "@/styles/globals.css";

jestPreviewConfigure({ autoPreview: true });
