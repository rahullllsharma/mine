import type { Task } from "fp-ts/lib/Task";
import type { Lens, Optional } from "monocle-ts";
import type { Dispatch } from "react";
import * as A from "fp-ts/Array";
import * as E from "fp-ts/Either";
import * as NEA from "fp-ts/NonEmptyArray";
import { constVoid, flow, identity, pipe } from "fp-ts/function";
import { useCallback, useEffect, useReducer } from "react";

// a base type definition for a child component that uses a reducer from the parent
export type ChildProps<M, A> = {
  model: M;
  dispatch: (action: A) => void;
};

// Lazy effect stored in a function `dispatch => void`. Executed when applied to a `dispatch` argument
export type Effect<A> = (dispatch: (action: A) => void) => void;

// eslint-disable-next-line @typescript-eslint/no-empty-function
export const noEffect: Effect<never> = _ => {};

/** Executes an async effect and dispatches an action based on the result of the async task when it completes
 * @param task an async task to perform
 * @param onSuccess a function that takes the result of the task and returns an action to dispatch
 */
export const effectOfAsync: <T, A>(
  task: Task<T>,
  onSuccess: (_: T) => A
) => Effect<A> = (task, onSuccess) => dispatch => {
  task().then(onSuccess).then(dispatch);
};

/**
 * Same as effectOfAsync, but ignores the result of the promise and does not dispatch an action
 * @param task
 * @returns
 */
export const effectOfAsync_: <T, A>(task: Task<T>) => Effect<A> =
  task => _dispatch => {
    task().then(constVoid);
  };

/**
 * Wraps a function as an effect
 * @param fn The function to wrap
 * @param args Arguments to pass to the function
 * @param onSuccess A function that takes the result of the function and returns an action to dispatch
 */
export const effectOfFunc = <T, P, A>(
  fn: (args: P) => T,
  args: P,
  onSuccess: (_: T) => A
): Effect<A> =>
  pipe(
    E.tryCatch(() => fn(args), identity),
    E.fold(
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      _ => _dispatch => {}, // do nothing if the function throws (todo: handle errors)
      result => dispatch => dispatch(onSuccess(result))
    )
  );

/**
 * Same as effectOfFunc, but ignores the result of the function and does not dispatch an action
 * @param fn The function to wrap
 * @param args Arguments to pass to the function
 */
export const effectOfFunc_ = <P, A>(
  fn: (args: P) => void,
  args: P
): Effect<A> =>
  pipe(
    E.tryCatch(() => fn(args), identity),
    E.fold(
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      _ => _dispatch => {}, // do nothing if the function throws (todo: handle errors)
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      _result => _dispatch => {}
    )
  );

/**
 * Wraps an action as an effect to dispatch synchronously
 * Note: Use with caution. Abusing this function could lead to infinite recursive actions dispatching. It's usually a better to reuse composed pure functions updating the model with multiple changes in a single action instead of dispatching recursive synchronous actions for each update.
 * @param action The action to dispatch
 */
export const effectOfAction: <A>(a: A) => Effect<A> = action => dispatch =>
  dispatch(action);

/** Combine multiple effects
 * @param effects an array of effects to combine
 */
export const effectsBatch: <A>(effects: Effect<A>[]) => Effect<A> =
  effects => dispatch =>
    effects.forEach(e => e(dispatch));

export const mapEffect: <A, B>(
  f: (a: A) => B
) => (effect: Effect<A>) => Effect<B> = f => effect => dispatch =>
  effect(flow(f, dispatch));

export const withEffect =
  <A>(effect: Effect<A>) =>
  <M>(model: M): [M, Effect<A>] =>
    [model, effect];

/**
 * Updates the child model
 * @param lens Lens pointing to the child model in the parent model
 * @param childActionCtor Child action constructor
 * @param childUpdate Child update function
 * @example // Abstracts this common pattern:
 *  const [childModel, childEffect] =
 *    childUpdate(model.childModel, childAction);
 *
 *  return [
 *    {...model, childModel},
 *    mapEffect(childActionCtor)(childEffect)
 *  ]
 * // into this:
 *   return updateChild(
 *      Lens.fromProp<Model>()('childModel'),
 *      childActionCtor,
 *      childUpdate
 *   )(model, childAction);
 *
 */
export const updateChildModelEffect =
  <M, A, CM, CA>(
    lens: Lens<M, CM>,
    childActionCtor: (ca: CA) => A,
    childUpdate: (childModel: CM, childAction: CA) => [CM, Effect<CA>]
  ) =>
  (model: M, childAction: CA): [M, Effect<A>] => {
    const [childModel, childEffect] = childUpdate(lens.get(model), childAction);

    return [
      lens.set(childModel)(model),
      mapEffect(childActionCtor)(childEffect),
    ];
  };

export const updateChildModel =
  <M, CM, CA>(
    lens: Lens<M, CM>,
    childUpdate: (childModel: CM, childAction: CA) => CM
  ) =>
  (model: M, childAction: CA): M =>
    lens.set(childUpdate(lens.get(model), childAction))(model);

export const updateOptionalChildModel =
  <M, CM, CA>(
    lens: Optional<M, CM>,
    childUpdate: (childModel: CM, childAction: CA) => CM
  ) =>
  (model: M, childAction: CA): M => {
    const upd = (cm: CM) => childUpdate(cm, childAction); // partially applied childUpdate

    return lens.modify(upd)(model);
  };

export const updateChildModelEffectWatch =
  <M, A, CM, CA>(
    lens: Lens<M, CM>,
    childActionCtor: (ca: CA) => A,
    childUpdate: (childModel: CM, childAction: CA) => [CM, Effect<CA>],
    watchChild: (model: M, childAction: CA) => [M, Effect<A>]
  ) =>
  (model: M, childAction: CA): [M, Effect<A>] => {
    const [newModel, effect] = updateChildModelEffect(
      lens,
      childActionCtor,
      childUpdate
    )(model, childAction);

    const [m1, e1] = watchChild(newModel, childAction);

    return [m1, effectsBatch([effect, e1])];
  };

type StateWithEffects<M, A> = { state: M; effects: Effect<A>[] };
type ActionWithEffects<A> =
  | {
      type: "EffectsExecuted";
    }
  | {
      type: "Action";
      action: A;
    };

/** A reducer that can produce side effects (like async actions or function calls)
 * It combines `useReducer` and `useEffect` to achieve this
 * @param reducerE the reducer function (update function) that combines the current state with an action
 * and returns a tuple of the next state and an effect
 * @param initState the initial state of the reducer
 * @param initEffect the initial effect to execute
 */
export function useReducerWithEffects<A, S>(
  reducerE: (state: S, action: A) => [S, Effect<A>],
  initState: S,
  initEffect: Effect<A>
): [S, Dispatch<A>] {
  const reducer = useCallback(
    (
      stateX: StateWithEffects<S, A>,
      actionX: ActionWithEffects<A>
    ): StateWithEffects<S, A> => {
      switch (actionX.type) {
        case "Action": {
          console.log(actionX.action);
          const [nextState, effect] = reducerE(stateX.state, actionX.action);
          return { state: nextState, effects: [...stateX.effects, effect] };
        }

        case "EffectsExecuted":
          return A.isNonEmpty(stateX.effects)
            ? {
                state: stateX.state,
                effects: NEA.tail(stateX.effects),
              }
            : stateX;
      }
    },
    [reducerE]
  );

  const [{ state, effects }, dispatch] = useReducer(reducer, {
    state: initState,
    effects: [initEffect],
  });

  useEffect(() => {
    if (A.isNonEmpty(effects)) {
      dispatch({ type: "EffectsExecuted" });
      NEA.head(effects)(a => dispatch({ type: "Action", action: a }));
    }
  }, [dispatch, effects]);

  const actionDispatch = useCallback(
    (a: A) => dispatch({ type: "Action", action: a }),
    [dispatch]
  );

  return [state, actionDispatch];
}
