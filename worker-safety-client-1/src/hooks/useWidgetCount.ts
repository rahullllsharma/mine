import { useState, useCallback } from "react";

const MAX_WIDGET_COUNT = 15;

export const useWidgetCount = () => {
  const [widgetCount, setWidgetCount] = useState(0);

  const incrementWidgetCount = useCallback(() => {
    setWidgetCount(prev => Math.min(prev + 1, MAX_WIDGET_COUNT));
  }, []);

  const decrementWidgetCount = useCallback(() => {
    setWidgetCount(prev => Math.max(prev - 1, 0));
  }, []);

  const setWidgetCountDirectly = useCallback((count: number) => {
    setWidgetCount(Math.max(0, Math.min(count, MAX_WIDGET_COUNT)));
  }, []);

  const canAddWidget = widgetCount < MAX_WIDGET_COUNT;

  return {
    widgetCount,
    maxWidgetCount: MAX_WIDGET_COUNT,
    incrementWidgetCount,
    decrementWidgetCount,
    setWidgetCountDirectly,
    canAddWidget,
  };
};
