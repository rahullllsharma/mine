import type { JsbId, ProjectLocationId } from "@/api/codecs";
import type { Api, ApiError, ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type { Effect } from "@/utils/reducerWithEffect";
import type { Option } from "fp-ts/lib/Option";
import type { TaskEither } from "fp-ts/lib/TaskEither";
import type { ValidDateTime } from "@/utils/validation";
import type { UserPermission } from "@/types/auth/AuthUser";
import { DateTime } from "luxon";
import { none } from "fp-ts/Option";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import * as TE from "fp-ts/lib/TaskEither";
import * as T from "fp-ts/lib/Task";
import * as Tup from "fp-ts/lib/Tuple";
import { flow, pipe } from "fp-ts/lib/function";
import { useRouter } from "next/router";
import * as A from "fp-ts/lib/Array";
import { Eq as EqString } from "fp-ts/lib/string";
import * as t from "io-ts";
import { signIn } from "next-auth/react";
import {
  effectOfAsync,
  mapEffect,
  noEffect,
  useReducerWithEffects,
} from "@/utils/reducerWithEffect";
import { InProgress, Resolved, isResolved } from "@/utils/deferred";
import * as Wizard from "@/components/forms/Jsb/Wizard";
import { DecodeError, showApiError, useApi } from "@/api/api";
import { jsbIdCodec, projectLocationIdCodec } from "@/api/codecs";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import * as Alert from "@/components/forms/Alert";
import { nonEmptyStringCodec, validDateTimeCodec } from "@/utils/validation";
import Loader from "@/components/shared/loader/Loader";
import { useAuthStore } from "@/store/auth/useAuthStore.store";

const initJsbTask = (
  api: Api,
  projectLocationId: Option<ProjectLocationId>,
  jsbId: Option<JsbId> // jsbId is None when initializing new JSB
): TaskEither<ApiError, Wizard.InitData> => {
  const getProjectLocation = (dt: ValidDateTime) =>
    pipe(
      projectLocationId,
      O.fold(
        () => TE.of(none), // when initializing without project location, succeed with None
        id => pipe(api.jsb.getProjectLocation(dt)(id))
      )
    );
  return pipe(
    TE.Do,
    TE.bind("jsbData", () => {
      return pipe(
        jsbId,
        O.fold(
          () => TE.of(O.none),
          id => pipe(api.jsb.getJsb(id), TE.map(O.some))
        )
      );
    }),
    TE.bind("dateTime", ({ jsbData }) => {
      return pipe(
        jsbData,
        O.chain(jsbValue => jsbValue.contents.jsbMetadata),
        O.fold(
          () =>
            pipe(
              T.fromIO(() => DateTime.local()),
              T.map(flow(validDateTimeCodec.decode, E.mapLeft(DecodeError)))
            ),
          meta => TE.of(meta.briefingDateTime)
        )
      );
    }),
    TE.bind("projectLocation", ({ dateTime }) => getProjectLocation(dateTime)),
    TE.bind("lastJsb", () => api.jsb.getLastJsb(projectLocationId)),
    TE.bind("lastAdhocJsb", () => api.jsb.getLastAdhocJsb())
  );
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
  | {
      type: "Initialized";
      result: ApiResult<Wizard.InitData>;
    }
  | {
      type: "WizardAction";
      action: Wizard.Action;
    }
  | {
      type: "AlertAction";
      action: Alert.Action;
    };

const Initialized = (result: ApiResult<Wizard.InitData>): Action => ({
  type: "Initialized",
  result,
});
const WizardAction = (action: Wizard.Action): Action => ({
  type: "WizardAction",
  action,
});
const AlertAction = (action: Alert.Action): Action => ({
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
          { ...model, wizardModel: Resolved(E.right(newWizardModel)) },
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
                showApiError,
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
          return [model, noEffect];
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

function WizardComponent({
  api,
  projectLocationId,
  jsbId,
  workPackageLabel,
}: {
  api: Api;
  projectLocationId: Option<ProjectLocationId>;
  jsbId: Option<JsbId>;
  workPackageLabel: string;
}): JSX.Element {
  const [model, dispatch] = useReducerWithEffects(
    update(api),
    init(),
    effectOfAsync(initJsbTask(api, projectLocationId, jsbId), Initialized)
  );

  const { me } = useAuthStore();

  if (isResolved(model.wizardModel)) {
    const wizardModelValue = model.wizardModel.value;
    return pipe(
      E.Do,
      E.bind("wizardModel", () =>
        pipe(
          wizardModelValue,
          E.mapLeft(e => e.type)
        )
      ),
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
        ({ wizardModel, user }) => {
          const checkPermission = (permission: UserPermission) =>
            pipe(user.permissions, A.elem(EqString)(permission));
          return (
            <>
              <Wizard.View
                projectLocationId={projectLocationId}
                model={wizardModel}
                dispatch={flow(WizardAction, dispatch)}
                workPackageLabel={workPackageLabel}
                checkPermission={checkPermission}
                userId={user.id}
              />
              <Alert.View
                model={model.alertModel}
                dispatch={flow(AlertAction, dispatch)}
              />
            </>
          );
        }
      )
    );
  } else {
    return (
      <div className="self-center">
        <Loader />
      </div>
    );
  }
}

export default function WizardPage(): JSX.Element {
  const api = useApi();
  const router = useRouter();
  const { workPackage } = useTenantStore(state => state.getAllEntities());

  const projectLocationId = pipe(
    projectLocationIdCodec.decode(router.query.locationId),
    O.fromEither
  );

  const jsbId = pipe(jsbIdCodec.decode(router.query.jsbId), O.fromEither);

  return pipe(
    api,
    O.fold(
      () => <div>API not available</div>,
      a => (
        <WizardComponent
          api={a}
          projectLocationId={projectLocationId}
          jsbId={jsbId}
          workPackageLabel={workPackage.label}
        />
      )
    )
  );
}
