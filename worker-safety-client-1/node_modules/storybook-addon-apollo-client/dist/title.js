"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getTitle = void 0;
var api_1 = require("@storybook/api");
var constants_1 = require("./constants");
function getTitle() {
    var _a;
    // eslint-disable-next-line react-hooks/rules-of-hooks
    var params = (0, api_1.useParameter)(constants_1.PARAM_KEY);
    return ((_a = params === null || params === void 0 ? void 0 : params.mocks) === null || _a === void 0 ? void 0 : _a.length)
        ? "Apollo Client (".concat(params.mocks.length, ")")
        : 'Apollo Client (0)';
}
exports.getTitle = getTitle;
//# sourceMappingURL=title.js.map