# Contact Ap

This is a submission fo MoneyLion security engineer take home assesment. The project is to build a simple contact information collection app built with Vanilla Frontend and FastAPI backend. A public deployment is available at https://ml-contact-yam.oscore.my

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Pre-requisite

The app reads sensitive information such as DB credentials and encryption keys from AWS Secrets Manager and AWS KMS. Make sure you have the necessary resources and AWS credentials that the container can access the resources

### Secrets Manager

Secrets Manager stores 2 secrets: Database credentials and JWT key. The keys of the secrets and keys can be configured in the config.py file in the v1 folder. The configuration is as follows:
**DB Config**
Key: contact_app_server/rds_contact_db
{
"username": secret["username"],
"password": secret["password"],
"host": secret["host"],
"port": secret["port"],
"db": secret["dbname"],
}
**JWT Key**
Key: contact_app_server/jwt_key
(
jwt_key: secret[jwt_key]
}
Make sure you have secrets in the specified format.

### KMS

Whereas KMS is being used to manage the KEK in the encryption of SSN data.

## Installation

1. Clone this repository:
   ````bash
   git clone https://github.com/yamkeli/ml-security-engineer-test.git```
   ````
2. Deploy a Docker Swarm stack
   ````bash
   docker stack deploy -c docker-compose.yaml contact_app```
   ````

## Usage

Once the stack is deployed, navigate to http://localhost on your browser to use the app.

## Documentation

Detailed documentation is available at the docs folder.
