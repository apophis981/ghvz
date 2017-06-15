import setup
from selenium.webdriver.common.by import By

driver = setup.MakeDriver(user="minny", page="/createGame", populate=False)

try:
  driver.Click([[By.ID, 'createGame']])

  driver.SendKeys(
      [[By.ID, 'idInput'], [By.TAG_NAME, 'input']],
      driver.GetGameId())

  driver.SendKeys(
      [[By.ID, 'nameInput'], [By.TAG_NAME, 'input']],
      'My Game')

  driver.SendKeys(
      [[By.ID, 'stunTimerInput'], [By.TAG_NAME, 'input']],
      '60')
  
  driver.Click([[By.ID, 'gameForm'], [By.ID, 'done']])
  
  driver.WaitForGameLoaded()

  if driver.is_mobile:
    driver.Click([[By.TAG_NAME, 'ghvz-mobile-main-page'], [By.NAME, 'drawerButton']])

  driver.Click([[By.NAME, 'drawerAdmin Dashboard']])

  if driver.is_mobile:
    driver.FindElement([[By.TAG_NAME, 'ghvz-notifications']])
  else:
    driver.ExpectContains(
        [[By.TAG_NAME, 'ghvz-game-details'], [By.ID, 'name']],
        'My Game')

    driver.ExpectContains(
        [[By.TAG_NAME, 'ghvz-game-details'], [By.ID, 'stunTimer']],
        '60')

  driver.Quit()

finally:
  # driver.Quit()
  pass
