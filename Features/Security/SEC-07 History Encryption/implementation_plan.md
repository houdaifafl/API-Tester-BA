1. Feature Summary
   Implement database encryption at rest and request/response masking for collaborative history entries (SEC-07).
   - **Backend**:
     - Integrate symmetric encryption using `cryptography.fernet` to encrypt the `headers`, `params`, `auth`, `body`, and `data` columns of history entries before they are written to the database.
     - Implement automatic decryption when reading those entries back in python model attributes.
     - Mask sensitive fields (such as `Authorization`, `x-api-key`, etc.) in headers and auth configurations returned via `get_history_entries` and `create_history_entry` endpoints.
     - Omit storing the response body (`data`) for requests that utilize credentials or when the response payload itself contains secrets, replacing it with a secure placeholder message.
     - Configure the symmetric encryption key `HISTORY_ENCRYPTION_KEY` in environment variables.

2. Design Review
   2.1 Architecture Rationale
     - Symmetric encryption via `cryptography.fernet` ensures database values are completely unreadable in their raw form at rest.
     - Using python property wrappers (`@property` / getter / setter) on the `History` database model encapsulates encryption/decryption transparently, preventing codebase churn and keeping other database queries or service classes clean.
     - Masking sensitive headers (e.g. replacing token values with `****`) in API responses prevents exposure in collaborative workspaces and in transit.
     - Omitting response payloads for authenticated requests prevents logging of API access keys or user session tokens returned by external services.

   2.2 State Ownership
     - Encryption is handled transparently inside the `History` model object on instantiation and serialisation.
     - Configuration keys are read from environment settings.

   2.3 Service Ownership
     - We will create an encryption utility service `backend/services/encryption_service.py` to handle encryption, decryption, and masking logic.

   2.4 Testing Strategy
     - Write integration tests in `backend/tests/test_history_encryption.py` to assert:
       - Values written to the database column are actually encrypted (asserting that a raw DB query yields Fernet tokens instead of plaintext JSON).
       - Deserialized model instances return the correct decrypted dictionary values.
       - API responses mask `Authorization` and other sensitive header keys.
       - Responses for authenticated requests omit response data, replacing it with the security policy placeholder.

   2.5 Scalability Concerns
     - Fernet encryption/decryption uses highly optimized C-bindings via `cryptography`, which introduces negligible overhead for typical API payloads.

3. Files to Create
   - **[NEW] [encryption_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/encryption_service.py)** (Est: ~70 lines)
     - Key loading, Fernet cipher initialization, encryption, decryption, and header/auth masking helper methods.
   - **[NEW] [test_history_encryption.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_history_encryption.py)** (Est: ~60 lines)
     - Test cases verifying rest-encryption correctness and API response masking.

4. Files to Modify
   - **[MODIFY] [history_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/history_model.py)**
     - Redefine `params`, `headers`, `body`, `auth`, and `data` columns to map to underlying text fields, and wrap them in encryption/decryption getter/setter properties.
   - **[MODIFY] [history_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/history_service.py)**
     - Apply header and auth masking logic on serialization.
     - Check if request is authenticated or contains secrets, and apply the response data placeholder if needed.
   - **[MODIFY] [.env](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env) & [.env.example](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env.example)**
     - Define `HISTORY_ENCRYPTION_KEY` configuration variable.

5. API Contract Changes
   - The fields returned by `GET /api/workspaces/<id>/history` will contain masked values for sensitive headers/auth config. E.g.:
     ```json
     {
       "headers": {
         "Authorization": "Bearer ****",
         "Accept": "application/json"
       }
     }
     ```

6. OpenAPI Spec Additions
   - None (endpoint responses retain the same schema, only string contents are masked).

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_history_encryption.py`
     - Run full test suite to check backward compatibility.
   - **Manual Verification**:
     - Create an API request with an `Authorization: Bearer my-secret-token` header. Execute it.
     - View the entry in workspace history, verify it loads with the header masked as `Bearer ****`.
