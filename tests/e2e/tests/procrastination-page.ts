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
      name: "ProcrastinationBuddy",
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
        // Streamlit hides the actual switch input, we must include hidden elements.
        // st.toggle() renders with role="switch" (not "checkbox") as of the
        // Streamlit version bumped in this PR.
        const isChecked = await locators.switches.filterLikes
          .getByRole("switch", { includeHidden: true })
          .isChecked();
        if (filter.onlyLiked !== isChecked) {
          await locators.switches.filterLikes.click();
        }
      }
    },
    generateTask: async () => {
      const countBefore = await locators.tasks.count();
      await locators.buttons.generate.click();
      // Generation can complete before this check runs, so the spinner may
      // never be observed visible - only assert it ends up hidden.
      await expect(locators.spinners.generatingTask).toBeHidden({
        timeout: 300_000,
      });
      // The spinner hiding, the Generate button re-enabling, and the new
      // task row appearing all come from separate DOM patches that aren't
      // guaranteed to land together - a caller reading the task list or
      // clicking Generate again right after can race a rerun that hasn't
      // fully landed yet. Prefer waiting for the new row, but don't hang
      // once the visible page is already at its configured page size
      // (pagination caps how many rows show, so the count stops growing).
      await expect(locators.tasks)
        .toHaveCount(countBefore + 1, { timeout: 5_000 })
        .catch(() => {});
      await expect(locators.buttons.generate).toBeEnabled({ timeout: 30_000 });
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
