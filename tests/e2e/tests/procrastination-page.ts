import { expect, Locator, Page } from "@playwright/test";

interface ProcrastinationPage {
  /**
   * Points to self.
   */
  (): Locator;
  /**
   * High-level interactions.
   */
  do: {
    filterTasks(filter: { onlyLiked?: boolean }): Promise<void>;
    generateTask(): Promise<void>;
    likeTask(filter: number): Promise<void>;
    openInfo(): Promise<void>;
    openSettings(): Promise<void>;
  };
  /**
   * Raw locators.
   */
  locators: {
    buttons: {
      generate: Locator;
      info: Locator;
      like: Locator;
      settings: Locator;
    };
    heading: Locator;
    switches: {
      filterLikes: Locator;
    };
    texts: {
      noTasks: Locator;
    };
    spinners: {
      generatingTask: Locator;
    };
    tasks: Locator;
  };
}

export function initProcrastinationPage(page: Page): ProcrastinationPage {
  const root = page.locator("body");
  const locators = {
    buttons: {
      generate: root.getByRole("button", { name: "Generate" }),
      info: root.getByRole("button", { name: "ℹ️" }),
      like: root.getByTestId("stIconEmoji").filter({ hasText: "❤" }),
      settings: root.getByRole("button", { name: "⚙️" }),
    },
    heading: root.getByRole("heading", {
      name: "Your partner in crime for finding perfectly pointless tasks!",
    }),
    switches: {
      filterLikes: root
        .getByTestId("stCheckbox")
        .filter({ hasText: "Filter Likes" }),
    },
    texts: {
      noTasks: root.getByText("No tasks to display."),
    },
    spinners: {
      generatingTask: root.getByTestId("stSpinner"),
    },
    tasks: root.getByText(/^\d{2}:\d{2}:\d{2}: .+$/),
  };
  const interactions = {
    filterTasks: async (filter: { onlyLiked?: boolean }) => {
      if (filter.onlyLiked !== undefined) {
        // Streamlit hides the actual checkbox input, we must include hidden elements.
        const isChecked = await locators.switches.filterLikes
          .getByRole("checkbox", { includeHidden: true })
          .isChecked();
        if (filter.onlyLiked !== isChecked) {
          await locators.switches.filterLikes.click();
        }
      }
    },
    generateTask: async () => {
      await locators.buttons.generate.click();
      await expect(locators.spinners.generatingTask).toBeVisible();
      await expect(locators.spinners.generatingTask).toBeHidden({
        timeout: 300_000,
      });
    },
    likeTask: async (filter: number) => {
      await locators.buttons.like.nth(filter).click();
    },
    openInfo: async () => {
      await locators.buttons.info.click();
    },
    openSettings: async () => {
      await locators.buttons.settings.click();
    },
  };
  return Object.assign(() => root, { locators, do: interactions });
}
