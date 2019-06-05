Cabot HTTP Check Plugin
=====

This is a plugin for running HTTP checks against a server in Cabot.

## Installation
cabot_check_http should come installed with cabot as default however if you need to install it manually, append

cabot_check_http

to the variable

CABOT_PLUGINS_ENABLED

in your

conf/production.env


## Configuration

cabot_check_http accepts an optional environment variable `CABOT_CHECK_HTTP_CA_BUNDLE` to specify the path of a 
CA bundle file to use instead of the default one provided by the [Certifi](https://pypi.org/project/certifi/) module.