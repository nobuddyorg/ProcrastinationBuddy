import { Locator, Page } from "@playwright/test";

interface InfoModal {
  /**
   * Points to self.
   */
  (): Locator;
  /**
   * High-level interactions.
   */
  do: {
    close(): Promise<void>;
  };
  /**
   * Raw locators.
   */
  locators: {
    buttons: {
      close: Locator;
    };
  };
}

export function initInfoModal(page: Page): InfoModal {
  const root = page.getByRole("dialog");
  const locators = {
    buttons: {
      close: page
        .getByRole("dialog")
        .getByRole("button", { name: "Close" })
        .nth(1),
    },
  };
  const interactions = {
    close: async () => {
      await locators.buttons.close.click();
    },
  };
  return Object.assign(() => root, { locators, do: interactions });
}
