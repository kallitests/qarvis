Feature: Envoi de paiement
  En tant qu'utilisateur authentifié de la RWA
  Je veux envoyer de l'argent à un contact
  Afin que la transaction apparaisse dans mon feed

  @smoke @regression
  Scenario: Paiement réussi vers un contact
    Given je suis connecté avec un utilisateur de démo
    When j'envoie 10.00 à un contact avec une note
    Then la transaction apparaît dans mon feed personnel
