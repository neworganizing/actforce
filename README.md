# ActionKit to Salesforce Connector

Important Environment Variables


### ActionKit Database Information

AK_DBNAME - ActionKit Database Name
AK_DBUSER - ActionKit Database User
AK_DBPASS - ActionKit Database Password
AK_DBSERVER - ActionKit Database Host (default to client-db.actionkit.com)

### Salesforce Information
SF_OAUTH_CLIENT_ID = Salesforce OAuth 2.0 Client ID
SF_OAUTH_CLIENT_SECRET = Salesforce OAuth 2.0 Client Secret
SF_OAUTH_REDIRECT_URI - Salesforce OAuth 2.0 Redirect URI (https://app.yourdomain.com/sfauth/)

### S3/Static File Storage Information

AWS_STORAGE_BUCKET - S3 Bucket static files
AWS_ACCESS_KEY_ID - Public ID with access to static file S3 bucket
AWS_SECRET_ACCESS_KEY - Private ID with access to static file S3 bucket

### SMTP/EMail Info

SMTP_HOST - Hostname of SMTP Server
SMTP_PORT - Port of SMTP Server (default to 22)
SMTP_USETLS - Use TLS (defaults to true)
SMTP_USER - Username of SMTP user
SMTP_PASSWORD - Password of SMTP user