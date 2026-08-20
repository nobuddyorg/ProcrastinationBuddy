import { expect, Locator, Page } from "@playwright/test";

interface SettingsModal {
  /**
   * Points to self.
   */
  (): Locator;
  /**
   * High-level interactions.
   */
  do: {
    chooseLanguage(language: string): Promise<void>;
    chooseTimezone(timezone: string): Promise<void>;
    chooseModel(model: string): Promise<void>;
    chooseTasksPerPage(taskPerPage: string): Promise<void>;
    close(): Promise<void>;
    save(): Promise<void>;
    trashTasks(): Promise<void>;
    uncheckFavorites(): Promise<void>;
  };
  /**
   * Raw locators.
   */
  locators: {
    checkboxes: {
      keepFavorites: Locator;
    };
    comboboxes: {
      language: Locator;
      timezone: Locator;
      model: Locator;
      tasksPerPage: Locator;
    };
    buttons: {
      close: Locator;
      save: Locator;
      trash: Locator;
    };
    spinners: {
      deletingTasks: Locator;
    };
  };
}

export function initSettingsModal(page: Page): SettingsModal {
  const root = page.getByRole("dialog");
  const locators = {
    checkboxes: {
      keepFavorites: root.getByText(
        /^(Keep favorites|Favoriten behalten|Mantener favoritos|Conserver les favoris)$/
      ),
    },
    comboboxes: {
      // Scoped by Streamlit's stable `st-key-<key>` class rather than
      // positional index: opening one combobox's listbox now marks its
      // siblings aria-hidden (react-aria's "hide other content while a
      // popover is open" pattern), so a shared dialog-wide nth(N) query
      // can silently point at nothing once any dropdown is open.
      language: root
        .locator(".st-key-language_selection")
        .getByRole("combobox"),
      timezone: root
        .locator(".st-key-timezone_selection")
        .getByRole("combobox"),
      model: root.locator(".st-key-model_selection").getByRole("combobox"),
      tasksPerPage: root
        .locator(".st-key-page_size_selection")
        .getByRole("combobox"),
    },
    buttons: {
      close: root.getByRole("button", { name: "Close" }),
      save: root.getByRole("button", {
        name: /^(Save|Speichern|Guardar|Enregistrer)$/,
      }),
      trash: root.getByRole("button", { name: "🗑️" }),
    },
    spinners: {
      deletingTasks: root.getByTestId("stSpinner"),
    },
  };
  const interactions = {
    chooseLanguage: async (language: string) => {
      await locators.comboboxes.language.fill(language);
      await locators.comboboxes.language.press("Enter");
    },
    chooseTimezone: async (timezone: string) => {
      await locators.comboboxes.timezone.fill(timezone);
      await locators.comboboxes.timezone.press("Enter");
    },
    chooseModel: async (model: string) => {
      await locators.comboboxes.model.fill(model);
      await locators.comboboxes.model.press("Enter");
    },
    chooseTasksPerPage: async (tasksPerPage: string) => {
      await locators.comboboxes.tasksPerPage.fill(tasksPerPage);
      await locators.comboboxes.tasksPerPage.press("Enter");
    },
    close: async () => {
      await locators.buttons.close.click();
    },
    save: async () => {
      await locators.buttons.save.click();
    },
    trashTasks: async () => {
      await locators.buttons.trash.click();
      await expect(locators.spinners.deletingTasks).toBeVisible();
      await expect(locators.spinners.deletingTasks).toBeHidden();
    },
    uncheckFavorites: async () => {
      const checkbox = locators.checkboxes.keepFavorites;

      if (await checkbox.isChecked()) {
        await checkbox.click();
        await expect(checkbox).not.toBeChecked({ timeout: 2000 });
      }

      // Optional: wait a bit before saving if your app needs it
      await page.waitForTimeout(1000);
    },
  };
  return Object.assign(() => root, { locators, do: interactions });
}
