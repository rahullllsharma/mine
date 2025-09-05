import type { EquipmentInformation } from "@/api/codecs";
import type { EwpEquipmentInformationInput } from "@/api/generated/types";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type * as t from "io-ts";
import type { StepSnapshot } from "../Utils";
import * as E from "fp-ts/lib/Either";
import { flow } from "fp-ts/lib/function";
import { InputRaw } from "../Basic/Input";

export type Model = {
  circuitBreaker: string;
  switch: string;
  transformer: string;
};

export function makeSnapshot(model: Model): StepSnapshot {
  return model;
}

export function initEmpty(): Model {
  return {
    circuitBreaker: "",
    switch: "",
    transformer: "",
  };
}

export function init(info: EquipmentInformation): Model {
  return {
    circuitBreaker: info.circuitBreaker.toString(),
    switch: info.switch.toString(),
    transformer: info.transformer.toString(),
  };
}

export function toEwpEquipmentInformationInput(
  model: Model
): t.Validation<EwpEquipmentInformationInput> {
  return E.right({
    circuitBreaker: model.circuitBreaker,
    switch: model.switch,
    transformer: model.transformer,
  });
}

export type Action =
  | {
      type: "CircuitBreakerChanged";
      value: string;
    }
  | {
      type: "SwitchChanged";
      value: string;
    }
  | {
      type: "TransformerChanged";
      value: string;
    };

export const CircuitBreakerChanged = (value: string): Action => ({
  type: "CircuitBreakerChanged",
  value,
});

export const SwitchChanged = (value: string): Action => ({
  type: "SwitchChanged",
  value,
});

export const TransformerChanged = (value: string): Action => ({
  type: "TransformerChanged",
  value,
});

export function update(model: Model, action: Action): Model {
  switch (action.type) {
    case "CircuitBreakerChanged":
      return {
        ...model,
        circuitBreaker: action.value,
      };
    case "SwitchChanged":
      return {
        ...model,
        switch: action.value,
      };
    case "TransformerChanged":
      return {
        ...model,
        transformer: action.value,
      };
  }
}

export type Props = ChildProps<Model, Action> & {
  isReadOnly?: boolean;
};
export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;
  return (
    <>
      <InputRaw
        label="Circuit Breaker #"
        value={model.circuitBreaker}
        disabled={isReadOnly}
        onChange={flow(CircuitBreakerChanged, dispatch)}
      />
      <InputRaw
        label="Switch #"
        value={model.switch}
        disabled={isReadOnly}
        onChange={flow(SwitchChanged, dispatch)}
      />
      <InputRaw
        label="Transformer # *"
        value={model.transformer}
        disabled={isReadOnly}
        onChange={flow(TransformerChanged, dispatch)}
      />
    </>
  );
}
