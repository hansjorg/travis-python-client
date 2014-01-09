"""
Python client for Travis CI (API v2)

For API docs see: https://api.travis-ci.org/docs/
"""

import sys
if sys.version_info[0] >= 3:
    # For Python 3.0 and later
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
else:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen, HTTPError
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

TRAVIS_BASE = 'https://api.travis-ci.org'

def get_travis_token(github_token):
    """
    Get a Travis access token for use with endpoints requiring
    authorization.

    Requires a GitHub OAuth token with same or greater scope than used
    by Travis (public_repo).
    """

    token = None
    response = call('/auth/github',
            data = {'github_token': github_token})

    if 'access_token' in response:
        token = response['access_token']
    
    return token

def restart_build(travis_token, build_id):
    return call('/requests', travis_token, { 'build_id': build_id })

def get_repo(owner_name, repo_name):
    return call('/repos/{}/{}'.format(owner_name, repo_name))

def get_repo_builds(owner_name, repo_name):
    return call('/repos/{}/{}/builds'.format(owner_name, repo_name))

def get_last_build_on_branch(owner_name, repo_name, branch):
    return call('/repos/{}/{}/branches/{}'.format(owner_name, repo_name, branch))

def get_public_key(owner_name, repo_name):
    return call('/repos/{}/{}/key'.format(owner_name, repo_name))

def get_build_by_id(id):
    return call('/builds/{}'.format(id))

def get_log(log_id):
    return call('/logs/{}'.format(log_id))

def get_uptime():
    return call('/uptime/')

def call(url, token = None, data = None):
    json_data = None
    if data:
        json_data = json.dumps(data)

    request = Request(TRAVIS_BASE + url, json_data)

    if token:
        request.add_header('Authorization', 'token ' + token)
    request.add_header('Content-Type',
            'application/json; charset=UTF-8')

    try:    
        response = urlopen(request)
    except HTTPError as error:
        print('Error response from Travis: ' + str(error.code))
        print(error.read())

        return None
 
    response_data = response.read()

    result = None
    if response_data:
        if sys.version_info[0] >= 3:
            # Python 3.0 and later
            encoding = response.headers.get_content_charset()
        else:
            encoding = response.headers.getparam('charset')
        try:
            result = json.loads(response_data.decode(encoding))
        except ValueError:
            print('Unable to deserialize json. Response: "{}"'.\
                    format(response_data))
    return result


# Helper functions

def get_secure_env_var(owner_name, repo_name, var, val):
    """
    Encrypts a VAR=val pair with the given repo's public key for use
    as a secure environment variable in .travis.yml.
    """
    pk_result = get_public_key(owner_name, repo_name)
    pem = pk_result['key']

    key = RSA.importKey(pem)
    cipher = PKCS1_v1_5.new(key)
    
    if sys.version_info[0] >= 3:
        # Python 3.0 and later
        plaintext = (var + '=' + val).encode(encoding='UTF-8')
    else:
        plaintext = var + '=' + val

    ciphertext = cipher.encrypt(plaintext)

    return base64.b64encode(ciphertext)

def trigger_branch_build_restart(travis_token, owner_name, repo_name, branch):
    """
    Trigger restart of the last build on a given branch. This will
    only restart an existing build, not create a new one.
    """
    last_build_id = get_last_build_on_branch(owner_name, repo_name, branch)['branch']['id']
    return restart_build(travis_token, last_build_id)

def trigger_build_restart(travis_token, owner_name, repo_name):
    """
    Trigger restart of the last build. This will only restart an
    existing build, not create a new one.
    """
    last_build_id = get_repo_builds(owner_name, repo_name)[0]['id']
    return restart_build(travis_token, last_build_id)['result']


if __name__ == "__main__":
    owner_name = 'hansjorg'
    repo_name = 'rustci-test-project'
    branch = 'master'
    
    result = get_repo(owner_name, repo_name)
    print(json.dumps(result, sort_keys=True, indent=4))
    
    result = get_last_build_on_branch(owner_name, repo_name, branch)
    print(json.dumps(result, sort_keys=True, indent=4))

    result = get_public_key(owner_name, repo_name)
    print(result['key'])

    print(get_secure_env_var(owner_name, repo_name, 'HIDDEN', 'value'))

