import setup
import time
from selenium.webdriver.common.by import By

try:

  # Sign in as an admin
  driver = setup.MakeDriver(user="zella")

  ######################  Testing Admin Guns Page  ######################

  # If the user has a notification, close it
  try: 
    driver.Click([[By.NAME, 'close-notification']])
  finally:
    pass

  # Admin adds gun
  driver.Click([[By.TAG_NAME, 'ghvz-unseen-notifications'], [By.CLASS_NAME, 'close']])

  driver.Click([[By.NAME, 'drawerAdmin Guns']])
  driver.Click([[By.ID, 'add']])
  driver.SendKeys(
        [[By.ID, 'form-section-create-gun'], [By.TAG_NAME, 'input']],
        '3.14')
 
  driver.Click([[By.ID, 'gunForm'],[By.ID, 'done']])

  # View added gun
  driver.ExpectContains([[By.NAME, 'gun-row-3.14']], "3.14")

  # Assign player a gun
  driver.Click([[By.NAME, 'gun-row-3.14'], [By.CLASS_NAME, 'pencil']])
  driver.SendKeys(
        [[By.NAME, 'gun-row-3.14'], [By.TAG_NAME, 'input']],
        'JackSlayerTheBeanSlasher')
  driver.Click([[By.NAME, 'gun-row-3.14'], [By.ID, 'setButton']])

  # Show that player shows up as having the gun
  driver.ExpectContains([[By.NAME, 'gun-row-3.14'], [By.CLASS_NAME, 'player-label']], "JackSlayerTheBeanSlasher")

  #Add another gun, assign to another player
  driver.Click([[By.ID, 'add']])
  driver.SendKeys(
        [[By.ID, 'form-section-create-gun'], [By.TAG_NAME, 'input']],
        'pancake')
  driver.Click([[By.ID, 'gunForm'],[By.ID, 'done']])
  driver.Click([[By.NAME, 'gun-row-pancake'], [By.CLASS_NAME, 'pencil']])
  driver.Click([[By.NAME, 'gun-row-pancake'], [By.TAG_NAME, 'input']])
  driver.Click([[By.NAME, 'gun-row-pancake'], [By.NAME, '103: MoldaviTheMoldavish']])
  driver.Click([[By.NAME, 'gun-row-pancake'], [By.ID, 'setButton']])

  # Search by label
  driver.Click([[By.NAME, 'header-Label'], [By.NAME, 'icon-search']])
  driver.SendKeys(
        [[By.NAME, 'header-Label'], [By.TAG_NAME, 'input']],
        'pan')
  # TODO(olivia): devise a way to check that these rows are visible or not
  # driver.ExpectContains([[By.ID, 'table']], "Moldavi")
  # driver.ExpectContains([[By.ID, 'table']], "Jack", False)
  driver.Backspace([[By.NAME, 'header-Label'], [By.TAG_NAME, 'input']], 3)

  # Search by player
  driver.Click([[By.NAME, 'header-Player'], [By.NAME, 'icon-search']])
  driver.SendKeys(
        [[By.NAME, 'header-Player'], [By.TAG_NAME, 'input']],
        'Jack')
  # TODO(olivia): devise a way to check that these rows are visible or not
  # driver.ExpectContains([[By.ID, 'table']], "Jack")
  # driver.ExpectContains([[By.ID, 'table']], "Moldavi", False)
  driver.Backspace([[By.NAME, 'header-Player'], [By.TAG_NAME, 'input']], 4)

  # Change the weapon ID, and show that it shows up
  driver.Click([[By.NAME, 'gun-row-3.14'], [By.ID, 'menu']])
  driver.Click([[By.NAME, 'gun-row-3.14'], [By.NAME, 'menu-item-Edit']])
  driver.SendKeys(
        [[By.ID, 'form-section-create-gun'], [By.TAG_NAME, 'input']],
        '42')
  driver.Click([[By.ID, 'gunForm'], [By.ID, 'done']])
  driver.ExpectContains([[By.NAME, 'gun-row-42']], "42")
   
  # TODO - when implemented, have a player see that they've been assigned a gun
   


  ####################  Testing Admin Players Page  ######################


  # Admin - set got equipment for Jack
  driver.Click([[By.NAME, 'drawerAdmin Players']])
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'menu']]) # This is Jack (non-admin, human)
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.NAME, 'menu-item-Set Got Equipment']]) # Doesn't update like it's supposed to - remote server
  driver.ExpectContains([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'gotEquipment']], "Yes") #Crashes here remote server

  # Check Jack's profile, make sure the change showed up
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'name']])
  driver.ExpectContains([[By.NAME, 'got-equipment']], "Yes")

  # If you set the equipment of someone who already has it, nothing should happen
  driver.Click([[By.NAME, 'drawerAdmin Players']])
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'menu']]) # This is Jack (non-admin, human)
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.NAME, 'menu-item-Set Got Equipment']])
  driver.ExpectContains([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'gotEquipment']], "Yes")

  # TODO(verdagon): have the webdrivers wait until things are visible / not visible.
  # This sleep is to wait for the menu to become not visible.
  time.sleep(1)

  # Unset Jack's equipment
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'menu']])
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.NAME, 'menu-item-Unset Got Equipment']])
  driver.ExpectContains([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'gotEquipment']], "No")

  # Check Jack's profile, make sure the change showed up
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'name']])
  driver.ExpectContains([[By.NAME, 'got-equipment']], "No")

  # Go back to the Admin Guns page
  driver.Click([[By.NAME, 'drawerAdmin Players']])

  # Search by number
  driver.Click([[By.NAME, 'header-#'], [By.NAME, 'icon-search']])
  driver.SendKeys(
        [[By.NAME, 'header-#'], [By.TAG_NAME, 'input']],
        '3')
  # TODO(olivia): devise a way to check that these rows are visible or not
  # driver.ExpectContains([[By.NAME, 'player-table']], "Jack") # Jack should show up
  # driver.ExpectContains([[By.NAME, 'player-table']], "Deckerd", False) # Deckerd shouldn't show up
  driver.Backspace([[By.NAME, 'header-#'], [By.TAG_NAME, 'input']])

  # # Search by name
  driver.Click([[By.NAME, 'playerTablePage'], [By.NAME, 'header-Name'], [By.NAME, 'icon-search']])
  driver.SendKeys(
        [[By.NAME, 'playerTablePage'], [By.NAME, 'header-Name'], [By.TAG_NAME, 'input']],
        'Deckerd')
  # TODO(olivia): devise a way to check that these rows are visible or not
  # driver.ExpectContains([[By.NAME, 'player-table']], "Deckerd") # Deckerd should show up
  # driver.ExpectContains([[By.NAME, 'player-table']], "Jack", False) # Jack shouldn't show up
  driver.Backspace([[By.NAME, 'playerTablePage'], [By.NAME, 'header-Name'], [By.TAG_NAME, 'input']], 7)

  # TODO - search by equipment once this works

  # Add a note
  driver.Click([[By.NAME, 'drawerAdmin Players']])
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.ID, 'menu']])
  driver.Click([[By.NAME, 'player-row-JackSlayerTheBeanSlasher'], [By.NAME, 'menu-item-Set Notes']])

  driver.SendKeys([[By.ID, 'notesInput'], [By.TAG_NAME, 'input']], 'zapfinkle skaddleblaster')
  driver.Click([[By.ID, 'notesForm'], [By.ID, 'done']])

  # Search by notes
  driver.Click([[By.NAME, 'header-Notes'], [By.NAME, 'icon-search']])
  driver.SendKeys(
        [[By.NAME, 'header-Notes'], [By.TAG_NAME, 'input']],
        'zap')
  # TODO(olivia): devise a way to check that these rows are visible or not
  # driver.ExpectContains([[By.NAME, 'player-table']], "Jack") # Jack should show up
  # driver.ExpectContains([[By.NAME, 'player-table']], "Deckerd", False) # Deckerd shouldn't show up

  driver.Quit()

finally:
  pass
