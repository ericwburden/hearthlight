import { ApplicationModelEntry } from '@/interfaces';

// --------------------------------------------------------------------------------------------------------------------
//#region | Token utility functions -----------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------------------------------

export const getLocalToken = () => localStorage.getItem('token');

export const saveLocalToken = (token: string) => localStorage.setItem('token', token);

export const removeLocalToken = () => localStorage.removeItem('token');

// --------------------------------------------------------------------------------------------------------------------
//#endregion ----------------------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------------------------------
//#region | Application Model utility functions -----------------------------------------------------------------------
// --------------------------------------------------------------------------------------------------------------------

function searchApplicationModelInstance(
  element: ApplicationModelEntry,
  id: number,
  type: string,
): ApplicationModelEntry | null {
  if (element.id == id && element.type == type) {
    return element;
  } else if (element.children != null) {
    let i;
    let result = null;
    for (i = 0; result == null && i < element.children.length; i++) {
      result = searchApplicationModelInstance(element.children[i], id, type);
    }
    return result;
  }
  return null;
}

export function searchApplicationModel(
  model: ApplicationModelEntry[],
  id: number,
  type: string,
): ApplicationModelEntry | null {
  let network;
  for (network of model) {
    const result = searchApplicationModelInstance(network, id, type);
    if (result) {
      return result;
    }
  }
  return null;
}

// --------------------------------------------------------------------------------------------------------------------
//#endregion ----------------------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------------------------------
