import { expect } from '@playwright/test';
import { buddyTest } from './procrastination-fixture';

buddyTest.describe('Procrastination Buddy UI', () => {
  buddyTest.beforeEach(async ({ on, page }) => {
    await page.goto('http://localhost:8501');
    await on(page).main.do.openSettings();
    await expect(on(page).modal.settings()).toBeVisible();
    await expect(on(page).modal.settings()).toHaveText(/Tweak Buddy/);
    await on(page).modal.settings.do.chooseLanguage('English');
    await on(page).modal.settings.do.chooseTimezone('Europe/Berlin');
    await on(page).modal.settings.do.chooseModel('llama3:8b');
    await on(page).modal.settings.do.chooseTasksPerPage('5');
    await on(page).modal.settings.do.uncheckFavorites();
    await on(page).modal.settings.do.trashTasks();
    await expect(on(page).main.locators.spinners.updatingTasks).toBeVisible();
    await expect(on(page).main.locators.spinners.updatingTasks).toBeHidden();
    await on(page).modal.settings.do.save();
    await expect(on(page).main.locators.texts.noTasks).toBeVisible();
  });

  buddyTest('should have the correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/Procrastination Buddy ⏰🤷/);
  });

  buddyTest('should display all key UI elements', async ({ on, page }) => {
    await expect(on(page).main.locators.heading).toBeVisible();
    await expect(on(page).main.locators.buttons.generate).toBeVisible();
    await expect(on(page).main.locators.buttons.info).toBeVisible();
    await expect(on(page).main.locators.buttons.settings).toBeVisible();
    await expect(on(page).main.locators.switches.filterLikes).toBeVisible();
  });

  buddyTest('should display the info modal', async ({ on, page }) => {
    await on(page).main.do.openInfo();
    await expect(on(page).modal.info()).toBeVisible();
    await expect(on(page).modal.info()).toHaveText(/Explanation Buddy/);
    await on(page).modal.info.do.close();
    await expect(on(page).modal.info()).toBeHidden();
  });

  buddyTest('should display settings modal', async ({ on, page }) => {
    await on(page).main.do.openSettings();
    await expect(on(page).modal.settings()).toBeVisible();
    await expect(on(page).modal.settings()).toHaveText(/Tweak Buddy/);
    await on(page).modal.settings.do.close();
    await expect(on(page).modal.settings()).toBeHidden();
  });

  buddyTest('should change language', async ({ on, page }) => {
    await on(page).main.do.openSettings();
    await on(page).modal.settings.do.chooseLanguage('Deutsch');
    await on(page).modal.settings.do.save();
    await expect(on(page).modal.settings()).toBeHidden();
    await expect(page.getByText(/Dein Komplize/)).toBeVisible();
  });

  buddyTest('should change timezone and update task timestamp', async ({ on, page }) => {
      await on(page).main.do.generateTask();
      const task = on(page).main.locators.tasks.nth(0);
      const taskText1 = await task.innerText();
      await on(page).main.do.openSettings();
      await on(page).modal.settings.do.chooseTimezone('America/New_York');
      await on(page).modal.settings.do.save();
      await expect(task).not.toHaveText(taskText1);
    }
  );

  buddyTest('should generate a task', async ({ on, page }) => {
    await expect(on(page).main.locators.texts.noTasks).toBeVisible();
    await on(page).main.do.generateTask();
    await expect(on(page).main.locators.tasks).toHaveCount(1);
  });

  buddyTest('should filter liked tasks', async ({ on, page }) => {
    for (let i = 0; i < 2; i++) {
      await on(page).main.do.generateTask();
    }

    await on(page).main.do.filterTasks({ onlyLiked: false });
    await expect(on(page).main.locators.tasks).toHaveCount(2);
    await on(page).main.do.likeTask(0);
    await on(page).main.do.filterTasks({ onlyLiked: true });
    await expect(on(page).main.locators.tasks).toHaveCount(1);
  });

  buddyTest('should not delete liked tasks if preference is set', async ({ on, page }) => {
      await on(page).main.do.generateTask();
      await expect(on(page).main.locators.tasks).toHaveCount(1);
      await on(page).main.do.likeTask(0);

      await on(page).main.do.openSettings();
      await expect(on(page).main.locators.spinners.updatingTasks).toBeHidden();
      await on(page).modal.settings.do.trashTasks();
      await on(page).modal.settings.do.save();
      await expect(on(page).main.locators.tasks).toHaveCount(1);

      await on(page).main.do.likeTask(0);
      await on(page).main.do.openSettings();
      await on(page).modal.settings.do.uncheckFavorites();
      await on(page).modal.settings.do.trashTasks();
      await expect(on(page).main.locators.spinners.updatingTasks).toBeHidden();
      await on(page).modal.settings.do.save();
      await expect(on(page).main.locators.tasks).toHaveCount(0);
    }
  );

  buddyTest('should show pagination for more than 5 tasks', async ({ on, page }) => {
      await on(page).main.do.openSettings();
      await on(page).modal.settings.do.chooseTasksPerPage('5');
      await on(page).modal.settings.do.save();

      for (let i = 0; i < 9; i++) {
        await on(page).main.do.generateTask();
      }

      await expect(page.getByRole('button', { name: '2' })).toBeVisible();
      await page.getByRole('button', { name: '2' }).click();
      await expect(on(page).main.locators.tasks).toHaveCount(4);

      await page.getByRole('button', { name: '1' }).click();
      await expect(on(page).main.locators.tasks).toHaveCount(5);

      await on(page).main.do.openSettings();
      await on(page).modal.settings.do.chooseTasksPerPage('3');
      await on(page).modal.settings.do.save();

      await expect(page.getByRole('button', { name: '3' })).toBeVisible();

      await on(page).main.do.openSettings();
      await on(page).modal.settings.do.trashTasks();
      await expect(on(page).main.locators.spinners.updatingTasks).toBeHidden();
      await on(page).modal.settings.do.save();

      await expect(on(page).main.locators.texts.noTasks).toBeVisible();
    }
  );
});
