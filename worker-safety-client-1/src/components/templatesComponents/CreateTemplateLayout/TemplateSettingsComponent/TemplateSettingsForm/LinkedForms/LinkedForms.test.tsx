import type { TemplateSettings } from "@/components/templatesComponents/customisedForm.types";
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FormProvider, useForm } from 'react-hook-form';
import LinkedForms from './LinkedForm';

// Test wrapper component to provide form context
const TestWrapper = ({ children, defaultValues = {} }: { children: React.ReactNode; defaultValues?: any }) => {
  const methods = useForm({ defaultValues });
  return <FormProvider {...methods}>{children}</FormProvider>;
};

describe('LinkedForms', () => {
  const defaultSettings: TemplateSettings = {
    copy_and_rebrief: {
      is_copy_enabled: false,
      is_rebrief_enabled: false,
    },
  } as TemplateSettings;

  describe('Rendering', () => {
    it('renders the component with correct heading', () => {
      render(
        <TestWrapper>
          <LinkedForms settings={defaultSettings} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Linked Forms')).toBeInTheDocument();
    });

    it('renders checkbox options with correct labels', () => {
      render(
        <TestWrapper>
          <LinkedForms settings={defaultSettings} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Allow rebriefing this form (available during Edit Period)')).toBeInTheDocument();
      expect(screen.getByText('Allow copying this form')).toBeInTheDocument();
    });
  });

  describe('Initial State', () => {
    it('always initializes with both options disabled (false state)', () => {
      render(
        <TestWrapper>
          <LinkedForms settings={defaultSettings} />
        </TestWrapper>
      );
      
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes).toHaveLength(2);
      
      // Both checkboxes should start unchecked
      checkboxes.forEach(checkbox => {
        expect(checkbox).not.toBeChecked();
      });
    });
  });

  describe('User Interactions', () => {
    it('updates checkbox state when rebrief option is clicked', async () => {
      render(
        <TestWrapper>
          <LinkedForms settings={defaultSettings} />
        </TestWrapper>
      );
      
      const rebriefCheckbox = screen.getByLabelText(/Allow rebriefing this form/);
      
      // Initially unchecked
      expect(rebriefCheckbox).not.toBeChecked();
      
      // Click to check
      fireEvent.click(rebriefCheckbox);
      
      // Should become checked
      await waitFor(() => {
        expect(rebriefCheckbox).toBeChecked();
      });
    });

    it('updates checkbox state when copy option is clicked', async () => {
      render(
        <TestWrapper>
          <LinkedForms settings={defaultSettings} />
        </TestWrapper>
      );
      
      const copyCheckbox = screen.getByLabelText(/Allow copying this form/);
      
      // Initially unchecked
      expect(copyCheckbox).not.toBeChecked();
      
      // Click to check
      fireEvent.click(copyCheckbox);
      
      // Should become checked
      await waitFor(() => {
        expect(copyCheckbox).toBeChecked();
      });
    });

    it('allows toggling both options independently', async () => {
      render(
        <TestWrapper>
          <LinkedForms settings={defaultSettings} />
        </TestWrapper>
      );
      
      const rebriefCheckbox = screen.getByLabelText(/Allow rebriefing this form/);
      const copyCheckbox = screen.getByLabelText(/Allow copying this form/);
      
      // Check rebrief first
      fireEvent.click(rebriefCheckbox);
      
      await waitFor(() => {
        expect(rebriefCheckbox).toBeChecked();
        expect(copyCheckbox).not.toBeChecked();
      });

      // Then check copy
      fireEvent.click(copyCheckbox);
      
      await waitFor(() => {
        expect(rebriefCheckbox).toBeChecked();
        expect(copyCheckbox).toBeChecked();
      });
    });

    it('allows unchecking previously checked options', async () => {
      const settingsWithBothEnabled: TemplateSettings = {
        copy_and_rebrief: {
          is_copy_enabled: true,
          is_rebrief_enabled: true,
        },
      } as TemplateSettings;

      render(
        <TestWrapper>
          <LinkedForms settings={settingsWithBothEnabled} />
        </TestWrapper>
      );
      
      const rebriefCheckbox = screen.getByLabelText(/Allow rebriefing this form/);
      const copyCheckbox = screen.getByLabelText(/Allow copying this form/);
      
      // Initially both should be checked
      expect(rebriefCheckbox).toBeChecked();
      expect(copyCheckbox).toBeChecked();
      
      // Uncheck rebrief
      fireEvent.click(rebriefCheckbox);
      
      await waitFor(() => {
        expect(rebriefCheckbox).not.toBeChecked();
        expect(copyCheckbox).toBeChecked();
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles undefined copy_and_rebrief settings gracefully', () => {
      const settingsWithUndefined = {} as TemplateSettings;
      
      render(
        <TestWrapper>
          <LinkedForms settings={settingsWithUndefined} />
        </TestWrapper>
      );
      
      // Component should render without errors
      expect(screen.getByText('Linked Forms')).toBeInTheDocument();
      
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).not.toBeChecked();
      });
    });

    it('handles partial copy_and_rebrief settings', () => {
      const partialSettings: TemplateSettings = {
        copy_and_rebrief: {
          is_copy_enabled: true,
          // is_rebrief_enabled is undefined
        }
      } as TemplateSettings;
      
      render(
        <TestWrapper>
          <LinkedForms settings={partialSettings} />
        </TestWrapper>
      );
      
      const copyCheckbox = screen.getByLabelText(/Allow copying this form/);
      const rebriefCheckbox = screen.getByLabelText(/Allow rebriefing this form/);
      
      expect(copyCheckbox).toBeChecked();
      expect(rebriefCheckbox).not.toBeChecked();
    });
  });
});