"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WithNextRouter = void 0;
var tslib_1 = require("tslib");
var jsx_runtime_1 = require("react/jsx-runtime");
var router_1 = (0, tslib_1.__importDefault)(require("next/router"));
var addon_actions_1 = require("@storybook/addon-actions");
var WithNextRouter = function (Story, context) {
    var _a, _b;
    var _c = (_a = context.parameters.nextRouter) !== null && _a !== void 0 ? _a : {}, Provider = _c.Provider, parameters = (0, tslib_1.__rest)(_c, ["Provider"]);
    if (Provider === undefined)
        throw new Error('NextContext.Provider is undefined, please add it to parameters.nextRouter.Provider');
    router_1.default.router = (0, tslib_1.__assign)({ locale: (_b = context === null || context === void 0 ? void 0 : context.globals) === null || _b === void 0 ? void 0 : _b.locale, route: '/', pathname: '/', query: {}, asPath: '/', push: function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (0, addon_actions_1.action)('nextRouter.push').apply(void 0, args);
            return Promise.resolve(true);
        }, replace: function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (0, addon_actions_1.action)('nextRouter.replace').apply(void 0, args);
            return Promise.resolve(true);
        }, reload: function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (0, addon_actions_1.action)('nextRouter.reload').apply(void 0, args);
        }, back: function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (0, addon_actions_1.action)('nextRouter.back').apply(void 0, args);
        }, prefetch: function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (0, addon_actions_1.action)('nextRouter.prefetch').apply(void 0, args);
            return Promise.resolve();
        }, beforePopState: function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (0, addon_actions_1.action)('nextRouter.beforePopState').apply(void 0, args);
        }, events: {
            on: function () {
                var args = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    args[_i] = arguments[_i];
                }
                (0, addon_actions_1.action)('nextRouter.events.on').apply(void 0, args);
            },
            off: function () {
                var args = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    args[_i] = arguments[_i];
                }
                (0, addon_actions_1.action)('nextRouter.events.off').apply(void 0, args);
            },
            emit: function () {
                var args = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    args[_i] = arguments[_i];
                }
                (0, addon_actions_1.action)('nextRouter.events.emit').apply(void 0, args);
            },
        }, isFallback: false }, parameters);
    return ((0, jsx_runtime_1.jsx)(Provider, (0, tslib_1.__assign)({ value: router_1.default.router }, { children: (0, jsx_runtime_1.jsx)(Story, {}, void 0) }), void 0));
};
exports.WithNextRouter = WithNextRouter;
//# sourceMappingURL=decorators.js.map