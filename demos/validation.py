#!/usr/bin/env python


"""
"""


from schematics.base import TypeException
from schematics.models import Model
from schematics.validation import validate_instance, validate_class_fields
from schematics.serialize import (to_python, to_json, whitelist, wholelist,
                                  make_safe_python, make_safe_json)
from schematics.types import MD5Type, StringType
import hashlib


###
### Basic User model
###

class User(Model):
    secret = MD5Type()
    name = StringType(required=True, max_length=50)
    bio = StringType(max_length=100)

    class Options:
        roles = {
            'owner': wholelist(),
            'public': whitelist('name', 'bio'),
        }

    def set_password(self, plaintext):
        hash_string = hashlib.md5(plaintext).hexdigest()
        self.secret = hash_string


###
### Manually create an instance
###

### Create instance with bogus password
u = User()
u.secret = 'whatevz'
u.name = 'test hash'

### Validation will fail because u.secret does not contain an MD5 hash
print 'Attempting validation on:\n\n    %s\n' % (to_json(u))
try:
    validate_instance(u)
    print 'Validation passed\n'
except TypeException, se:
    print 'TypeException caught: %s\n' % (se)
    

### Set the password *correctly* using our `set_password` function
u.set_password('whatevz')
print 'Adjusted invalid data and trying again on:\n\n    %s\n' % (to_json(u))
try:
    validate_instance(u)
    print 'Validation passed\n'
except TypeException, se:
    print 'TypeException caught: %s (This section wont actually run)\n' % (se)


###
### Instantiate an instance with this data
###
 
total_input = {
    'secret': 'e8b5d682452313a6142c10b045a9a135',
    'name': 'J2D2',
    'bio': 'J2D2 loves music',
    'rogue_type': 'MWAHAHA',
}

### Checking for any failure. Exception thrown on first failure.
print 'Attempting validation on:\n\n    %s\n' % (total_input)
try:
    validate_class_fields(User, total_input)
    print 'Validation passed'
except TypeException, se:
    print('TypeException caught: %s' % (se))
print 'After validation:\n\n    %s\n' % (total_input)


### Check all types and collect all failures
exceptions = validate_class_fields(User, total_input, validate_all=True)

if len(exceptions) == 0:
    print 'Validation passed\n'
else:
    print '%s exceptions found\n\n    %s\n' % (len(exceptions),
                                               [str(e) for e in exceptions])


###
### Type Security
###

# Add the rogue type back to `total_input`
total_input['rogue_type'] = 'MWAHAHA'

user_doc = User(**total_input)
print 'Model as Python:\n    %s\n' % (to_python(user_doc))
safe_doc = make_safe_json(User, user_doc, 'owner')
print 'Owner safe doc:\n    %s\n' % (safe_doc)
public_safe_doc = make_safe_json(User, user_doc, 'public')
print 'Public safe doc:\n    %s\n' % (public_safe_doc)

