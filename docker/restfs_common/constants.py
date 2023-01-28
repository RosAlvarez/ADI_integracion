#!/usr/bin/env python3

'''
    Common definitions of the RestFS: constants
'''

# Common definitions
#
ADMIN = 'admin'
ADMIN_TOKEN = 'admin-token'
USER_TOKEN = 'user-token'
DEFAULT_ENCODING = 'utf-8'
WRITABLE = 'writable_by'
READABLE = 'readable_by'

HTTPS_DEBUG_MODE = False

DEFAULT_AUTH_SERVICE_PORT = 3001
DEFAULT_BLOB_SERVICE_PORT = 3002
DEFAULT_DIR_SERVICE_PORT = 3003

# Keys and values used by DirectoryDB
#
ROOT = 'root'
URL = 'URL'
ROOT_ID = 'root_folder'
PARENT = 'parent'
FILES = 'file_list'
FOLDERS = 'folder_list'
DIR_CHILDS = 'childs'
DIR_PARENT_ID = 'parent'
DIR_IDENTIFIER = 'dir_id'
DIR_IDENTIFIER_SIZE = 20
DEFAULT_DIR_DB = 'directories.json'

# Keys and values used by AuthDB
#
USER = 'user'
TOKEN = 'token'
AGE = 'age'
OWNER = 'owner'
USER_TOKEN_SIZE = 30
USER_TOKEN_AGE_INTERVAL = 5.0
USER_TOKEN_MAX_AGE = 180
HASH_PASS = 'hash-pass'
DEFAULT_AUTH_DB = 'users.json'

# Keys and values used by BlobDB
#
LOCAL_FILENAME = 'local_filename'
BLOB_DB_FILENAME = 'storage_data.json'
