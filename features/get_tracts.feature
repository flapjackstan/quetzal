Feature: Get census tracts in a county

  Scenario: Elmer wants tracts for Califotnia, LA County
      Given Elmer asks for tracts in LA County 
      When he asks for the county
      Then he gets a table of tracts that are in LA county

  Scenario: Elmer wants tracts for California, Orange County
      Given Elmer asks for tracts in Orange County
      When he asks for the county
      Then he gets a table of tracts that are in Orange county

  Scenario: Elmer wants tracts for Illinois, Cook County
      Given Elmer asks for tracts in Cook County
      When he asks for the county
      Then he gets a table of tracts that are in Cook county
