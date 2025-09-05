"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.managerEntries = exports.config = void 0;
var tslib_1 = require("tslib");
function config(entry) {
    if (entry === void 0) { entry = []; }
    return (0, tslib_1.__spreadArray)((0, tslib_1.__spreadArray)([], entry, true), [
        require.resolve('./preset/addDecorator')
    ], false);
}
exports.config = config;
function managerEntries(entry) {
    if (entry === void 0) { entry = []; }
    return (0, tslib_1.__spreadArray)((0, tslib_1.__spreadArray)([], entry, true), [
        require.resolve('./preset/register')
    ], false);
}
exports.managerEntries = managerEntries;
//# sourceMappingURL=preset.js.map