import fsPromises from "fs/promises";
import { act, renderHook } from "@testing-library/react-hooks";
import xlsx from "xlsx";
import { nanoid } from "nanoid";
import * as spreadsheet from "../providers/spreadsheet";
import { sampleRiskCountData } from "../__mocks__/mockData";
import useGenerateSpreadsheet from "./useGenerateSpreadsheet";

// mock dependencies
jest.mock("../providers/spreadsheet", () => ({
  __esModule: true,
  ...jest.requireActual("../providers/spreadsheet"),
}));
jest.mock("fs", () => jest.requireActual("memfs").fs);
jest.mock("fs/promises", () => jest.requireActual("memfs").fs.promises);
jest.mock("../utils", () => ({
  ...jest.requireActual("../utils"),
  downloadContentAsFile: async (content: string, fileName: string) => {
    const { fs } = jest.requireActual("memfs");
    await fs.promises.writeFile(`/${fileName}`, content, "base64");
  },
}));

const singleDocumentData = [
  [`workbook-${nanoid()}`, sampleRiskCountData],
] as spreadsheet.WorkbookData;

const multipleDocumentsData = [
  [`workbook-${nanoid()}`, sampleRiskCountData],
  [`workbook-${nanoid()}`, sampleRiskCountData],
  [`workbook-${nanoid()}`, sampleRiskCountData],
  [`workbook-${nanoid()}`, sampleRiskCountData],
] as spreadsheet.WorkbookData;

const filtersData = [
  "filters",
  [
    {
      startDate: "2022-01-29",
      endDate: "2022-02-03",
      projectIds: [],
      projectStatuses: [],
      regionIds: [],
      divisionIds: [],
      contractorIds: [],
    },
  ],
] as unknown as spreadsheet.WorkbookData;

const singleDocumentWithFilters = [
  singleDocumentData[0],
  filtersData,
] as spreadsheet.WorkbookData;

describe(useGenerateSpreadsheet.name, () => {
  it("should return an object with a generateDocument function", () => {
    const { result } = renderHook(() => useGenerateSpreadsheet());

    expect(result.current.generateDocument).toBeInstanceOf(Function);
  });

  it("should return all flags as false, initially", () => {
    const { result } = renderHook(() => useGenerateSpreadsheet());
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { generateDocument, ...flags } = result.current;

    Object.values(flags).forEach(flag => {
      expect(flag).toBe(false);
    });
  });

  describe("when writing the document", () => {
    const spy = jest.spyOn(xlsx, "writeFile");

    beforeEach(() => {
      spy.mockClear();
    });

    describe("for one dimension array data", () => {
      it.each(["csv", "xlsx"] as const)(
        "should generate one file for format %s",
        async fileType => {
          const fileName = "/hello";
          const file = `${fileName}.${fileType}`;

          const { result, waitForNextUpdate } = renderHook(() =>
            useGenerateSpreadsheet()
          );

          act(() => {
            result.current.generateDocument(singleDocumentData, {
              fileName,
              fileType,
            });
          });

          await waitForNextUpdate();

          expect(spy).toBeCalledWith(expect.anything(), file, {
            file,
            type: "file",
            bookType: fileType,
          });

          expect((await fsPromises.stat(file)).isFile()).toBe(true);
        }
      );
    });

    describe("for a multi dimension array data", () => {
      it("should generate one file for format xlsx", async () => {
        // workaround: to work with the virtual fs, we need to pass in the slash at the begging.
        const file = "/hello-xlsx.xlsx";

        const [fileName, fileType] = file.split(".") as [
          string,
          spreadsheet.WorkbookSupportedFileTypes
        ];

        const { result, waitForNextUpdate } = renderHook(() =>
          useGenerateSpreadsheet()
        );

        act(() => {
          result.current.generateDocument(multipleDocumentsData, {
            fileName,
            fileType,
          });
        });

        await waitForNextUpdate();

        expect(spy).toBeCalledWith(expect.anything(), file, {
          file,
          type: "file",
          bookType: fileType,
        });

        // assert the the file exists
        expect((await fsPromises.stat(file)).isFile()).toBe(true);
      });

      it("should generate one zip for format csv", async () => {
        // workaround: to work with the virtual fs, we need to pass in the slash at the begging.
        const fileName = "/hello-multi-csv";

        const { result, waitForNextUpdate } = renderHook(() =>
          useGenerateSpreadsheet()
        );

        act(() => {
          result.current.generateDocument(multipleDocumentsData, {
            fileName,
            fileType: "csv",
          });
        });

        await waitForNextUpdate();

        expect((await fsPromises.stat(`${fileName}.zip`)).isFile()).toBe(true);
      });
    });

    describe("for data with filters applied", () => {
      it("should generate one file for format xlsx", async () => {
        // workaround: to work with the virtual fs, we need to pass in the slash at the begging.
        const file = "/hello-filters-xlsx.xlsx";

        const [fileName, fileType] = file.split(".") as [
          string,
          spreadsheet.WorkbookSupportedFileTypes
        ];

        const { result, waitForNextUpdate } = renderHook(() =>
          useGenerateSpreadsheet()
        );

        act(() => {
          result.current.generateDocument(singleDocumentWithFilters, {
            fileName,
            fileType,
          });
        });

        await waitForNextUpdate();

        expect(spy).toBeCalledWith(expect.anything(), file, {
          file,
          type: "file",
          bookType: fileType,
        });

        // assert the the file exists
        expect((await fsPromises.stat(file)).isFile()).toBe(true);
      });

      it("should generate one zip for format csv", async () => {
        // workaround: to work with the virtual fs, we need to pass in the slash at the begging.
        const fileName = "/hello-single-filters";

        const { result, waitForNextUpdate } = renderHook(() =>
          useGenerateSpreadsheet()
        );

        act(() => {
          result.current.generateDocument(singleDocumentWithFilters, {
            fileName,
            fileType: "csv",
          });
        });

        await waitForNextUpdate();

        // assert the the file exists
        expect((await fsPromises.stat(`${fileName}.zip`)).isFile()).toBe(true);
      });
    });
  });

  describe("when calling generateDocument function", () => {
    const copyGenerateDownloadableWorkbook =
      spreadsheet.generateDownloadableWorkbook;

    beforeEach(() => {
      (spreadsheet.generateDownloadableWorkbook as jest.Mocked<
        typeof spreadsheet.generateDownloadableWorkbook
      >) = jest.fn().mockResolvedValue({});
    });

    afterEach(() => {
      (
        spreadsheet.generateDownloadableWorkbook as jest.MockedFunction<
          typeof spreadsheet.generateDownloadableWorkbook
        >
      ).mockClear();
    });

    afterAll(() => {
      (spreadsheet.generateDownloadableWorkbook as jest.Mocked<
        typeof spreadsheet.generateDownloadableWorkbook
      >) = copyGenerateDownloadableWorkbook;
    });

    describe("emits lifecycle flags", () => {
      describe("errors scenarios", () => {
        it("should throw an error when the data is not a valid array and set `isError` flag as true", async () => {
          const { result } = renderHook(() => useGenerateSpreadsheet());
          act(() => {
            result.current
              // eslint-disable-next-line @typescript-eslint/ban-ts-comment
              // @ts-ignore
              .generateDocument(undefined, {
                fileName: "hello",
                fileType: "csv",
              })
              .catch(e => {
                expect(e).toEqual(new Error("invalid data"));
              });
          });
          expect(result.current.isLoading).toBe(false);
          expect(result.current.isCompleted).toBe(false);
          expect(result.current.isError).toBe(true);
        });
        // TODO: should we include a runtime validation to make sure the object is valid?
        // Could be useful to track nasty, edge cases but it has a very high penalty cost (parsing the JSON in memory and throw it away)
        it.todo(
          "should throw an error when the data is not a valid JSON object"
        );
      });

      it("should set the `isLoading` as true while importing and parsing the data", async () => {
        const { result, waitForNextUpdate } = renderHook(() =>
          useGenerateSpreadsheet()
        );
        act(() => {
          result.current.generateDocument(singleDocumentData, {
            fileName: "hello",
            fileType: "csv",
          });
        });
        expect(result.current.isLoading).toBe(true);
        expect(result.current.isCompleted).toBe(false);
        expect(result.current.isError).toBe(false);
        await waitForNextUpdate();
      });
      it("should set the `isCompleted` as true when the document is downloaded", async () => {
        const { result, waitForNextUpdate } = renderHook(() =>
          useGenerateSpreadsheet()
        );
        act(() => {
          result.current.generateDocument(singleDocumentData, {
            fileName: "hello",
            fileType: "csv",
          });
        });
        await waitForNextUpdate();
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isCompleted).toBe(true);
        expect(result.current.isError).toBe(false);
      });
    });

    it("must only generate one file at the time when calling it multiple times", async () => {
      // temporarily mute console.warn
      const spyConsoleWarn = jest
        .spyOn(global.console, "warn")
        .mockImplementation(() => false);

      const { result, waitForNextUpdate } = renderHook(() =>
        useGenerateSpreadsheet()
      );

      act(() => {
        result.current.generateDocument(singleDocumentData, {
          fileName: "/hello-xlsx",
          fileType: "xlsx",
        });
      });

      act(() => {
        result.current.generateDocument(singleDocumentData, {
          fileName: "/hello-xlsx-2",
          fileType: "xlsx",
        });
      });

      act(() => {
        result.current.generateDocument(singleDocumentData, {
          fileName: "/hello-xlsx-3",
          fileType: "xlsx",
        });
      });

      await waitForNextUpdate();

      expect(spreadsheet.generateDownloadableWorkbook).toHaveBeenCalledTimes(1);

      // restore the console.warn back
      spyConsoleWarn.mockRestore();
    });

    // https://stackoverflow.com/questions/70065014/xlsx-sheetname-exceeding-31-characters-in-length-in-react
    it("must trim work sheet titles with more than 31 characters with ellipsis", async () => {
      const spy = jest.spyOn(xlsx, "writeFile");

      const { result, waitForNextUpdate } = renderHook(() =>
        useGenerateSpreadsheet()
      );

      const singleDocumentDataWithLargeName: spreadsheet.WorkbookData = [
        [`workbook-title-with-excessive-title-trims`, singleDocumentData[0][1]],
      ];

      act(() => {
        result.current.generateDocument(singleDocumentDataWithLargeName, {
          fileName: "/hello-xlsx",
          fileType: "xlsx",
        });
      });

      await waitForNextUpdate();

      expect(spreadsheet.generateDownloadableWorkbook).toHaveBeenCalledTimes(1);

      spy.mockRestore();
    });
  });
});
