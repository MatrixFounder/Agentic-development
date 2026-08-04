### UC-01: New User Registration

**Actors:**
- New User
- System
- Email Service (external)

**Preconditions:**
- User is not registered in the system
- User email address is valid and accessible

**Main Scenario:**
1. User opens registration page
2. System displays form with fields: email, password, confirm password
3. User fills form and clicks "Register"
4. System validates email
5. System checks passwords match
6. System checks email is not taken
7. System creates account with status "unconfirmed"
8. System sends email with confirmation code
9. System displays page "Check your email"

**Alternative Scenarios:**

**A1: Invalid email (at step 4)**
1. System displays error: "Invalid email address"
2. User corrects email
3. Return to step 3 of main scenario

**A2: Passwords do not match (at step 5)**
1. System displays error: "Passwords do not match"
2. User corrects passwords
3. Return to step 3 of main scenario

**A3: Email already taken (at step 6)**
1. System displays error: "User with this email already exists"
2. System suggests login or password recovery
3. End of use case

**Postconditions:**
- Account created with status "unconfirmed"
- Confirmation email sent
- User sees page with instruction to check email

**Acceptance Criteria:**
- Registration form contains the fields email, password and confirm password
- Email validated according to RFC 5322 standard
- Password must be at least 8 characters
- System does not allow registering duplicate email
- Confirmation email sent within 1 minute
- Confirmation code valid for 24 hours
- Each error in A1-A3 names the field it rejected and the value it expected
