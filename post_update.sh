#!/bin/sh

# Change the password for a new default one, unique per user
openssl rand -base64 32 | passwd --stdin pi

# TODO :
# * Handle base_addres update (commit 48843d82281e0aa64e2331ccb7d7ecc78e428afd)
