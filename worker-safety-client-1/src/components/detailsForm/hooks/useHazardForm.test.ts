import type { Hazard } from "@/types/project/Hazard";
import { renderHook } from "@testing-library/react-hooks";
import * as rhf from "react-hook-form";
import { formTemplate, mockTenantStore } from "@/utils/dev/jest";
import { useHazardForm } from "./useHazardForm";

const taskHazards: Hazard[] = [
  {
    id: "custom-hazard-1",
    name: "Hazard 1",
    isApplicable: true,
    controls: [],
  },
  {
    id: "custom-hazard-2",
    name: "Hazard 2",
    isApplicable: true,
    controls: [],
  },
  {
    id: "custom-hazard-3",
    name: "Hazard 3",
    isApplicable: true,
    controls: [],
  },
  {
    id: "custom-hazard-4",
    name: "Hazard 4",
    isApplicable: true,
    controls: [],
  },
];

const hazardsLibrary: Hazard[] = [];

describe(useHazardForm.name, () => {
  beforeAll(mockTenantStore);

  it("should return the list of hazards with keys as well as multiple handlers", () => {
    const { result } = renderHook(
      () => useHazardForm(taskHazards, hazardsLibrary),
      {
        wrapper({ children }) {
          return formTemplate(children);
        },
      }
    );

    expect(result.current).toMatchObject(
      expect.objectContaining({
        hazards: expect.arrayContaining(
          taskHazards.map(task => ({
            ...task,
            key: task.id,
          }))
        ),
        isAddButtonDisabled: expect.any(Function),
        addHazardHandler: expect.any(Function),
        removeHazardHandler: expect.any(Function),
        selectHazardHandler: expect.any(Function),
      })
    );
  });

  describe("`isAddButtonDisabled` handler", () => {
    it("should return false when the size of hazardLibraries is different from all hazards created by the user", () => {
      const hazardTasks = [...taskHazards];
      const hazardLibraries = [
        ...hazardsLibrary,
        {
          id: "1",
          name: "Situational Jobsite Awareness",
          isApplicable: true,
        } as Hazard,
      ];

      const { result } = renderHook(
        () => useHazardForm(hazardTasks, hazardLibraries),
        {
          wrapper({ children }) {
            return formTemplate(children);
          },
        }
      );

      expect(result.current.isAddButtonDisabled()).toBe(false);
    });

    it("should return true when the size of hazardLibraries is equal to the size of all hazards created by the user", () => {
      const hazardTasks = [...taskHazards];
      const hazardLibraries = [...hazardsLibrary];

      const { result } = renderHook(
        () => useHazardForm(hazardTasks, hazardLibraries),
        {
          wrapper({ children }) {
            return formTemplate(children);
          },
        }
      );

      expect(result.current.isAddButtonDisabled()).toBe(true);
    });
  });

  describe("when is updated", () => {
    it("should return a new list of hazards and new handlers", () => {
      const hazardTasks = [...taskHazards];
      const hazardLibraries = [...hazardsLibrary];

      const { result, rerender } = renderHook(
        () => useHazardForm(hazardTasks, hazardLibraries),
        {
          wrapper({ children }) {
            return formTemplate(children);
          },
        }
      );

      const { hazards: prevHazards } = result.current;
      hazardTasks.push({
        id: "custom-hazard-5",
        name: "Hazard 5",
        isApplicable: false,
        controls: [],
      });
      rerender();
      expect(result.current.hazards).not.toEqual(prevHazards);
    });
  });

  describe("when passing options", () => {
    it("should, by default, have the form state include all hazards in the 'hazards' state", () => {
      const spy = jest.fn();
      jest.spyOn(rhf, "useFormContext").mockImplementation(
        () =>
          ({
            setValue: spy,
            getValues: jest.fn(),
          } as unknown as ReturnType<typeof rhf.useFormContext>)
      );

      renderHook(() => useHazardForm(taskHazards, hazardsLibrary), {
        wrapper({ children }) {
          return formTemplate(children);
        },
      });

      expect(spy).toHaveBeenCalledWith("hazards", expect.anything());
    });

    it("should accept a index and a prefix and should add to the formValues", () => {
      const spy = jest.fn();
      jest.spyOn(rhf, "useFormContext").mockImplementation(
        () =>
          ({
            setValue: spy,
            getValues: jest.fn(),
          } as unknown as ReturnType<typeof rhf.useFormContext>)
      );

      renderHook(
        () =>
          useHazardForm(taskHazards, hazardsLibrary, {
            prefix: "tasks",
            taskIndex: 0,
          }),
        {
          wrapper({ children }) {
            return formTemplate(children);
          },
        }
      );

      expect(spy).toHaveBeenCalledWith("tasks.0.hazards", expect.anything());
    });
  });
});
