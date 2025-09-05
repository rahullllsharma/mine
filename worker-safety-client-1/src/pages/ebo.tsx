import type { Ebo, EboId } from "@/api/codecs";
import type { Api, ApiError, ApiResult } from "@/api/api";
import type { Effect } from "@/utils/reducerWithEffect";
import type { Deferred } from "@/utils/deferred";
import type { Option } from "fp-ts/lib/Option";
import type { TaskEither } from "fp-ts/lib/TaskEither";
import type { NonEmptyString } from "io-ts-types";
import type { UserPermission } from "../types/auth/AuthUser";
import * as O from "fp-ts/lib/Option";
import * as E from "fp-ts/lib/Either";
import * as A from "fp-ts/lib/Array";
import { Eq as EqString } from "fp-ts/lib/string";
import * as TE from "fp-ts/lib/TaskEither";
import * as Tup from "fp-ts/lib/Tuple";
import { flow, pipe } from "fp-ts/lib/function";
import { useRouter } from "next/router";
import * as t from "io-ts";
import { signIn } from "next-auth/react";
import { useApi, showUserApiError } from "@/api/api";
import {
  useReducerWithEffects,
  effectOfAsync,
  noEffect,
  mapEffect,
} from "@/utils/reducerWithEffect";
import { eboIdCodec } from "@/api/codecs";
import { isResolved, Resolved, InProgress } from "@/utils/deferred";
import * as Wizard from "@/components/forms/Ebo/Wizard";
import * as Alert from "@/components/forms/Alert";
import Loader from "@/components/shared/loader/Loader";
import { useAuthStore } from "../store/auth/useAuthStore.store";
import { nonEmptyStringCodec } from "../utils/validation";

const initEboTask = (
  api: Api,
  eboId: Option<EboId>
): TaskEither<ApiError, Option<Ebo>> => {
  const r = pipe(
    eboId,
    O.fold(
      () => TE.of(O.none),
      id => pipe(id, api.ebo.getEbo, TE.map(O.some))
    )
  );

  return r;
};

type Model = {
  wizardModel: Deferred<ApiResult<Wizard.Model>>;
  alertModel: Alert.Model;
};

const init = (): Model => ({
  wizardModel: InProgress(),
  alertModel: Alert.init(),
});

type Action =
  | { type: "Initialized"; result: ApiResult<Option<Ebo>> }
  | { type: "WizardAction"; action: Wizard.Action }
  | { type: "AlertAction"; action: Alert.Action };

const Initialized = (result: ApiResult<Option<Ebo>>): Action => ({
  type: "Initialized",
  result,
});

const WizardAction = (action: Wizard.Action): Action => ({
  type: "WizardAction",
  action,
});

export const AlertAction = (action: Alert.Action): Action => ({
  type: "AlertAction",
  action,
});

const updateWizard =
  (api: Api) =>
  (model: Model) =>
  (
    wizardModel: Wizard.Model,
    action: Wizard.Action
  ): [Model, Effect<Action>] => {
    const [newWizardModel, wizardEffect] = Wizard.update(api)(
      wizardModel,
      action
    );

    switch (wizardEffect.type) {
      case "ComponentEffect":
        return [
          { ...model, wizardModel: Resolved(E.right(newWizardModel)) },
          mapEffect(WizardAction)(wizardEffect.effect),
        ];
      case "AlertAction":
        const [newAlertModel, alertEffect] = Alert.update(
          model.alertModel,
          wizardEffect.action
        );
        return [
          {
            ...model,
            wizardModel: Resolved(E.right(newWizardModel)),
            alertModel: newAlertModel,
          },
          mapEffect(AlertAction)(alertEffect),
        ];
      case "NoEffect":
        return [
          {
            ...model,
            wizardModel: Resolved(E.right(newWizardModel)),
          },
          noEffect,
        ];
    }
  };

const update =
  (api: Api) =>
  (model: Model, action: Action): [Model, Effect<Action>] => {
    switch (action.type) {
      case "Initialized":
        const initResult = pipe(action.result, E.map(Wizard.init));
        return [
          {
            ...model,
            wizardModel: pipe(initResult, E.map(Tup.fst), Resolved),
          },
          pipe(
            initResult,
            E.map(Tup.snd),
            E.fold(
              flow(
                showUserApiError,
                Alert.requestAlertEffect("error"),
                mapEffect(AlertAction)
              ),
              mapEffect(WizardAction)
            )
          ),
        ];
      case "WizardAction":
        if (
          isResolved(model.wizardModel) &&
          E.isRight(model.wizardModel.value)
        ) {
          return updateWizard(api)(model)(
            model.wizardModel.value.right,
            action.action
          );
        } else {
          return [{ ...model }, noEffect];
        }
      case "AlertAction":
        const [newAlertModel, alertEffect] = Alert.update(
          model.alertModel,
          action.action
        );
        return [
          { ...model, alertModel: newAlertModel },
          mapEffect(AlertAction)(alertEffect),
        ];
    }
  };

function EboWizardComponent({
  api,
  eboId,
  checkPermission,
  userId,
}: {
  api: Api;
  eboId: Option<EboId>;
  checkPermission: (permission: UserPermission) => boolean;
  userId: NonEmptyString;
}): JSX.Element {
  const [model, dispatch] = useReducerWithEffects(
    update(api),
    init(),
    effectOfAsync(initEboTask(api, eboId), Initialized)
  );

  if (isResolved(model.wizardModel)) {
    if (E.isRight(model.wizardModel.value)) {
      return (
        <>
          <Wizard.View
            model={model.wizardModel.value.right}
            dispatch={flow(WizardAction, dispatch)}
            checkPermission={checkPermission}
            userId={userId}
          />
          <Alert.View
            model={model.alertModel}
            dispatch={flow(AlertAction, dispatch)}
          />
        </>
      );
    } else {
      if (model.wizardModel.value.left.type === "RequestError") {
        signIn("keycloak", { redirect: true });
      }
      return (
        <div className="self-center">
          <Loader />
        </div>
      );
    }
  } else {
    return (
      <div className="self-center">
        <Loader />
      </div>
    );
  }
}

export default function EboWizardPage(): JSX.Element {
  const api = useApi();
  const router = useRouter();
  const { me } = useAuthStore();

  const eboId = pipe(eboIdCodec.decode(router.query.eboId), O.fromEither);

  return pipe(
    E.Do,
    E.bind("user", () =>
      pipe(
        me,
        t.type({
          id: t.string.pipe(nonEmptyStringCodec()),
          permissions: t.array(t.string.pipe(nonEmptyStringCodec())),
        }).decode,
        E.mapLeft(_ => `Failed to decode current user`)
      )
    ),
    E.fold(
      err => {
        if (err === "RequestError") {
          signIn("keycloak", { redirect: true });
        }
        return (
          <div className="self-center">
            <Loader />
          </div>
        );
      },
      ({ user }) => {
        const checkPermission = (permission: UserPermission) =>
          pipe(user.permissions, A.elem(EqString)(permission));
        return pipe(
          api,
          O.fold(
            () => <div>API not available</div>,
            a => (
              <EboWizardComponent
                api={a}
                eboId={eboId}
                checkPermission={checkPermission}
                userId={user.id}
              />
            )
          )
        );
      }
    )
  );
}
