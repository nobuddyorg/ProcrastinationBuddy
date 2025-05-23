import { expect, Locator, Page } from '@playwright/test';

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
    }
  };
}

export function initSettingsModal(page: Page): SettingsModal {
  const root = page.getByRole('dialog');
  const locators = {
    checkboxes: {
      keepFavorites: root.getByText(
        /^(Keep favorites|Favoriten behalten|Mantener favoritos|Conserver les favoris)$/
      ),
    },
    comboboxes: {
      language: root.getByRole('combobox').nth(0),
      timezone: root.getByRole('combobox').nth(1),
      model: root.getByRole('combobox').nth(2),
      tasksPerPage: root.getByRole('combobox').nth(3),
    },
    buttons: {
      close: root.getByRole('button', { name: 'Close' }),
      save: root.getByRole('button', {
        name: /^(Save|Speichern|Guardar|Enregistrer)$/,
      }),
      trash: root.getByRole('button', { name: '🗑️' }),
    },
    spinners: {
      deletingTasks: root.getByTestId("stSpinner"),
    }
  };
  const interactions = {
    chooseLanguage: async (language: string) => {
      await locators.comboboxes.language.fill(language);
      await locators.comboboxes.language.press('Enter');
    },
    chooseTimezone: async (timezone: string) => {
      await locators.comboboxes.timezone.fill(timezone);
      await locators.comboboxes.timezone.press('Enter');
    },
    chooseModel: async (model: string) => {
      await locators.comboboxes.model.fill(model);
      await locators.comboboxes.model.press('Enter');
    },
    chooseTasksPerPage: async (tasksPerPage: string) => {
      await locators.comboboxes.tasksPerPage.fill(tasksPerPage);
      await locators.comboboxes.tasksPerPage.press('Enter');
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
      await locators.checkboxes.keepFavorites.uncheck();
    },
  };
  return Object.assign(() => root, { locators, do: interactions });
}
