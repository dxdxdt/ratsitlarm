# Ratsitlarm
Are you waiting for your personnummer having moved to Sweden? Use this python
module to make the waiting a bit more pleasant. Incorporating AWS Lambda and
SNS, the module sends a notification when there's a hit.

## INSTALL
If you wish to run the module on AWS Lambda, make a periodic event rule that
fires every 30 mins or hour on EventBridge. Create an SNS topic for hit
notification.

The AWS role/user will need following permissions:

- logs:CreateLogGroup
- logs:CreateLogStream
- logs:PutLogEvents
- sns:Publish
- events:DisableRule

Copy the config files and edit them to suit your needs.

```sh
cp doc/config.jsonc doc/query.jsonc src
```

Note that `profile` and `region` are inferred by the SDK if running on Lambda or
EC2. In such case, all the config should specify are `topic` and `rule`. Delete
the `disable-events` mapping altogether if used locally.

### Run it locally
Install the dependencies.

```sh
python3.12 -m pip install --upgrade "pyjson5" "boto3" "requests"
```

At this point, you may start the module in `src` to test or use it as a daemon.
The main script of the module polls every half until there's a hit.

```sh
cd src
python3.12 -m ratsitlarm
```

### Run it on Lambda
Build the zip bundles.

```sh
make
```

Using the generated bundles(`lambda_function.zip` and `lambda_layer.zip`), set
up the AWS lambda function like so

- Runtime: Python 3.12
- Arch: arm64
- The layer applied to the function
- The periodic event rule attached to the function

Upon a query resulted in a hit, the module disables the event rule and publishes
a message to the SNS topic before exiting.
