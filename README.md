# Cmput404W2021

## Environment Variables
There are a number of environment variables that can be, and should be, configured when running an instance of this project. On Heroku specifically, these can be found in Settings -> Config Vars
* DATABASE_URL: The url to a functioning PostgreSQL database. Can be set to sqlite:///db.sqlite3 for local testing.
* DEV_DEBUG (True|False): Should be False in nearly all cases except for debugging purposes. This will enable advanced error reporting.
* HOST_NAME: Should be the hostname for your heroku instance
* NEW_ACCOUNTS_AUTO_APPROVED (True|False): When True, users will be able to sign up and use your site immediately. When False, users will need to be approved by an administrator who will set the "is_active" flag on their accounts.
* PROJECT_PATH: Always set this to mysite
* SCHEME: Should be set to https, but could be set to http if necessary, particularly for local testing.
* SECRET_KEY: The Django secret key for your site. Should be secret.

## Heroku Deployment
[https://socialdistributionproject.herokuapp.com/](https://socialdistributionproject.herokuapp.com/)

## Test Credentials

### Normal User
* Username: TA
* Password: TestAccount1234

### Admin
* Username: admin
* Password: 1234

### Server (Elevated API Access)
* Username: server
* Password: connect1234

## Giving a Node Remote Access
All a foreign node needs to access the sensitive parts of our API with elevated permissions is a user account with appropriate permissions. The steps to create this account are as follows:
1. Login to the admin panel with admin credentials: [https://socialdistributionproject.herokuapp.com/admin/](https://socialdistributionproject.herokuapp.com/admin/)
2. Click on "Users"
3. Click on "Add User +"
4. Provide a suitable username and password. These will be shared with the person(s) running the node.
5. Click on "Save"
6. Wait to be redirected to a page that allows you to edit this user.
7. Check the "Is server" box.
8. Click on "Save"
9. Share the credentials with whoever needs them, and they will have elevated access to the API.

## Adding a Foreign Node for Friendships + Post Retrieval
1. Login to the admin panel with admin credentials: [https://socialdistributionproject.herokuapp.com/admin/](https://socialdistributionproject.herokuapp.com/admin/)
2. Click on "Foreign Servers"
3. Click on "Add Foreign Server +"
4. Provide a name for identification purposes
5. Provide a URL to an endpoint that will retrieve that server's authors
6. Provide the JSON key that will access that list of authors once returned (can be blank)
7. Provide a URL to an endpoint that will retrieve that server's posts
8. Provide the JSON key that will access that list of posts once returned (can be blank)
9. Provide the username and password given to you by the operators of this foreign node
10. Click on "Save"
