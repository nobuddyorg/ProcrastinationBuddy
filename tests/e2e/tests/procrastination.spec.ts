import { test, expect, Page, Locator } from '@playwright/test';

test.describe('Procrastination Buddy UI', () => {
  let heading: ReturnType<Page['getByRole']>;
  let generateButton: ReturnType<Page['getByRole']>;
  let infoButton: ReturnType<Page['getByRole']>;
  let settingsButton: ReturnType<Page['getByRole']>;
  let filterLikesLabel: ReturnType<Page['getByText']>;
  let noTasksText: ReturnType<Page['getByText']>;
  let spinner: ReturnType<Page['locator']>;
  let likeButton: ReturnType<Page['getByRole']>;
  let tasks: ReturnType<Page['locator']>;
  let trashButton: ReturnType<Page['getByRole']>;
  let saveButton: ReturnType<Page['getByRole']>;
  let keepFavoritesCheckbox: ReturnType<Page['getByText']>;

  async function clickWithDelay(element: Locator, delayMs = 500) {
    await expect(element).toHaveCount(1);
    await element.click();
    await element.page().waitForTimeout(delayMs);
  }

  async function fillWithDelay(element: Locator, value: string, delayMs = 500) {
    await expect(element).toHaveCount(1);
    await element.fill(value);
    await element.press('Enter');
    await element.page().waitForTimeout(delayMs);
  }

  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8501');

    // Define locators
    heading = page.getByRole('heading', {
      name: 'Your partner in crime for finding perfectly pointless tasks!',
    });
    generateButton = page.getByRole('button', { name: 'Generate' });
    infoButton = page.getByRole('button', { name: 'ℹ️' });
    settingsButton = page.getByRole('button', { name: '⚙️' });
    filterLikesLabel = page.getByText('Filter Likes');
    noTasksText = page.getByText('No tasks to display.');
    spinner = page.locator('[data-testid="stSpinner"]');
    likeButton = page.getByTestId('stIconEmoji').filter({ hasText: '❤' });
    tasks = page.locator('text=/^\\d{2}:\\d{2}:\\d{2}: .+$/');
    trashButton = page.getByRole('button', { name: '🗑️' });
    saveButton = page.getByRole('button', { name: /^(Save|Speichern|Guardar|Enregistrer)$/ });
    keepFavoritesCheckbox = page.getByText(/^(Keep favorites|Favoriten behalten|Mantener favoritos|Conserver les favoris)$/);

    // reset the app state
    await clickWithDelay(settingsButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Tweak Buddy/);
    await fillWithDelay(page.getByRole('combobox').nth(0), 'English');
    await fillWithDelay(page.getByRole('combobox').nth(1), 'Europe/Berlin');
    await fillWithDelay(page.getByRole('combobox').nth(2), 'llama3:8b');
    await fillWithDelay(page.getByRole('combobox').nth(3), '5');
    await clickWithDelay(keepFavoritesCheckbox);
    await clickWithDelay(trashButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden();
    await clickWithDelay(saveButton);
    await expect(noTasksText).toBeVisible();
  });

  test('should have the correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/Procrastination Buddy ⏰🤷/);
  });

  test('should display all key UI elements', async () => {
    await expect(heading).toBeVisible();

    await expect(generateButton).toBeVisible();
    await expect(generateButton).toBeEnabled();

    await expect(infoButton).toBeVisible();
    await expect(infoButton).toBeEnabled();

    await expect(settingsButton).toBeVisible();
    await expect(settingsButton).toBeEnabled();

    await expect(filterLikesLabel).toBeVisible();
    await expect(filterLikesLabel).toBeEnabled();
  });

  test('should display the info modal when the info button is clicked', async ({ page }) => {
    await clickWithDelay(infoButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Explanation Buddy/);
    await clickWithDelay(modal.getByRole('button', { name: 'Close' }).nth(1));
    await expect(modal).toBeHidden();
  });

  test('should display the settings modal when the settings button is clicked', async ({ page }) => {
    await clickWithDelay(settingsButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Tweak Buddy/);
    await clickWithDelay(modal.getByRole('button', { name: 'Close' }));
    await expect(modal).toBeHidden();
  });

  test('should change language', async ({ page }) => {
    await clickWithDelay(settingsButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Tweak Buddy/);
    await fillWithDelay(page.getByRole('combobox').nth(0), 'Deutsch');
    await clickWithDelay(saveButton);
    await expect(modal).toBeHidden();
    await expect(page.getByText(/Dein Komplize bei der Suche nach völlig sinnlosen Aufgaben!/)).toBeVisible();
    await expect(page.getByText(/Generiere/)).toBeVisible();
    await expect(page.getByText(/Keine Aufgaben zum Anzeigen./)).toBeVisible();
  });

  test('should change timezone', async ({ page }) => {
    await clickWithDelay(generateButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden({ timeout: 300_000 });
    await expect(noTasksText).toBeHidden();

    await expect(tasks).toHaveCount(1);
    await expect(tasks.nth(0)).toBeVisible();
    await expect(tasks.nth(0)).toHaveText(/^\d{2}:\d{2}:\d{2}: .+$/);
    const taskText1 = await tasks.nth(0).textContent();
    await expect(tasks.nth(0)).toHaveText(taskText1 ?? '');

    await clickWithDelay(settingsButton);
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveText(/Tweak Buddy/);
    await fillWithDelay(page.getByRole('combobox').nth(1), 'America/New_York');
    await clickWithDelay(saveButton);
    await expect(modal).toBeHidden();
    await expect(page.getByText(/^\d{2}:\d{2}:\d{2}: .+$/)).toBeVisible();
    await expect(tasks).toHaveCount(1);
    await expect(tasks.nth(0)).toBeVisible();

    await expect(tasks.nth(0)).not.toHaveText(taskText1 ?? '');
    const taskText2 = await tasks.nth(0).textContent();

    expect(taskText1).not.toEqual(taskText2);
  });

  test('should generate a task when the Generate button is clicked', async ({ page }) => {
    await expect(noTasksText).toBeVisible();
    await clickWithDelay(generateButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden({ timeout: 300_000 });
    await expect(noTasksText).toBeHidden();
    await expect(page.getByText(/^\d{2}:\d{2}:\d{2}: .+$/)).toBeVisible();
  });

  test('should filter liked tasks', async ({ page }) => {
    await expect(noTasksText).toBeVisible();
    await clickWithDelay(generateButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden({ timeout: 300_000 });
    await expect(noTasksText).toBeHidden();

    await clickWithDelay(generateButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden({ timeout: 300_000 });

    await expect(tasks).toHaveCount(2);
    await expect(tasks.nth(0)).toBeVisible();
    await expect(tasks.nth(1)).toBeVisible();

    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(0);
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(2);

    await clickWithDelay(likeButton.nth(0));
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(1);
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(2);

    await clickWithDelay(likeButton.nth(1));
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(2);
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(2);

    await clickWithDelay(likeButton.nth(0));
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(1);
    await clickWithDelay(filterLikesLabel);
    await expect(tasks).toHaveCount(2);
  });

test('should not delete liked tasks', async ({ page }) => {
    await expect(noTasksText).toBeVisible();
    await clickWithDelay(generateButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden({ timeout: 300_000 });
    await expect(noTasksText).toBeHidden();

    await expect(tasks).toHaveCount(1);
    await expect(tasks.nth(0)).toBeVisible();

    await clickWithDelay(likeButton.nth(0));

    await clickWithDelay(settingsButton);
    await clickWithDelay(trashButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden();
    await clickWithDelay(saveButton);

    await expect(tasks).toHaveCount(1);

    await clickWithDelay(likeButton.nth(0));

    await clickWithDelay(settingsButton);
    await clickWithDelay(keepFavoritesCheckbox);
    await clickWithDelay(trashButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden();
    await clickWithDelay(saveButton);

    await expect(tasks).toHaveCount(0);
  });

  test('should show pagination when there are more than 5 tasks', async ({ page }) => {
    await expect(noTasksText).toBeVisible();
    await clickWithDelay(settingsButton);
    await fillWithDelay(page.getByRole('combobox').nth(3), '5');
    await clickWithDelay(saveButton);

    for (let i = 0; i < 5; i++) {
      await clickWithDelay(generateButton);
      await expect(spinner).toBeVisible();
      await expect(spinner).toBeHidden({ timeout: 300_000 });
    }

    await expect(page.getByRole('button', {name: '1'})).toBeHidden();

    for (let i = 0; i < 4; i++) {
      await clickWithDelay(generateButton);
      await expect(spinner).toBeVisible();
      await expect(spinner).toBeHidden({ timeout: 300_000 });
    }

    await expect(page.getByRole('button', {name: '1'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2'})).toBeVisible();
    await expect(tasks).toHaveCount(5);

    await clickWithDelay(page.getByRole('button', {name: '2'}));
    await expect(tasks).toHaveCount(4);

    await clickWithDelay(page.getByRole('button', {name: '1'}));
    await expect(tasks).toHaveCount(5);

    await clickWithDelay(settingsButton);
    await fillWithDelay(page.getByRole('combobox').nth(3), '10');
    await clickWithDelay(saveButton);
    await expect(page.getByRole('button', {name: '1'})).toBeHidden();

    await clickWithDelay(settingsButton);
    await fillWithDelay(page.getByRole('combobox').nth(3), '3');
    await clickWithDelay(saveButton);
    await expect(page.getByRole('button', {name: '1'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3'})).toBeVisible();

    await clickWithDelay(settingsButton);
    await clickWithDelay(trashButton);
    await expect(spinner).toBeVisible();
    await expect(spinner).toBeHidden();
    await clickWithDelay(saveButton);
    await expect(noTasksText).toBeVisible();
    await expect(page.getByRole('button', {name: '1'})).toBeHidden();
  });
});
