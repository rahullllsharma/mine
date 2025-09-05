import type { PhotoItemErrorOverlayProps } from '@/components/templatesComponents/customisedForm.types';
import React from 'react';
import { BodyText, Icon } from "@urbint/silica"; 
import ButtonPrimary from '@/components/shared/button/primary/ButtonPrimary';

export const PhotoItemErrorOverlay = ({
  onReload,
  showSpinner,
}:PhotoItemErrorOverlayProps) => {
  return (
    <>
      <ButtonPrimary
        onClick={onReload}
        className={`absolute top-1 right-1 p-1 rounded-full bg-black bg-opacity-50 hover:bg-opacity-70 text-white transition-all duration-200 ${
          showSpinner 
            ? 'cursor-not-allowed opacity-50' 
            : 'cursor-pointer'
        }`}
        title="Reload image"
        disabled={showSpinner} 
      >
        <Icon 
          name="refresh_02" 
          className={showSpinner ? 'animate-spin' : ''} 
        />
      </ButtonPrimary>   
      
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-100 border-2 border-dashed border-gray-300 rounded">      
        <Icon 
          name="refresh" 
          className="text-gray-400 mb-1" 
        />
        <BodyText className="text-xs text-gray-500 text-center px-1 mb-2">
          Failed
        </BodyText>
        <ButtonPrimary
          onClick={onReload}
          className={` text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 ${
            showSpinner 
            ? "cursor-not-allowed opacity-50"
            : ""
          }`}
          iconStart="refresh" 
          disabled={showSpinner}
          aria-label="Retry loading image"
        >
          Retry
        </ButtonPrimary>
      </div>
    </>
  );
};