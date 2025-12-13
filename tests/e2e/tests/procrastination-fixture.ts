import test, { Page } from "@playwright/test";
import { initInfoModal } from "./info-modal";
import { initProcrastinationPage } from "./procrastination-page";
import { initSettingsModal } from "./settings-modal";

function createPageTree(page: Page) {
  // We use getters here for lazy evaluation. There's no need to create all page objects if we're
  // just interested in a single one.
  return {
    get main() {
      return initProcrastinationPage(page);
    },
    get modal() {
      return {
        get info() {
          return initInfoModal(page);
        },
        get settings() {
          return initSettingsModal(page);
        },
      };
    },
  };
}

export const buddyTest = test.extend<{
  on: typeof createPageTree;
}>({
  on: async ({}, use) => {
    await use((page: Page) => {
      return createPageTree(page);
    });
  },
});
