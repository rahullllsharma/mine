import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { IconName } from "@urbint/silica";
import { Transition } from "@headlessui/react";
import { nanoid } from "nanoid";
import { constant, flow, pipe } from "fp-ts/lib/function";
import * as O from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import { useCallback } from "react";
import { effectOfAsync, noEffect } from "@/utils/reducerWithEffect";

export type AlertType = "success" | "warning" | "info" | "error";
const timeoutDelay = 4000;

export type Alert = {
  alertType: AlertType;
  message: string;
};

const alertIcon = (alertType: AlertType): IconName => {
  switch (alertType) {
    case "success":
      return "circle_check";
    case "warning":
      return "warning";
    case "info":
      return "info_circle";
    case "error":
      return "error";
  }
};

type AlertItem = {
  alertType: AlertType;
  message: string;
  id: string;
};

const alertItem =
  (alertType: AlertType, message: string) =>
  (id: string): AlertItem => ({
    alertType,
    message,
    id,
  });

export type Model = {
  items: AlertItem[];
};

export function init(): Model {
  return {
    items: [],
  };
}

export type Action =
  | { type: "AlertRequested"; alertType: AlertType; message: string }
  | { type: "AlertAdded"; item: AlertItem }
  | { type: "AlertRemoved"; id: string };

export const AlertRequested =
  (alertType: AlertType) =>
  (message: string): Action => ({
    type: "AlertRequested",
    alertType,
    message,
  });

export const AlertAdded = (item: AlertItem): Action => ({
  type: "AlertAdded",
  item,
});

export const AlertRemoved = (id: string): Action => ({
  type: "AlertRemoved",
  id,
});

export const requestAlertEffect = (alertType: AlertType) => (message: string) =>
  effectOfAsync(
    () => Promise.resolve(nanoid()),
    flow(alertItem(alertType, message), AlertAdded)
  );

export const update = (
  model: Model,
  action: Action
): [Model, Effect<Action>] => {
  switch (action.type) {
    case "AlertRequested":
      return [model, requestAlertEffect(action.alertType)(action.message)];

    case "AlertAdded":
      const delayTask = pipe(
        () =>
          new Promise<string>(resolve =>
            setTimeout(() => resolve(action.item.id), timeoutDelay)
          )
      );

      return [
        {
          ...model,
          items: [...model.items, action.item],
        },
        effectOfAsync(delayTask, AlertRemoved),
      ];

    case "AlertRemoved":
      const index = pipe(
        model.items,
        A.findIndex(item => item.id === action.id)
      );
      return [
        pipe(
          index,
          O.chain(i => A.deleteAt(i)(model.items)),
          O.fold(
            () => model,
            otherItems => ({ ...model, items: otherItems })
          )
        ),
        noEffect,
      ];
  }
};

export type Props = ChildProps<Model, Action>;

export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;

  const hasItem = useCallback(
    (id: string) =>
      pipe(
        model.items,
        A.findFirst(item => item.id === id),
        O.isSome
      ),
    [model.items]
  );

  return (
    <div className="fixed top-16 w-fit px-4 left-2/4 -translate-x-1/2 z-50 flex flex-col items-center">
      {model.items.map(item => (
        <div key={item.id} className="mb-2 last:mb-0">
          <Transition
            appear
            show={hasItem(item.id)}
            enter="transition-opacity duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <ItemView
              item={item}
              onDismiss={flow(constant(item.id), AlertRemoved, dispatch)}
            />
          </Transition>
        </div>
      ))}
    </div>
  );
}

type ItemViewProps = {
  item: AlertItem;
  onDismiss: () => void;
};

function ItemView({ item, onDismiss }: ItemViewProps): JSX.Element {
  const backgroundStyles = cx({
    ["bg-system-error-40"]: item.alertType === "error",
    ["bg-system-warning-40"]: item.alertType === "warning",
    ["bg-system-info-40"]: item.alertType === "info",
    ["bg-system-success-40"]: item.alertType === "success",
  });

  const icon = alertIcon(item.alertType);

  return (
    <button
      className="px-3 py-2 bg-brand-urbint-60 inline-flex items-center rounded shadow-30"
      onClick={onDismiss}
    >
      <div
        className={cx(
          "mr-2 w-6 h-6 rounded flex items-center justify-center flex-shrink-0",
          backgroundStyles
        )}
      >
        <Icon name={icon} className="text-lg text-white" />
      </div>
      <p className="text-neutral-light-100 text-base text-left">
        {item.message}
      </p>
    </button>
  );
}
