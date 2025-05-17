import { test, expect, Page, Locator } from '@playwright/test';

test.describe('Procrastination Buddy UI', () => {
  let page: Page;
  const locators = {} as {
    heading: Locator;
    generateButton: Locator;
    infoButton: Locator;
    settingsButton: Locator;
    filterLikesLabel: Locator;
    noTasksText: Locator;
    spinner: Locator;
    likeButton: Locator;
    tasks: Locator;
    trashButton: Locator;
    saveButton: Locator;
    keepFavoritesCheckbox: Locator;
  };

  const clickWithDelay = async (element: Locator, delayMs = 500) => {
    await expect(element).toHaveCount(1);
    await element.click();
    await element.page().waitForTimeout(delayMs);
  };

  const fillWithDelay = async (element: Locator, value: string, delayMs = 500) => {
    await expect(element).toHaveCount(1);
    await element.fill(value);
    await element.press('Enter');
    await element.page().waitForTimeout(delayMs);
  };

  const defineLocators = (p: Page) => {
    locators.heading = p.getByRole('heading', {
      name: 'Your partner in crime for finding perfectly pointless tasks!',
    });
    locators.generateButton = p.getByRole('button', { name: 'Generate' });
    locators.infoButton = p.getByRole('button', { name: 'ℹ️' });
    locators.settingsButton = p.getByRole('button', { name: '⚙️' });
    locators.filterLikesLabel = p.getByText('Filter Likes');
    locators.noTasksText = p.getByText('No tasks to display.');
    locators.spinner = p.locator('[data-testid="stSpinner"]');
    locators.likeButton = p.getByTestId('stIconEmoji').filter({ hasText: '❤' });
    locators.tasks = p.locator('text=/^\\d{2}:\\d{2}:\\d{2}: .+$/');
    locators.trashButton = p.getByRole('button', { name: '🗑️' });
    locators.saveButton = p.getByRole('button', {
      name: /^(Save|Speichern|Guardar|Enregistrer)$/,
    });
    locators.keepFavoritesCheckbox = p.getByText(
      /^(Keep favorites|Favoriten behalten|Mantener favoritos|Conserver les favoris)$/
    );
  };

  const resetAppState = async () => {
    await clickWithDelay(locators.settingsButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Tweak Buddy/);
    await fillWithDelay(page.getByRole('combobox').nth(0), 'English');
    await fillWithDelay(page.getByRole('combobox').nth(1), 'Europe/Berlin');
    await fillWithDelay(page.getByRole('combobox').nth(2), 'llama3:8b');
    await fillWithDelay(page.getByRole('combobox').nth(3), '5');
    await clickWithDelay(locators.keepFavoritesCheckbox);
    await clickWithDelay(locators.trashButton);
    await expect(locators.spinner).toBeVisible();
    await expect(locators.spinner).toBeHidden();
    await clickWithDelay(locators.saveButton);
    await expect(locators.noTasksText).toBeVisible();
  };

  test.beforeEach(async ({ page: p }) => {
    page = p;
    await page.goto('http://localhost:8501');
    defineLocators(page);
    await resetAppState();
  });

  test('should have the correct title', async () => {
    await expect(page).toHaveTitle(/Procrastination Buddy ⏰🤷/);
  });

  test('should display all key UI elements', async () => {
    const {
      heading,
      generateButton,
      infoButton,
      settingsButton,
      filterLikesLabel,
    } = locators;

    await expect(heading).toBeVisible();
    await expect(generateButton).toBeVisible();
    await expect(infoButton).toBeVisible();
    await expect(settingsButton).toBeVisible();
    await expect(filterLikesLabel).toBeVisible();
  });

  test('should display the info modal', async () => {
    await clickWithDelay(locators.infoButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Explanation Buddy/);
    await clickWithDelay(modal.getByRole('button', { name: 'Close' }).nth(1));
    await expect(modal).toBeHidden();
  });

  test('should display settings modal', async () => {
    await clickWithDelay(locators.settingsButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Tweak Buddy/);
    await clickWithDelay(modal.getByRole('button', { name: 'Close' }));
    await expect(modal).toBeHidden();
  });

  test('should change language', async () => {
    await clickWithDelay(locators.settingsButton);
    const modal = page.getByRole('dialog');
    await fillWithDelay(page.getByRole('combobox').nth(0), 'Deutsch');
    await clickWithDelay(locators.saveButton);
    await expect(modal).toBeHidden();
    await expect(page.getByText(/Dein Komplize/)).toBeVisible();
  });

  test('should change timezone and update task timestamp', async () => {
    const { tasks } = locators;
    await clickWithDelay(locators.generateButton);
    await expect(locators.spinner).toBeHidden({ timeout: 300_000 });
    const taskText1 = await tasks.nth(0).textContent();

    await clickWithDelay(locators.settingsButton);
    await fillWithDelay(page.getByRole('combobox').nth(1), 'America/New_York');
    await clickWithDelay(locators.saveButton);

    const taskText2 = await tasks.nth(0).textContent();
    expect(taskText1).not.toEqual(taskText2);
  });

  test('should generate a task', async () => {
    await expect(locators.noTasksText).toBeVisible();
    await clickWithDelay(locators.generateButton);
    await expect(locators.spinner).toBeHidden({ timeout: 300_000 });
    await expect(locators.tasks.nth(0)).toBeVisible();
  });

  test('should filter liked tasks', async () => {
    const { tasks, filterLikesLabel, likeButton } = locators;

    for (let i = 0; i < 2; i++) {
      await clickWithDelay(locators.generateButton);
      await expect(locators.spinner).toBeHidden({ timeout: 300_000 });
    }

    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(0);

    await clickWithDelay(filterLikesLabel);
    await clickWithDelay(likeButton.nth(0));
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(1);
  });

  test('should not delete liked tasks if preference is set', async () => {
    await clickWithDelay(locators.generateButton);
    await expect(locators.tasks).toHaveCount(1);
    await clickWithDelay(locators.likeButton.nth(0));

    await clickWithDelay(locators.settingsButton);
    await clickWithDelay(locators.trashButton);
    await expect(locators.spinner).toBeHidden();
    await clickWithDelay(locators.saveButton);
    await expect(locators.tasks).toHaveCount(1);

    await clickWithDelay(locators.likeButton.nth(0));
    await clickWithDelay(locators.settingsButton);
    await clickWithDelay(locators.keepFavoritesCheckbox);
    await clickWithDelay(locators.trashButton);
    await expect(locators.spinner).toBeHidden();
    await clickWithDelay(locators.saveButton);
    await expect(locators.tasks).toHaveCount(0);
  });

  test('should show pagination for more than 5 tasks', async () => {
    await clickWithDelay(locators.settingsButton);
    await fillWithDelay(page.getByRole('combobox').nth(3), '5');
    await clickWithDelay(locators.saveButton);

    for (let i = 0; i < 9; i++) {
      await clickWithDelay(locators.generateButton);
      await expect(locators.spinner).toBeHidden({ timeout: 300_000 });
    }

    await expect(page.getByRole('button', { name: '2' })).toBeVisible();
    await clickWithDelay(page.getByRole('button', { name: '2' }));
    await expect(locators.tasks).toHaveCount(4);

    await clickWithDelay(page.getByRole('button', { name: '1' }));
    await expect(locators.tasks).toHaveCount(5);

    await clickWithDelay(locators.settingsButton);
    await fillWithDelay(page.getByRole('combobox').nth(3), '3');
    await clickWithDelay(locators.saveButton);

    await expect(page.getByRole('button', { name: '3' })).toBeVisible();

    await clickWithDelay(locators.settingsButton);
    await clickWithDelay(locators.trashButton);
    await expect(locators.spinner).toBeHidden();
    await clickWithDelay(locators.saveButton);

    await expect(locators.noTasksText).toBeVisible();
  });
});
