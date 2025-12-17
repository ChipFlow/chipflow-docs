# chipflow.auth

ChipFlow authentication helper module.

Handles authentication for ChipFlow API with multiple fallback methods:
1. Environment variable CHIPFLOW_API_KEY
2. GitHub CLI token authentication (if gh is available)
3. OAuth 2.0 Device Flow

## Exceptions

| [`AuthenticationError`](#chipflow.auth.AuthenticationError)   | Exception raised when authentication fails.   |
|---------------------------------------------------------------|-----------------------------------------------|

## Functions

| [`get_credentials_file`](#chipflow.auth.get_credentials_file)()                                              | Get path to credentials file.                       |
|--------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| [`save_api_key`](#chipflow.auth.save_api_key)(api_key)                                                       | Save API key to credentials file.                   |
| [`load_saved_api_key`](#chipflow.auth.load_saved_api_key)()                                                  | Load API key from credentials file if it exists.    |
| [`is_gh_authenticated`](#chipflow.auth.is_gh_authenticated)()                                                | Check if GitHub CLI is installed and authenticated. |
| [`get_gh_token`](#chipflow.auth.get_gh_token)()                                                              | Get GitHub token from gh CLI.                       |
| [`authenticate_with_github_token`](#chipflow.auth.authenticate_with_github_token)(api_origin[, interactive]) | Authenticate using GitHub CLI token.                |
| [`authenticate_with_device_flow`](#chipflow.auth.authenticate_with_device_flow)(api_origin[, interactive])   | Authenticate using OAuth 2.0 Device Flow.           |
| [`get_api_key`](#chipflow.auth.get_api_key)([api_origin, interactive, force_login])                          | Get API key using the following priority:           |
| [`logout`](#chipflow.auth.logout)()                                                                          | Remove saved credentials.                           |

## Module Contents

### *exception* chipflow.auth.AuthenticationError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Exception raised when authentication fails.

### chipflow.auth.get_credentials_file()

Get path to credentials file.

### chipflow.auth.save_api_key(api_key)

Save API key to credentials file.

* **Parameters:**
  **api_key** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))

### chipflow.auth.load_saved_api_key()

Load API key from credentials file if it exists.

### chipflow.auth.is_gh_authenticated()

Check if GitHub CLI is installed and authenticated.

### chipflow.auth.get_gh_token()

Get GitHub token from gh CLI.

### chipflow.auth.authenticate_with_github_token(api_origin, interactive=True)

Authenticate using GitHub CLI token.

Args:
: api_origin: ChipFlow API origin URL
  interactive: Whether to show interactive messages

Returns:
: API key on success, None on failure

* **Parameters:**
  * **api_origin** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **interactive** ([*bool*](https://docs.python.org/3/library/functions.html#bool))

### chipflow.auth.authenticate_with_device_flow(api_origin, interactive=True)

Authenticate using OAuth 2.0 Device Flow.

Args:
: api_origin: ChipFlow API origin URL
  interactive: Whether to show interactive messages

Returns:
: API key on success, raises AuthenticationError on failure

* **Parameters:**
  * **api_origin** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **interactive** ([*bool*](https://docs.python.org/3/library/functions.html#bool))

### chipflow.auth.get_api_key(api_origin=None, interactive=True, force_login=False)

Get API key using the following priority:
1. CHIPFLOW_API_KEY environment variable
2. Saved credentials file (unless force_login is True)
3. GitHub CLI token authentication
4. Device flow authentication

Args:
: api_origin: ChipFlow API origin URL (defaults to CHIPFLOW_API_ORIGIN env var or production)
  interactive: Whether to show interactive messages and prompts
  force_login: Force re-authentication even if credentials exist

Returns:
: API key string

Raises:
: AuthenticationError: If all authentication methods fail

* **Parameters:**
  * **api_origin** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*)
  * **interactive** ([*bool*](https://docs.python.org/3/library/functions.html#bool))
  * **force_login** ([*bool*](https://docs.python.org/3/library/functions.html#bool))

### chipflow.auth.logout()

Remove saved credentials.
