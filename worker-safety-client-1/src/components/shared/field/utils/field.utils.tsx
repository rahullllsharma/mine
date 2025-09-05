export const FieldErrorDetectionClassName = "field-error-detection";

/**
 * Retrieves nodes from DOM that have FieldErrorDetectionClass
 * Retrieves the first parent from the DOM that contains an <label> element
 * Scroll the found element intoView
 *
 * results in early return if invoked when there are no error fields on DOM or errorFieldNode has no parent
 */
export const scrollToFirstErrorSection = () => {
  const errorFieldsOnDOM = document.getElementsByClassName(
    FieldErrorDetectionClassName
  );

  if (errorFieldsOnDOM.length === 0) return;

  const parentOfFirstErrorField = errorFieldsOnDOM[0].parentElement;

  if (!parentOfFirstErrorField) return;

  const targetSectionWithError = findParentNodeOfTagName(
    parentOfFirstErrorField,
    "label"
  );

  if (targetSectionWithError) {
    targetSectionWithError.scrollIntoView({ behavior: "smooth" });
  }
};

/**
 * Traverse the DOM structure upwards from a given a given node
 * Find and return DOM node with a children of tagName
 *
 * Based on XML of <Field /> component, this function should always return <Field /> component
 */
const findParentNodeOfTagName = (
  node: HTMLElement,
  tagName: string
): Element | undefined => {
  if (
    Array.from(node.children).some(c => c.tagName.toLowerCase() === tagName)
  ) {
    return node;
  }

  const parentNode = node.parentElement;

  if (!parentNode) return undefined;
  return findParentNodeOfTagName(parentNode, tagName);
};
