import type {
  PersonnelRowType,
  FormElement,
  FormType,
  PersonnelUserValue,
} from "@/components/templatesComponents/customisedForm.types";

export const getCrewDetails = (id: string, formObject:FormType) => {
  let result: PersonnelUserValue[] = [];
  const managersMap = new Map();
  
  // Helper function to extract personnel data from any content item
  const extractPersonnelFromItem = (item: FormElement) => {
    if (item?.type === 'personnel_component' && item.properties?.user_value) {
      result.push(...item.properties.user_value);
    }
  };
  
  // Helper function to process content arrays recursively
  const processContent = (contentArray: Array<FormElement>) => {
    if (!Array.isArray(contentArray)) return;
    
    contentArray.forEach(item => {
      extractPersonnelFromItem(item);
      
      // Handle nested content based on item type
      if (item?.contents) {
        switch (item.type) {
          case 'sub_page':
          case 'section':
            processContent(item.contents);
            break;
        }
      }
    });
  };
  
  if (Array.isArray(formObject?.contents)) {
    formObject.contents.forEach(page => {
      if (page?.contents) {
        processContent(page.contents);
      }
    });
  }
  result = result.filter(item => item.crew_details.external_id !== id)
  result.forEach(user => {
    const { manager_id, manager_name, manager_email } = user.crew_details;
    // Only add if manager_id exists and hasn't been added yet
    if (manager_id && !managersMap.has(manager_id)) {
      managersMap.set(manager_id, {
          id: manager_id,
          name: manager_name,
          email: manager_email
      });
    }
  });
  return Array.from(managersMap.values());
};

export const getUniqueManagers = (userData:PersonnelRowType[], formObject:FormType) => {
  const managersMap = new Map();
  userData.forEach(user => {
    const { managerId, managerName, managerEmail } = user;
    // Only add if manager_id exists and hasn't been added yet
    if (managerId && !managersMap.has(managerId)) {
      managersMap.set(managerId, {
          id: managerId,
          name: managerName,
          email: managerEmail
      });
    }
  });

  formObject?.metadata?.supervisor?.forEach(manager => {
    if (manager.id && !managersMap.has(manager.id)) {
      managersMap.set(manager.id, manager);
    }
  });
  
  return Array.from(managersMap.values());
}