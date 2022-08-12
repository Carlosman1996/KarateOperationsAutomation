@ignore
Feature:


Background:
  * url urls.wscUrl


Scenario:
  * def req = __arg
  * def authHeader = call read('classpath:karate-auth.js') req.auth
  * def headers = karate.merge(req.headers || {}, authHeader || {})

  Given path
  # And params params
  And headers headers
  When method GET

  * def expectedStatusCode = req.statusCodeMatches || responseStatus
  * match responseStatus == expectedStatusCode

  # Validate schema:
  * def responseValidator = req.responseMatches? req.responseMatches : {}
  * match response contains responseValidator
