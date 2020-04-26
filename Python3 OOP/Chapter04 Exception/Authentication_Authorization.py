'''
<Authentication&Authorization System>

Authentication is the process of ensuring a user is really the person they say they are. We'll follow the lead of common web systems today, which use a username and private password combination. Other methods of authentication include voice recognition, fingerprint or retinal scanners, and identification cards.

Authorization, on the other hand, is all about determining whether a given(authenticated) user is permitted to perform a specific action. We'll create a basic permission list system that stores a list of the specific people allowed to perform each action.
'''

import hashlib

class User:
    def __init__(self, username, password):
        '''Create a new user object. The password will be encrypted before storing'''
        self.username = username
        self.password = self._encrypt_pw(password)
        self.is_logged_in = False
        
    def _encrypt_pw(self, password):
        '''Encrypt the password with the username and return the sha digest.'''
        hash_string = (self.username + password)
        hash_string = hash_string.encode('utf8')
        return hashlib.sha256(hash_string).hexdigest()
    
    def check_password(self, password):
        '''Return True if the password is valid for this user, false otherwise'''
        encrypted = self._encrypt_pw(password)
        return encrypted == self.password

class AuthException(Exception):
    def __init__(self, username, user=None):
        super().__init__(username, user)
        self.username = username
        self.user = user

# We don't want to add a user if the username already exists in the dictionary
class UsernameAlreadyExists(AuthException):
    pass

class PasswordTooShort(AuthException):
    pass

# Simply a mapping of username to user objects
class Authenticator:
    def __init__(self):
        '''Construct an authenticator to manage users logging in and out.'''
        self.users = {}
    
    def add_user(self, username, password):
        if username in self.users:
            raise UsernameAlreadyExists(username)
        if len(password) < 6:
            raise PasswordTooShort(username)
        self.users[username] = User(username, password)
        
    def login(self, username, password):
        try:
            user = self.users[username]
        except KeyError: # Dictionary Key Error
            raise InvalidUsername(username)
        
        if not user.check_password(password):
            raise InvalidPassword(username, user)
            
        user.is_logged_in = True
        return True
    
    def is_logged_in(self, username):
        '''this method is not the same as user.is_logged_in'''
        if username in self.users:
            return self.users[username].is_logged_in
        return False
        
class InvalidUsername(AuthException):
    pass

class InvalidPassword(AuthException):
    pass


class Authorizer:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.permissions = {}
        
    def add_permission(self, perm_name):
        '''Create a new permission that users can be added to'''
        try:
            perm_set = self.permissions[perm_name] #perm_set is local variable, but it designates self.permissions[perm_name] after the assignment.
        except KeyError:
            self.permissions[perm_name] = set()
        else: # No Exception means there exists an permission
            raise PermissionError('Permission Exists')
            
    def permit_user(self, perm_name, username):
        '''Grand the given permission to the user'''
        try:
            perm_set = self.permissions[perm_name] #perm_set is local variable, but it designates self.permissions[perm_name] after the assignment.
        except KeyError:
            # The error message will be...
            # During handling of the above exception, another exception occurred.
            raise PermissionError('Permission does not exist')
        else:
            if username not in self.authenticator.users:
                raise InvalidUsername(username)
            perm_set.add(username)
            
    def check_permission(self, perm_name, username):
        '''check whether a user has a specific permission or not'''
        
        # Before check permission, one must be logged in!!!
        if not self.authenticator.is_logged_in(username):
            raise NotLoggedInError(username)
        try:
            perm_set = self.permissions[perm_name]
        except KeyError:
            raise PermissionError('Permission does not exist')
        else:
            if username not in perm_set:
                raise NotPermittedError(username)
            else:
                return True

class PermissionError(Exception):
    pass

class NotLoggedInError(AuthException):
    pass

class NotPermittedError(AuthException):
    pass

authenticator = Authenticator()
authorizor = Authorizer(authenticator)