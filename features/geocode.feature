Feature: Address to Lat Longs

  Scenerio: A user wants to reset an api key
  Given a user has a new api key
  When the user inputs a valid string
  Then the program should begin using the new key

  Scenerio: A user wants lat longs and meta data from an address
  Given a user has access to the api service
  When the user inputs an address
  Then the program should provide lat longs and metadata