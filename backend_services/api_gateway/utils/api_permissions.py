# Permission values of higher value is a superset of any permission with lower value
# i.e Maintainer can do anything that a user can do
PUBLIC_PERMISSION = 0
USER_PERMISSION = 1 # Account owner's permission (e.g a logged in user only has permission of their OWN personal account)
MAINTAINER_PERMISSION = 2

PERMISSIONS_TABLE = {
    "users": {
        "POST": PUBLIC_PERMISSION,
        "GET": USER_PERMISSION,
        "DELETE": USER_PERMISSION,
        "PUT": USER_PERMISSION
        },
    "sessions": {
        "POST": PUBLIC_PERMISSION,
        "GET": USER_PERMISSION,
        "DELETE": USER_PERMISSION,
        },
    "questions": {
        "POST": MAINTAINER_PERMISSION,
        "GET": USER_PERMISSION,
        "DELETE": MAINTAINER_PERMISSION,
        "PUT": MAINTAINER_PERMISSION
        }
}

