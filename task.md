# Firebase Authentication Migration Tasklist

- [ ] Install `firebase-admin` dependency
- [ ] Initialize Firebase Admin SDK in `app.py`
- [ ] Create `static/firebase-config.js` with project placeholders
- [ ] Refactor `register.html` to use Firebase JS SDK for account creation
- [ ] Refactor `login.html` to use Firebase JS SDK and send ID tokens to backend
- [ ] Update `/login` and `/register` routes in `app.py` to verify Firebase tokens
- [ ] Map Firebase UIDs to the local `User` database model for data persistence
- [ ] Test the full authentication flow (Sign up -> Log in -> Persistence)
- [ ] [Optional] Enable Google Sign-In integration
