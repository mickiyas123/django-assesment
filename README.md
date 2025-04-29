# Django-Assesment

Create a Django API with django rest framework

- [ ]  users with custom roles - admin, coach, agent, football player
- [ ]  sign up and social sign up (google, facebook)
- [ ]  login and social login
- [ ]  password reset

# Django Authentication API

A professional Django REST API with JWT authentication, password reset functionality, and Google OAuth integration.

## API Endpoints

### Authentication

- `POST /api/users/register/` - Register a new user
- `POST /api/users/login/` - Get JWT tokens for authentication
- `POST /api/users/login/refresh/` - Refresh JWT token
- `POST /api/users/logout/` - Logout (blacklist token)
- `POST /api/users/google/` - Login with Google

### User Management

- `GET /api/users/me/` - Get current user profile
- `PUT /api/users/me/` - Update user profile

### Password Reset

- `POST /api/users/password-reset/` - Request password reset email
- `POST /api/users/password-reset-confirm/` - Confirm password reset with new password
- `GET /reset-password/<uid>/<token>/` - Password reset confirmation page

### Social Authentication

- `GET /login/google/` - Google login page
- `GET /accounts/google/login/` - Initiate Google OAuth flow
- `GET /accounts/google/login/callback/` - Google OAuth callback URL

### Admin

- `GET /admin/` - Django admin interface
