# Tests

## Integration Tests

Integration tests use the same connection information and postgres container as the application but a different database. When pytest executes an integration test it will first drop the test DB, then create a new one, and apply migrations so that each test run has a fresh database instance available.
