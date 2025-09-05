import type { AttributeSubmittedValues } from "@/container/admin/tenantAttributes/attributeEdit/AttributeEdit";
import type { TenantEntityMap } from "@/store/tenant/types";
import type {
  EntityAttributeKey,
  EntityAttributes,
  EntityKey,
  TenantEntity,
} from "@/types/tenant/TenantEntities";
import type { FormInputs, SelectedField } from "./types";
import type { AttributeConfiguration } from "@/api/generated/types";
import { useMutation } from "@apollo/client";
import { useContext, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { AttributeSection } from "@/components/tenantAttributes/attributeSection/AttributeSection";
import { AttributesTable } from "@/components/tenantAttributes/attributesTable/AttributesTable";
import { AttributeEdit } from "@/container/admin/tenantAttributes/attributeEdit/AttributeEdit";
import ConfigureTenant from "@/graphql/queries/configureTenant.gql";
import Permissions from "@/graphql/queries/permissions.gql";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

function TenantAttributes(): JSX.Element {
  const { tenant, getAllEntities, setTenant } = useTenantStore();
  const [openModal, setOpenModal] = useState(false);
  const [selectedField, setSelectedField] = useState<SelectedField>({
    entityKey: "",
    label: "",
  });
  const toastCtx = useContext(ToastContext);

  const entitiesObject = getAllEntities();

  const [configureTenant, { loading: isLoading }] = useMutation(
    ConfigureTenant,
    {
      refetchQueries: [{ query: Permissions }],
      onCompleted: data => {
        const cleanResponse = {
          ...data.configureTenant,
          attributes: data.configureTenant.attributes.map(
            (attr: AttributeConfiguration) => {
              const { __typename, ...cleanAttr } = attr;
              return cleanAttr;
            }
          ),
        };

        const updatedTenant = {
          ...tenant,
          entities: tenant.entities.map((entity: TenantEntity) =>
            entity.key === cleanResponse.key
              ? {
                  ...entity,
                  label: cleanResponse.label,
                  labelPlural: cleanResponse.labelPlural,
                  attributes: cleanResponse.attributes.map(
                    (attr: Partial<EntityAttributes>) => ({
                      ...attr,
                      mandatory: attr.mandatory ?? false,
                      filterable: attr.filterable ?? false,
                      mappings: attr.mappings ?? null,
                    })
                  ),
                }
              : entity
          ),
        };
        setTenant(updatedTenant);

        toastCtx?.pushToast("success", "Configuration saved");
        closeModal();
      },
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          `Error updating entity ${selectedField.label}.`
        );
        closeModal();
      },
    }
  );

  const methods = useForm<FormInputs>({
    mode: "onBlur",
    reValidateMode: "onBlur",
    defaultValues: {
      label: "",
      labelPlural: "",
      mandatory: false,
      options: [
        {
          key: "visible",
          value: true,
          isDisabled: false,
        },
        {
          key: "required",
          value: true,
          isDisabled: false,
        },
      ],
    },
  });

  const modalSetupHandler = (
    values: TenantEntityMap | EntityAttributes,
    entityKey?: EntityKey,
    attributeKey?: EntityAttributeKey
  ) => {
    methods.reset();

    setSelectedField({
      entityKey,
      attributeKey,
      label: values.defaultLabel,
    });

    const { mappings, mandatory, visible, required } =
      values as EntityAttributes;

    methods.reset({
      label: values.label ?? "",
      labelPlural: values.labelPlural ?? "",
      mandatory,
      options: [
        {
          key: "visible",
          value: mandatory || visible,
          isDisabled: false,
        },
        {
          key: "required",
          value: mandatory || (visible && required),
          isDisabled: !visible,
        },
      ],
      ...(mappings ? { mappings } : undefined),
    });
    setOpenModal(true);
  };

  const editClickHandler = (
    entityKey: EntityKey,
    attributeKey?: EntityAttributeKey
  ) => {
    const entityInfo = entitiesObject[entityKey];

    /**
     * Check if it's an entity modal
     */
    if (!attributeKey) {
      modalSetupHandler(entityInfo, entityKey);
      return;
    }

    /**
     * This will be an entity attribute modal
     */
    const attributeInfo = entityInfo.attributes[attributeKey];
    modalSetupHandler(attributeInfo, entityKey, attributeInfo.key);
  };

  const closeModal = () => {
    setOpenModal(false);
    setSelectedField({
      entityKey: "",
      label: "",
    });

    methods.reset({
      label: "",
      labelPlural: "",
      mandatory: false,
      options: [
        {
          key: "visible",
          value: true,
          isDisabled: false,
        },
        {
          key: "required",
          value: true,
          isDisabled: false,
        },
      ],
    });
    methods.clearErrors();
  };

  const onFormSubmit = (data: AttributeSubmittedValues) => {
    const entityInfo = tenant.entities.find(
      ({ key }) => key === selectedField.entityKey
    );

    if (!entityInfo) {
      toastCtx?.pushToast(
        "error",
        `Error updating entity ${selectedField.label}.`
      );
      return;
    }

    const options = data.options?.reduce(
      (acc, { key, value }) => ({ ...acc, [key]: value }),
      {}
    );

    /**
     * We have to send the whole entity object information to the BE
     * without the default fields:
     * - defaultLabel
     * - defaultLabelPlural
     * - mandatory
     */
    const tenantAttributesUpdated = {
      key: entityInfo.key,
      /**
       * if selectedField.attributeKey is defined then it means that we are editing the
       * attributes and not the entity
       */
      label: selectedField.attributeKey ? entityInfo.label : data.label,
      labelPlural: selectedField.attributeKey
        ? entityInfo.labelPlural
        : data.labelPlural,
      attributes: entityInfo.attributes.map(
        ({
          key,
          label,
          labelPlural,
          defaultLabel: _defaultLabel,
          defaultLabelPlural: _defaultLabelPlural,
          mandatory: _mandatory,
          mappings,
          visible,
          required,
          ...attributeProps
        }) => {
          const defaultOptions = { visible, required };
          const isSelectedAttribute = key === selectedField.attributeKey;
          const props = isSelectedAttribute
            ? {
                label: data.label,
                labelPlural: data.labelPlural,
                mappings: data.mappings,
                ...options,
              }
            : {
                label,
                labelPlural,
                mappings,
                ...defaultOptions,
              };

          return {
            ...attributeProps,
            key,
            ...props,
          };
        }
      ),
    };

    configureTenant({
      variables: {
        tenantAttributes: tenantAttributesUpdated,
      },
    });
  };

  return (
    <div className="h-screen overflow-y-auto">
      <header className="text-neutral-shade-100">
        <h2 className="text-xl font-semibold">Tenant Attributes</h2>
        <p className="text-base">
          Configure baseline attributes for your organizations
        </p>
        <section className="mt-2">
          <ul>
            {tenant.entities.map(({ key, label, defaultLabel, attributes }) => (
              <li key={key} className="mb-2">
                <AttributeSection
                  label={label}
                  defaultLabel={defaultLabel}
                  onEditClick={() => {
                    editClickHandler(key);
                  }}
                >
                  {attributes.length > 0 && (
                    <AttributesTable
                      data={attributes}
                      onEdit={attributeKey => {
                        editClickHandler(key, attributeKey);
                      }}
                    />
                  )}
                </AttributeSection>
              </li>
            ))}
          </ul>
        </section>
      </header>
      <Modal
        isOpen={openModal}
        closeModal={closeModal}
        title={`Edit ${selectedField.label?.toLowerCase() ?? ""}`}
      >
        <FormProvider {...methods}>
          <AttributeEdit
            isEntityAttribute={!!selectedField.attributeKey}
            isSubmitting={isLoading}
            onCancel={closeModal}
            onSubmit={onFormSubmit}
          />
        </FormProvider>
      </Modal>
    </div>
  );
}

export { TenantAttributes };
