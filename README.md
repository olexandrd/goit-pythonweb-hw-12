# goit-pythonweb-hw-12

![Coverage](https://img.shields.io/badge/CodeCoverage-81%25-brightgreen)

## Demo

Live demo: [https://fastapi.olexandr.cx.ua/docs](https://fastapi.olexandr.cx.ua/docs)
On demo MailCatcher is used to catch emails.
You can see them on [https://fastapi.olexandr.cx.ua/email-messages](https://fastapi.olexandr.cx.ua/email-messages)

Documentation is updated automatically using github-actions: [https://olexandrd.github.io/goit-pythonweb-hw-12/](https://olexandrd.github.io/goit-pythonweb-hw-12/)

## Setup

1. Create a `.env` file in the root of the project with the following content:

```env
POSTGRES_DB=app
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_PORT=5432
POSTGRES_HOST=postgres

REDIS_HOST=redis
REDIS_PORT=6379

DB_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
JWT_SECRET=
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=465
MAIL_SERVER=smtp.mailgun.org

CLD_NAME=
CLD_API_KEY=
CLD_API_SECRET=

```

And add your own values to the variables:

* `POSTGRES_USER` - the username for the PostgreSQL database
* `POSTGRES_PASSWORD` - the password for the PostgreSQL database
* `JWT_SECRET` - the secret key for the JWT token
* `MAIL_USERNAME` - the username for the email server
* `MAIL_PASSWORD` - the password for the email server
* `MAIL_FROM` - the email address from which the emails will be sent
* `MAIL_SERVER` - the SMTP server for the email server
* `CLD_NAME` - the name of the Cloudinary account
* `CLD_API_KEY` - the API key for the Cloudinary account
* `CLD_API_SECRET` - the API secret for the Cloudinary account
